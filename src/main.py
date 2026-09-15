"""
Pico Smart Doorbell — MicroPython firmware
==========================================
Board  : Raspberry Pi Pico W (RP2040 + CYW43439)
Author : DevNode Technologies / SRECONICS

Wiring
------
  PIR OUT  → GP15  (PULL_DOWN, interrupt-driven)
  Piezo +  → GP16  (PWM output)
  Piezo −  → GND
  Power    → VSYS via TP4056 LiPo charger

How it works
------------
1. Setup hardware watchdog (8 s) + PIR rising-edge interrupt
2. Main loop feeds WDT every 500 ms — no busy work
3. On PIR trigger:
     a. Play 4-note chime on piezo (GP16 PWM)
     b. Connect to WiFi (15 s timeout)
     c. POST push notification to ntfy.sh
     d. Append event to flash log
4. WDT resets board if anything hangs for >8 s

Copy config.py (from config.example.py) to the root of
the Pico before uploading this file.
"""

import machine
import utime
import network
import urequests
import json

# ── load credentials ───────────────────────────────────────────────────────
try:
    from config import WIFI_SSID, WIFI_PASS, NTFY_TOPIC
except ImportError:
    raise RuntimeError(
        "config.py not found. Copy config.example.py → config.py "
        "and fill in your credentials."
    )

# ── pin assignments ────────────────────────────────────────────────────────
PIR_PIN    = 15   # HC-SR501 signal out
BUZZER_PIN = 16   # piezo buzzer positive leg

# ── persistence ────────────────────────────────────────────────────────────
LOG_FILE = "doorbell_log.json"

# ── notes for the chime (C6 E6 G6 C7) ────────────────────────────────────
CHIME_NOTES = [1047, 1319, 1568, 2093]   # Hz
NOTE_MS     = 120

# ── hardware watchdog ──────────────────────────────────────────────────────
# Resets the board if it hangs for more than 8 seconds
wdt = machine.WDT(timeout=8_000)


# ── helpers ───────────────────────────────────────────────────────────────
def chime():
    """Play a 4-note ascending doorbell chime on the piezo."""
    buzzer = machine.PWM(machine.Pin(BUZZER_PIN))
    for freq in CHIME_NOTES:
        buzzer.freq(freq)
        buzzer.duty_u16(30_000)
        utime.sleep_ms(NOTE_MS)
    buzzer.duty_u16(0)
    buzzer.deinit()


def connect_wifi(timeout_s: int = 15) -> bool:
    """Connect to WiFi. Returns True on success."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected():
        return True
    wlan.connect(WIFI_SSID, WIFI_PASS)
    deadline = utime.time() + timeout_s
    while not wlan.isconnected():
        if utime.time() >= deadline:
            return False
        utime.sleep_ms(500)
    return True


def send_ntfy(ts: str) -> bool:
    """POST a push notification to ntfy.sh. Returns True on success."""
    url     = f"https://ntfy.sh/{NTFY_TOPIC}"
    headers = {
        "Title"   : "Doorbell \U0001f514",
        "Priority": "high",
        "Tags"    : "bell",
    }
    body = f"Someone at the door \u2014 {ts}"
    try:
        r = urequests.post(url, data=body, headers=headers, timeout=8)
        r.close()
        return True
    except Exception as exc:
        print("[ntfy] send failed:", exc)
        return False


def log_event(ts: str, alerted: bool):
    """Append event record to flash log file."""
    record = json.dumps({"ts": ts, "alerted": alerted})
    try:
        with open(LOG_FILE, "a") as f:
            f.write(record + "\n")
    except OSError:
        # Flash full or write-protected — skip silently
        pass


# ── PIR interrupt handler ─────────────────────────────────────────────────
def handle_trigger(pin):
    """Called on rising edge of PIR output."""
    ts = str(utime.time())
    print(f"[doorbell] Trigger at {ts}")

    # 1. chime immediately (no WiFi needed)
    chime()
    wdt.feed()

    # 2. send push notification
    connected = connect_wifi()
    wdt.feed()
    alerted = send_ntfy(ts) if connected else False
    wdt.feed()

    # 3. persist event
    log_event(ts, alerted)

    status = "notified" if alerted else ("wifi-fail" if not connected else "ntfy-fail")
    print(f"[doorbell] Event logged — status: {status}")


# ── main ──────────────────────────────────────────────────────────────────
pir = machine.Pin(PIR_PIN, machine.Pin.IN, machine.Pin.PULL_DOWN)
pir.irq(trigger=machine.Pin.IRQ_RISING, handler=handle_trigger)

print("Pico Smart Doorbell armed.")
print(f"  PIR    → GP{PIR_PIN}")
print(f"  Buzzer → GP{BUZZER_PIN}")
print(f"  ntfy   → {NTFY_TOPIC}")
print("Waiting for motion…")

while True:
    wdt.feed()
    utime.sleep_ms(500)
