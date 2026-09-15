# Wiring Guide — Pico Smart Doorbell

## Components
- Raspberry Pi Pico W
- HC-SR501 PIR motion sensor
- Passive piezo buzzer
- LiPo 3.7V 500 mAh
- TP4056 LiPo charger module

## Pin Connections

```
Pico W Pin    │ Component
─────────────────────────────────────────
GP15          │ PIR sensor OUT
GP16          │ Piezo buzzer + leg
GND           │ PIR GND, Piezo −, TP4056 GND
VSYS (pin 39) │ TP4056 OUT+  (battery power in)
```

## PIR Sensitivity
- Adjust the sensitivity pot on HC-SR501 clockwise to increase range
- Time-delay pot: turn counter-clockwise to minimum (~3s) to avoid missing rapid triggers

## Power Notes
- VSYS accepts 1.8–5.5V so TP4056 3.7V LiPo output works directly
- Do **not** connect to 3V3 — it's an output pin on the Pico
- USB can remain connected for charging while running
