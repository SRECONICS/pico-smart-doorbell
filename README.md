<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=30&duration=2800&pause=2000&color=00D9FF&center=true&vCenter=true&width=900&lines=Pico+Smart+Doorbell+%F0%9F%94%94;PIR+%2B+WiFi+Push+Alert;MicroPython+on+RP2040;Battery-Powered+%7C+Instant+Notifications" alt="Typing SVG" />

<br/>

[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi%20Pico%20W-c51a4a?style=for-the-badge&logo=raspberrypi&logoColor=white)](https://www.raspberrypi.com/products/raspberry-pi-pico/)
[![Language](https://img.shields.io/badge/Language-MicroPython-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://micropython.org/)
[![Notification](https://img.shields.io/badge/Push-ntfy.sh-7B68EE?style=for-the-badge&logo=pushover&logoColor=white)](https://ntfy.sh)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![DevNode](https://img.shields.io/badge/by-DevNode%20Technologies-FF6B35?style=for-the-badge)](https://github.com/SRECONICS)

<br/>

```
 ┌─────────────────────────────────────────────────────┐
 │  PIR detects motion → Piezo chimes → Phone notified │
 │  Deep-sleep between events → runs weeks on a LiPo   │
 └─────────────────────────────────────────────────────┘
```

</div>

---

## ✨ Features

| Feature | Details |
|---------|---------|
| 🔔 **Instant Push** | Free push notifications via [ntfy.sh](https://ntfy.sh) — no account, no subscription |
| 🔋 **Battery First** | Hardware WDT + PIR interrupt-driven — Pico W sleeps until motion fires |
| 🎵 **Local Chime** | 4-note ascending piezo melody on every trigger |
| 📝 **Flash Log** | Every event written to `doorbell_log.json` on-device flash |
| 🔄 **Auto-Recovery** | 8-second hardware watchdog resets on WiFi hang or crash |
| 📶 **WiFi Resilient** | 15-second connect timeout; logs event locally even if offline |

---

## 🔧 Hardware

```
┌──────────────────────┐
│   Raspberry Pi       │
│      Pico W          │         ┌──────────┐
│                      │         │   PIR    │
│  GP15 ◄──────────────┼─────────┤  Sensor  │
│  GP16 ──────────────►│         └──────────┘
│                      │         ┌──────────┐
│  VSYS ◄──────────────┼─────────┤  LiPo +  │
│  GND  ◄──────────────┼─────────┤  TP4056  │
└──────────────────────┘         └──────────┘
         │GP16
         ▼
    ┌─────────┐
    │  Piezo  │
    │  Buzzer │
    └─────────┘
```

| Part | Connection | Notes |
|------|-----------|-------|
| PIR HC-SR501 | OUT → GP15 | PULL_DOWN in firmware |
| Piezo Buzzer | + → GP16, − → GND | PWM driven |
| LiPo 3.7V | VSYS via TP4056 | 500 mAh runs ~2 weeks |
| Pico W | — | RP2040 + CYW43439 WiFi |

---

## 🚀 Quick Start

### 1. Flash MicroPython
Download the Pico W build from [micropython.org](https://micropython.org/download/RPI_PICO_W/) and flash it.

### 2. Configure credentials
Edit `src/config.py`:
```python
WIFI_SSID   = "YourNetwork"
WIFI_PASS   = "YourPassword"
NTFY_TOPIC  = "my-doorbell"    # pick any unique name
```

### 3. Upload to Pico W
```bash
# Using mpremote
mpremote cp src/config.py :config.py
mpremote cp src/main.py   :main.py

# Or drag-drop in Thonny
```

### 4. Get notifications
Install the **ntfy** app → subscribe to your topic name. Done.

<details>
<summary>📱 ntfy setup (click to expand)</summary>

1. Android: [Play Store](https://play.google.com/store/apps/details?id=io.heckel.ntfy) | iOS: [App Store](https://apps.apple.com/app/ntfy/id1625396347)
2. Open app → tap **+** → enter your topic name (same as `NTFY_TOPIC` in config)
3. Notifications arrive as native push alerts — no login needed

</details>

---

## 📁 Project Structure

```
pico-smart-doorbell/
├── src/
│   ├── main.py          # Main firmware — PIR interrupt, chime, WiFi, ntfy
│   └── config.py        # WiFi credentials + topic (gitignored)
├── docs/
│   └── wiring.md        # Detailed wiring notes
├── config.example.py    # Template — copy to src/config.py
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🛠️ How It Works

```
 Power-on
    │
    ▼
 Setup WDT (8s) + PIR interrupt on GP15
    │
    ▼ (sleeps here — µA draw)
 ◄── PIR fires (RISING edge) ──────────────────────────────────┐
    │                                                           │
    ▼                                                           │
 Chime piezo (4-note melody)          next trigger resumes here┘
    │
    ▼
 Connect WiFi (15s timeout)
    │
    ▼
 POST to ntfy.sh/{NTFY_TOPIC}
    │
    ▼
 Append {"ts":..., "alerted":...} to doorbell_log.json
    │
    ▼
 Feed WDT → back to sleep
```

---

## 📊 Power Budget

| State | Current | Duration |
|-------|---------|---------|
| Deep idle (PIR polling) | ~22 mA | between events |
| Chime + WiFi connect | ~160 mA | ~3 s per event |
| **500 mAh LiPo** | — | **~2 weeks** (10 triggers/day) |

---

## 🔔 Notification Format

```
Title:    Doorbell 🔔
Priority: High
Body:     Someone at the door — 1726285200
Tags:     bell
```

---

## 📝 Event Log

Events are appended to `doorbell_log.json` on Pico flash:
```json
{"ts": "1726285200", "alerted": true}
{"ts": "1726291800", "alerted": false}
```
`alerted: false` = WiFi was down; chime still played locally.

---

<div align="center">

Made with ❤️ by [DevNode Technologies](https://github.com/SRECONICS)

[![GitHub](https://img.shields.io/badge/More%20Projects-SRECONICS-181717?style=for-the-badge&logo=github)](https://github.com/SRECONICS)

</div>
