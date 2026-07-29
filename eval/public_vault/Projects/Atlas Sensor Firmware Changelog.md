---
id: 01JEV000000000000000000199
title: Atlas Sensor Firmware Changelog
type: log
created: 2025-02-12T09:00:00Z
updated: 2026-05-17T12:00:00Z
tags: [atlas, project]
---
# Atlas Sensor Firmware Changelog

## Version 2.8 (March 2025)

Fixed intermittent ADC sampling drops on power-up due to insufficient capacitor charge time. Added calibration offset storage in EEPROM to preserve drift corrections across power cycles. See [[Atlas Milestone Tracker]] for deployment timeline.

## Version 2.7 (January 2025)

Reduced transmission current draw by 12% through optimized RF module sequencing. Added temperature compensation for humidity readings using lookup table approximation. Improved LoRaWAN join reliability by extending transmit window from 2 to 5 seconds.

## Version 2.6 (October 2024)

Initial production release. Implements core sensing pipeline: temperature, humidity, and air pressure sampling at 1-minute intervals. LoRaWAN transmission batching groups 8 readings into single packet to reduce airtime and power consumption.

## Version 2.5 (August 2024)

Beta release for field trials. Includes basic telemetry: battery voltage, signal strength, and transmission success count. Early versions detected false resets during high RF interference; resolved in 2.6 through improved power supply filtering.
