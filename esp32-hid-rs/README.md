# esp32-hid-rs

Rust library for implementing USB HID keyboard and composite device (HID + RNDIS + CDC) on ESP32-S3.

---

## Module Overview

- **hid_keyboard.rs**: Implements the `HidKeyboard` struct and the `send_string` API for sending text as HID keypresses.
- **composite.rs**: Structure and logic for composite USB device (HID + RNDIS + CDC).
- **layout.rs**: Character-to-HID keycode mapping (QWERTY, ASCII, extendable for CZ/SK).
- **hid/descriptors.rs**: Contains the HID boot protocol report descriptor.

## Architecture

- **Hardware:** ESP32-S3 with native USB FS controller (D+/D-)
- **Stack:** [TinyUSB](https://github.com/hathach/tinyusb) (C, via ESP-IDF) → [embassy-usb](https://docs.embassy.dev/embassy-usb/) (Rust async) → [usbd-hid](https://docs.rs/usbd-hid) (HID reports) → `esp32-hid-rs` (text-to-HID logic)
- **Profiles:**
  - `std` for desktop/server
  - `embedded,hid` for ESP32-S3 (target: xtensa-esp32s3-none-elf)
- **Composite device:** Ready for HID + RNDIS + CDC (see `composite.rs`)

## Features
- HID keyboard (boot protocol, QWERTY, basic ASCII)
- Composite device (HID + RNDIS + CDC, ready for extension)
- API: `send_string(&str)` for sending text as a HID sequence
- Easy integration into MCP firmware

## Quick Start (Embedded)

1. Add to your `Cargo.toml`:
   ```toml
   esp32-hid-rs = { path = "../esp32-hid-rs", features = ["hid"] }
   ```
2. In your firmware, initialize Embassy USB and create a `HidKeyboard`:
   ```rust
   use esp32_hid_rs::HidKeyboard;
   // ... initialize embassy_usb, get HidWriter ...
   let mut keyboard = HidKeyboard::new(writer);
   keyboard.send_string("Hello, world!\n").await?;
   ```
3. Build for ESP32-S3:
   ```sh
   cargo build --release --target xtensa-esp32s3-none-elf --features "embedded,hid"
   ```
4. Flash using your preferred tool (see `scripts/flash_esp32_hid.sh`).

---

## Troubleshooting

- **Device not enumerating as HID?**
  - Check USB wiring (D+/D-), power, and that the correct descriptor is used.
  - Use `lsusb` (Linux) or Device Manager (Windows) to inspect device class.
  - Try a different USB cable or port.
- **HID reports not received by host?**
  - Ensure `send_string` is called after USB is configured.
  - Add delays between keypresses if host misses characters.
- **Composite device not recognized?**
  - Some OSes require drivers for RNDIS/CDC. Test HID-only first.
  - Check that all interface descriptors are valid and non-overlapping.
- **Key mapping issues?**
  - See `layout.rs` for mapping logic. Extend for your locale if needed.
- **Build errors for xtensa-esp32s3-none-elf?**
  - Ensure you have the correct Rust target and toolchain installed.
  - Source your ESP-IDF environment before building.

For more, see the documentation and example scripts in the `scripts/` directory.

## Installation

Add to `Cargo.toml`:
```toml
esp32-hid-rs = { path = "../esp32-hid-rs", features = ["hid"] }
```

## Usage Example

```rust
use esp32_hid_rs::HidKeyboard;

// ... initialize embassy_usb, get HidWriter ...
let mut keyboard = HidKeyboard::new(writer);
keyboard.send_string("Hello, world!\n").await?;
```

## Build with MCP firmware

- Add `esp32-hid-rs` as a dependency to `mcp-prompts-rs`
- Build: `cargo build --release --target xtensa-esp32s3-none-elf --features "embedded,hid"`

## Character mapping to HID keycodes

Uses QWERTY mapping, basic ASCII characters, including modifiers (Shift).
- See `layout.rs` for mapping logic
- For Czech/Slovak layout, extend `char_to_hid()` with additional match arms

## Composite device

Structure ready for extension with RNDIS/CDC (USB network, serial link). See `composite.rs`.

## Security notes
- Whitelist of allowed prompts (see integration in MCP server)
- Limiter: 1 prompt/minute
- Audit log: hash, timestamp, prompt_id
- All prompt modifications are validated against JSON Schema before embedding in ROM

## Testing
- Verify device enumeration on Windows, Linux, Android, BIOS/UEFI (boot protocol)
- Test sending text to a text editor via HID
- Unit tests for `char_to_hid()` mapping
- Integration test for composite device enumeration
- Hardware-in-the-loop: CI runner with USB mux for real PC testing

## References
- [ESP-IDF USB device API](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/usb_device.html)
- [TinyUSB HID boot protocol example](https://github.com/hathach/tinyusb/discussions/1003)
- [embassy-usb documentation](https://docs.embassy.dev/embassy-usb/)
- [usbd-hid crate](https://docs.rs/usbd-hid)
- [Composite device design](https://lib.rs/crates/esp-synopsys-usb-otg)

## License
MIT
