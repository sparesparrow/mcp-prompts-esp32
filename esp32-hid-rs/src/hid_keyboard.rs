mod layout;
use embassy_usb::class::hid::{HidWriter, HidError};
use embassy_time::Duration;

pub struct HidKeyboard<'a> {
    writer: HidWriter<'a>,
}

impl<'a> HidKeyboard<'a> {
    pub fn new(writer: HidWriter<'a>) -> Self {
        Self { writer }
    }

    pub async fn send_string(&mut self, text: &str) -> Result<(), HidError> {
        for c in text.chars() {
            if let Some((modifier, keycode)) = layout::char_to_hid(c) {
                self.send_key_report(modifier, keycode).await?;
                self.send_key_release().await?;
                embassy_time::Timer::after(Duration::from_millis(10)).await;
            }
        }
        Ok(())
    }

    async fn send_key_report(&mut self, modifier: u8, keycode: u8) -> Result<(), HidError> {
        let report = [modifier, 0, keycode, 0, 0, 0, 0, 0];
        self.writer.write(&report).await?;
        Ok(())
    }

    async fn send_key_release(&mut self) -> Result<(), HidError> {
        let report = [0u8; 8];
        self.writer.write(&report).await?;
        Ok(())
    }
}

// layout.rs bude obsahovat mapování znaků na HID kódy (QWERTY, Shift, komentáře pro rozšíření CZ layoutu)

/// Mapuje znak na HID keycode a modifikátor (QWERTY, základní ASCII)
pub fn char_to_hid(c: char) -> Option<(u8, u8)> {
    match c {
        'a'..='z' => Some((0, 0x04 + (c as u8 - b'a'))),
        'A'..='Z' => Some((0x02, 0x04 + (c as u8 - b'A'))), // 0x02 = Left Shift
        '0'..='9' => Some((0, match c {
            '0' => 0x27,
            '1' => 0x1E,
            '2' => 0x1F,
            '3' => 0x20,
            '4' => 0x21,
            '5' => 0x22,
            '6' => 0x23,
            '7' => 0x24,
            '8' => 0x25,
            '9' => 0x26,
            _ => 0,
        })),
        ' ' => Some((0, 0x2C)),
        '\n' | '\r' => Some((0, 0x28)),
        '!' => Some((0x02, 0x1E)),
        '@' => Some((0x02, 0x1F)),
        '#' => Some((0x02, 0x20)),
        '$' => Some((0x02, 0x21)),
        '%' => Some((0x02, 0x22)),
        '^' => Some((0x02, 0x23)),
        '&' => Some((0x02, 0x24)),
        '*' => Some((0x02, 0x25)),
        '(' => Some((0x02, 0x26)),
        ')' => Some((0x02, 0x27)),
        '-' => Some((0, 0x2D)),
        '_' => Some((0x02, 0x2D)),
        '=' => Some((0, 0x2E)),
        '+' => Some((0x02, 0x2E)),
        '[' => Some((0, 0x2F)),
        '{' => Some((0x02, 0x2F)),
        ']' => Some((0, 0x30)),
        '}' => Some((0x02, 0x30)),
        '\\' => Some((0, 0x31)),
        '|' => Some((0x02, 0x31)),
        ';' => Some((0, 0x33)),
        ':' => Some((0x02, 0x33)),
        '\'' => Some((0, 0x34)),
        '"' => Some((0x02, 0x34)),
        '`' => Some((0, 0x35)),
        '~' => Some((0x02, 0x35)),
        ',' => Some((0, 0x36)),
        '<' => Some((0x02, 0x36)),
        '.' => Some((0, 0x37)),
        '>' => Some((0x02, 0x37)),
        '/' => Some((0, 0x38)),
        '?' => Some((0x02, 0x38)),
        _ => None,
    }
} 