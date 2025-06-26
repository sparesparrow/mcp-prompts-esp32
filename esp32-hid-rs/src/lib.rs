#![no_std]

//! esp32-hid-rs: USB HID keyboard and composite device for ESP32-S3
//!
//! - HID boot protocol keyboard (QWERTY, basic ASCII)
//! - Composite device (HID + RNDIS + CDC)
//! - API: send_string(&str) for sending text as HID sequence

pub mod hid_keyboard;
pub mod composite;
pub mod layout;
pub mod hid {
    pub mod descriptors;
}

pub use hid_keyboard::HidKeyboard;
pub use composite::CompositeDevice;

// For embedded build: use --features "embedded,hid"
// For desktop build: use --features "std"