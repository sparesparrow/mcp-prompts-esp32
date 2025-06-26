# USB HID Implementace pro mcp-prompts-rs

## Přehled architektury

ESP32-S3 podpora nativního USB device stacku založeného na TinyUSB umožňuje implementaci HID klávesnice pro odesílání sestavených promptů přes USB do hostitelského zařízení.

### Podporované transporty
- **WiFi WebSocket** - MCP JSON-RPC komunikace pro konfiguraci
- **USB RNDIS** - síťový interface pro Android USB tethering
- **USB HID Keyboard** - odesílání textových promptů jako klávesové sekvence
- **USB CDC Serial** - alternativní komunikační kanál

### Klíčové komponenty

#### 1. USB Descriptor Configuration
```rust
// Boot protocol support pro BIOS kompatibilitu
const HID_BOOT_KEYBOARD_DESCRIPTOR: &[u8] = &[
    0x05, 0x01,        // Usage Page (Generic Desktop Ctrls)
    0x09, 0x06,        // Usage (Keyboard)
    0xA1, 0x01,        // Collection (Application)
    0x05, 0x07,        //   Usage Page (Kbrd/Keypad)
    0x19, 0xE0,        //   Usage Minimum (0xE0)
    0x29, 0xE7,        //   Usage Maximum (0xE7)
    0x15, 0x00,        //   Logical Minimum (0)
    0x25, 0x01,        //   Logical Maximum (1)
    0x75, 0x01,        //   Report Size (1)
    0x95, 0x08,        //   Report Count (8)
    0x81, 0x02,        //   Input (Data,Var,Abs)
    0x95, 0x01,        //   Report Count (1)
    0x75, 0x08,        //   Report Size (8)
    0x81, 0x03,        //   Input (Cnst,Var,Abs)
    0x95, 0x06,        //   Report Count (6)
    0x75, 0x08,        //   Report Size (8)
    0x15, 0x00,        //   Logical Minimum (0)
    0x25, 0x65,        //   Logical Maximum (101)
    0x05, 0x07,        //   Usage Page (Kbrd/Keypad)
    0x19, 0x00,        //   Usage Minimum (0x00)
    0x29, 0x65,        //   Usage Maximum (0x65)
    0x81, 0x00,        //   Input (Data,Array,Abs)
    0xC0,              // End Collection
];
```

#### 2. Composite Device Setup
```rust
// Kombinace HID klávesnice + RNDIS network
pub struct CompositeDevice {
    hid_interface: HidInterface,
    rndis_interface: RndisInterface,
    cdc_interface: CdcInterface,
}

impl CompositeDevice {
    pub fn new() -> Self {
        // Configuration pro multi-interface device
        // VID: 0xCafe, PID: 0x4020
        // String descriptors: "MCP Prompts", "HID+Network Bridge"
    }
}
```

#### 3. HID Keyboard Implementation
```rust
pub struct HidKeyboard {
    writer: UsbHidWriter<'static>,
    layout: KeyboardLayout,
}

impl HidKeyboard {
    pub async fn send_string(&mut self, text: &str) -> Result<(), HidError> {
        for char in text.chars() {
            let (modifier, keycode) = self.layout.char_to_keycode(char)?;
            self.send_key_report(modifier, keycode).await?;
            self.send_key_release().await?;
            embassy_time::Timer::after(Duration::from_millis(10)).await;
        }
        Ok(())
    }
    
    async fn send_key_report(&mut self, modifier: u8, keycode: u8) -> Result<(), HidError> {
        let report = [modifier, 0, keycode, 0, 0, 0, 0, 0];
        self.writer.write(&report).await?;
        Ok(())
    }
}
```

## Build System

### Cargo.toml Dependencies
```toml
[dependencies]
embassy-executor = { version = "0.6", features = ["arch-xtensa"] }
embassy-usb = { version = "0.3", features = ["defmt"] }
embassy-time = { version = "0.3" }
esp-hal = { version = "0.24", features = ["esp32s3", "embassy-usb"] }
esp-backtrace = { version = "0.15", features = ["esp32s3", "panic-handler", "exception-handler", "print-uart"] }

[features]
default = ["std"]
std = ["dep:tokio", "dep:serde_json"]
embedded = ["dep:embassy-executor", "dep:embassy-usb", "dep:esp-hal"]
hid = ["embedded", "dep:usbd-hid"]
```

