## Testing & Validation

### Manual Checklist
- [ ] Verify HID keyboard functionality on Windows, Linux, and Android (OTG/tethering)
- [ ] Test fallback to WiFi/WebSocket if USB is not available
- [ ] Measure binary size and ensure it is below 3MB

### How to Measure Binary Size
After building, check the binary size:

```sh
stat --printf="%s" esp32-hid-rs/target/xtensa-esp32s3-none-elf/release/esp32-hid-rs
```
The build script will fail if the binary exceeds 3MB.

### Tips
- Use different USB ports/cables/adapters if enumeration fails
- For national layouts, extend `layout.rs`
- Check logs and dmesg (Linux) or Device Manager (Windows) for device status
# mcp-prompts-esp32

## USB HID Integration (esp32-hid-rs)

This project integrates a USB HID keyboard and composite device (HID + RNDIS + CDC) for ESP32-S3 using the `esp32-hid-rs` crate.

### HID Usage Scenarios
- Send prompts or text from ESP32 to a host (PC, Android, etc.) as a USB keyboard.
- Use as a composite device: HID + RNDIS (network) + CDC (serial).
- Fallback to WiFi/WebSocket if USB is not available.

### Example: Sending a Prompt as Keyboard
```rust
use esp32_hid_rs::HidKeyboard;
// ... initialize embassy_usb, get HidWriter ...
let mut keyboard = HidKeyboard::new(writer);
keyboard.send_string("Hello, world!\n").await?;
```

### Composite Device Example
```rust
use esp32_hid_rs::CompositeDevice;
let mut composite = CompositeDevice::new(Some(keyboard));
composite.send_string("Prompt").await?;
```

### Troubleshooting
- If the device does not enumerate as a keyboard, check USB cable and power.
- Ensure the binary size is below 3MB (see build scripts for checks).
- For national layouts (CZ/SK), extend `layout.rs` mapping.
- On Windows/Android, test with different USB ports and OTG adapters.

---

See also: `esp32-hid-rs/README.md`, `usb-hid-implementation.md`, `esp32-build-scripts.md`