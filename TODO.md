# TODO: Integrace USB HID (esp32-hid-rs) do MCP ESP32 build/deploy

## 1. Vytvořit repozitář/balíček `esp32-hid-rs`
- [ ] Inicializovat nový Rust crate s podporou ESP32-S3 (xtensa-esp32s3-none-elf)
- [ ] Přidat závislosti: `embassy-usb`, `esp-hal`, `usbd-hid`, `embassy-executor`, `embassy-time`
- [ ] Implementovat základní HID klávesnici (viz HID_BOOT_KEYBOARD_DESCRIPTOR)
- [ ] Implementovat CompositeDevice (HID + RNDIS + CDC)
- [ ] Přidat API: `send_string(text: &str)` pro odeslání textu jako HID sekvence
- [ ] Přidat testy: boot protocol, composite enumeration

## 2. Propojit s mcp-prompts-rs (v embedded režimu)
- [ ] Přidat feature `hid` do Cargo.toml a build pipeline
- [ ] V `src/embedded/main.rs` přidat inicializaci HID device a napojení na MCP příkazy
- [ ] Umožnit přijímat MCP příkaz `SendHidText` a předat do HID klávesnice
- [ ] Otestovat odeslání promptu přes HID do hostitelského zařízení

## 3. Build & deploy pipeline
- [ ] Upravit `scripts/build_esp32.sh`/`build_esp32_hid.sh` pro build s feature `hid`
- [ ] Přidat `scripts/flash_esp32_hid.sh` pro flashování HID firmware
- [ ] Aktualizovat `.github/workflows/esp-build.yml` pro build/test HID varianty

## 4. Dokumentace
- [ ] Přidat sekci o HID do README (MCP + HID scénáře)
- [ ] Popsat příklady použití (odeslání promptu jako klávesnice, composite device)
- [ ] Přidat troubleshooting (enumerace, kompatibilita, velikost binárky)

## 5. Testování a validace
- [ ] Ověřit funkčnost na Windows, Linux, Android (tethering + HID)
- [ ] Otestovat fallback na WiFi/WebSocket při absenci USB
- [ ] Změřit velikost binárky, optimalizovat pro <3MB

---

Viz také: usb-hid-implementation.md, final-implementation-plan.md, esp32-build-scripts.md 