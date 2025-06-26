use crate::hid_keyboard::HidKeyboard;
// use crate::rndis::RndisInterface; // budoucí rozšíření
// use crate::cdc::CdcInterface; // budoucí rozšíření

/// Struktura pro composite USB device (HID + RNDIS + CDC)
pub struct CompositeDevice {
    pub hid: Option<HidKeyboard<'static>>,
    // pub rndis: Option<RndisInterface>,
    // pub cdc: Option<CdcInterface>,
}

impl CompositeDevice {
    pub fn new(hid: Option<HidKeyboard<'static>>) -> Self {
        // Inicializace všech rozhraní (zatím pouze HID, ostatní lze přidat později)
        Self {
            hid,
            // rndis: None,
            // cdc: None,
        }
    }

    pub fn start(&self) {
        // Spuštění všech rozhraní (zatím pouze placeholder)
        // Např. self.hid.as_ref().map(|h| h.start());
    }

    /// Odeslání textu jako HID sekvence přes HID klávesnici (pokud je přítomna)
    pub async fn send_string(&mut self, text: &str) -> Result<(), ()> {
        if let Some(hid) = self.hid.as_mut() {
            hid.send_string(text).await.map_err(|_| ())
        } else {
            Err(())
        }
    }
}

// Pro rozšíření: přidejte inicializaci a start pro RNDIS/CDC podle potřeby. 