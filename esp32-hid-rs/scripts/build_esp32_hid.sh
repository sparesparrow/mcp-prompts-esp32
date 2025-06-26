#!/bin/bash
# Build script pro ESP32 HID firmware
set -e

echo "🔧 Building ESP32-S3 HID firmware..."

# Environment setup
source $HOME/export-esp.sh

# Build s HID podporou
cargo build --release --target xtensa-esp32s3-none-elf --features "hid"

# Kontrola velikosti
SIZE=$(stat -c%s target/xtensa-esp32s3-none-elf/release/esp32-hid-rs)
echo "📊 Binary size: $(echo "scale=2; $SIZE/1024/1024" | bc)MB"
if [ $SIZE -gt 3145728 ]; then
    echo "❌ Binary too large: ${SIZE} bytes (max 3MB)"
    exit 1
fi

echo "✅ Build successful: ${SIZE} bytes" 