### Build Scripts
```bash
#!/bin/bash
# scripts/build_esp32_hid.sh

set -e

echo "🔨 Building ESP32-S3 HID firmware..."

# Environment setup
source $HOME/export-esp.sh

# Generate catalog
node scripts/export_catalog.ts

# Build with HID support
cargo build --release --target xtensa-esp32s3-none-elf --features "embedded,hid"

# Size validation (max 3MB)
SIZE=$(stat -c%s target/xtensa-esp32s3-none-elf/release/mcp-prompts-rs)
if [ $SIZE -gt 3145728 ]; then
    echo "❌ Binary too large: ${SIZE} bytes (max 3MB)"
    exit 1
fi

echo "✅ Build successful: ${SIZE} bytes"
```

## Testing & Deployment

### Integration Tests
```rust
#[cfg(test)]
mod tests {
    use super::*;
    
    #[embassy_executor::test]
    async fn test_hid_keyboard_boot_protocol() {
        let mut keyboard = HidKeyboard::new().await;
        keyboard.send_string("Hello World\n").await.unwrap();
        // Verify boot protocol compatibility
    }
    
    #[embassy_executor::test]
    async fn test_composite_device_enumeration() {
        let device = CompositeDevice::new();
        device.start().await;
        // Test multiple interface enumeration
    }
}
```

### Flash Script
```bash
#!/bin/bash
# scripts/flash_esp32_hid.sh

PORT=${1:-/dev/ttyUSB0}

echo "📡 Flashing ESP32-S3 with HID firmware..."

# Reset to bootloader mode
esptool.py --chip esp32s3 --port $PORT --before default_reset --after hard_reset chip_id

# Erase flash
esptool.py --chip esp32s3 --port $PORT erase_flash

# Flash firmware
espflash flash --monitor target/xtensa-esp32s3-none-elf/release/mcp-prompts-rs --port $PORT

echo "✅ Flash complete - device should enumerate as HID keyboard"
```

## Usage Examples

### 1. Basic HID Keyboard Mode
```rust
// Embedded firmware
#[embassy_executor::main]
async fn main(spawner: Spawner) {
    let mut device = CompositeDevice::new();
    let mut keyboard = device.hid_keyboard();
    
    // Wait for MCP command
    loop {
        let command = mcp_server.recv_command().await;
        match command {
            MccCommand::SendHidText(text) => {
                keyboard.send_string(&text).await?;
            }
        }
    }
}
```

### 2. WebSocket + HID Integration
```typescript
// Client-side usage
const mcpClient = new MCP.Client("ws://192.168.4.1:9000");
await mcpClient.call("prompts/apply", {
    template: "system_prompt_template",
    variables: { task: "code review" },
    output_mode: "hid_keyboard"
});
// ESP32 odešle sestavený prompt jako klávesové sekvence
```

### 3. Android USB Tethering
```rust
// RNDIS network interface pro Android connectivity
pub async fn setup_android_bridge() {
    let usb_device = UsbDeviceBuilder::new()
        .product("MCP Prompts Bridge")
        .manufacturer("SpareSparrow")
        .vid_pid(0xCafe, 0x4021)  // RNDIS VID/PID
        .build();
}
```

## Konfigurace a omezení

### Rychlost a limity
- **USB 1.1 Full Speed**: 12 Mbps
- **Max typing speed**: ~100 znaků/sekundu (10ms delay mezi klávesami)
- **Buffer size**: 8KB (cca 8 sekund textu)
- **Composite device**: HID + RNDIS + CDC současně

### Kompatibilita
- ✅ Windows 10/11 (bez ovladačů)
- ✅ macOS (boot protocol)
- ✅ Linux (všechny distribuce)  
- ✅ Android (USB tethering)
- ✅ BIOS/UEFI (boot protocol)

### Bezpečnostní opatření
- **Whitelist promptů**: pouze schválené šablony
- **Rate limiting**: max 1 prompt per minute
- **Content filtering**: kontrola nebezpečných sekvencí
- **Audit log**: všechny HID operace

## Roadmap

### Fáze 1 (1-2 týdny)
- [ ] Basic HID keyboard implementation
- [ ] Boot protocol support
- [ ] Simple text sending

### Fáze 2 (1 týden)  
- [ ] Composite device (HID + RNDIS)
- [ ] Android USB tethering support
- [ ] WebSocket MCP server

### Fáze 3 (1 týden)
- [ ] Advanced features (macro support)
- [ ] Security hardening
- [ ] Production deployment tools

Tato implementace poskytne robustní a bezpečný způsob odesílání MCP promptů přes USB HID interface s podporou všech hlavních operačních systémů a mobilních zařízení.