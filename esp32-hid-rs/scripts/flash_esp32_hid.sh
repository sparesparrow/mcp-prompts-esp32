#!/bin/bash
# Flash script pro ESP32 HID firmware
PORT=${1:-/dev/ttyUSB0}

echo "📡 Flashing ESP32-S3 with HID firmware..."

# Reset to bootloader mode
esptool.py --chip esp32s3 --port $PORT --before default_reset --after hard_reset chip_id

# Erase flash
esptool.py --chip esp32s3 --port $PORT erase_flash

# Flash firmware
espflash flash --monitor target/xtensa-esp32s3-none-elf/release/esp32-hid-rs --port $PORT

echo "✅ Flash complete - device should enumerate as HID keyboard" 