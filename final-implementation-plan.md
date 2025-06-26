# Finální seznam souborů pro implementaci mcp-prompts-rs s ESP32

## 🔴 KRITICKÉ SOUBORY (implementovat okamžitě)

### Cargo.toml
**Priorita:** KRITICKÁ  
**Typ:** Konfigurace  
**Popis:** Hlavní konfigurace projektu s ESP32 features, dual binaries, conditional dependencies  
**Implementace:** Obsahuje `[[bin]]` sekce pro desktop i embedded, features pro `std`/`no-std`, ESP32 dependencies

### .cargo/config.toml  
**Priorita:** KRITICKÁ  
**Typ:** Konfigurace  
**Popis:** Rust toolchain konfigurace pro ESP32 - target, runner, environment variables  
**Implementace:** Nastavuje `xtensa-esp32s3-none-elf` target, `espflash` runner, WiFi credentials

### src/embedded/main.rs
**Priorita:** KRITICKÁ  
**Typ:** Zdrojový kód  
**Popis:** ESP32 entry point s `#![no_std]`, WiFi setup, WebSocket server  
**Implementace:** Async main loop, WiFi init, LittleFS storage, embedded prompts loading

### src/api/websocket.rs
**Priorita:** KRITICKÁ  
**Typ:** Zdrojový kód  
**Popis:** Unifikovaný WebSocket server pro desktop (tokio-tungstenite) + ESP32 (embedded-svc)  
**Implementace:** Feature-gated implementation, JSON-RPC over WebSocket, MCP protocol handling

### src/api/mcp.rs
**Priorita:** KRITICKÁ  
**Typ:** Zdrojový kód  
**Popis:** Model Context Protocol implementation podle specifikace  
**Implementace:** JSON-RPC 2.0, MCP message types, resource/tool/prompt handlers

### src/storage/littlefs.rs
**Priorita:** KRITICKÁ  
**Typ:** Zdrojový kód  
**Popis:** LittleFS filesystem storage pro ESP32, fallback na embedded prompts  
**Implementace:** ESP-IDF LittleFS bindings, error handling, embedded prompts integration

### scripts/build_esp32.sh
**Priorita:** KRITICKÁ  
**Typ:** Build skript  
**Popis:** Complete ESP32 build pipeline - toolchain check, catalog export, compilation, binary generation  
**Implementace:** Bash script s error handling, size checks, esptool integration

### scripts/flash_esp32.sh  
**Priorita:** KRITICKÁ  
**Typ:** Deploy skript  
**Popis:** ESP32 flashing script s port detection, filesystem upload  
**Implementace:** esptool.py automation, port validation, progress reporting

### .github/workflows/esp-build.yml
**Priorita:** KRITICKÁ  
**Typ:** CI/CD  
**Popis:** GitHub Actions pro ESP32 cross-compilation, artifact upload  
**Implementace:** Ubuntu runner, espup installation, artifact caching, binary validation

## 🟡 VYSOKÁ PRIORITA (základní funkcionalita)

### src/main.rs
**Typ:** Entry point pro desktop/cloud  
**Implementace:** Tokio runtime, HTTP + WebSocket servers, CLI args parsing

### src/lib.rs  
**Typ:** Library root s exports  
**Implementace:** Conditional module exports, feature gates, public API

### src/embedded/build.rs
**Typ:** Embedded build config  
**Implementace:** ESP-IDF specific build flags, memory optimization

### src/storage/mod.rs
**Typ:** Storage trait definition  
**Implementace:** Async Storage trait, error types, backend selection

### src/model/prompt.rs
**Typ:** Prompt data structures  
**Implementace:** Serde-compatible structs, validation, templating support

### build.rs
**Typ:** Build-time configuration  
**Implementace:** Feature detection, ESP-IDF integration, linker scripts

### scripts/export_catalog.ts
**Typ:** Catalog export script  
**Implementace:** TypeScript tool pro export JSON → Rust const arrays

### tests/integration_ws.rs
**Typ:** WebSocket integration tests  
**Implementace:** Test WebSocket MCP communication, both desktop and embedded

## 🟢 STŘEDNÍ PRIORITA (rozšíření)

### src/api/http.rs
**Typ:** REST API pro desktop  
**Implementace:** Hyper/Axum based REST endpoints, OpenAPI spec

### src/storage/fs.rs  
**Typ:** Filesystem storage  
**Implementace:** JSON file storage, directory watching, atomic writes

### src/model/schema.rs
**Typ:** JSON Schema validation  
**Implementace:** Serde schemas, MCP protocol validation

### src/utils/templating.rs
**Typ:** Template engine  
**Implementace:** Handlebars or custom template processor, variable substitution

## ⚪ NÍZKÁ PRIORITA (nice-to-have)

### src/storage/postgres.rs
**Typ:** PostgreSQL backend  
**Implementace:** SQLx integration, migrations, connection pooling

### docker/Dockerfile
**Typ:** Containerization  
**Implementace:** Multi-stage build, runtime optimization

### src/utils/logger.rs
**Typ:** Logging abstraction  
**Implementace:** Feature-gated logging (log crate vs esp-println)

## 📋 IMPLEMENTAČNÍ POŘADÍ

### Fáze 1: ESP32 Minimum Viable Product (1-2 týdny)
1. `Cargo.toml` + `.cargo/config.toml` - základní konfigurace
2. `src/embedded/main.rs` - minimální ESP32 firmware  
3. `src/api/websocket.rs` - jednoduchý WebSocket server
4. `src/storage/littlefs.rs` - embedded-only storage
5. `scripts/build_esp32.sh` + `scripts/flash_esp32.sh` - build pipeline

### Fáze 2: MCP Protocol Integration (1 týden)  
6. `src/api/mcp.rs` - kompletní MCP implementation
7. `src/model/prompt.rs` - prompt data structures
8. `scripts/export_catalog.ts` - catalog automation
9. `.github/workflows/esp-build.yml` - CI/CD

### Fáze 3: Desktop Compatibility (1 týden)
10. `src/main.rs` - desktop entry point
11. `src/lib.rs` - unified library interface  
12. `tests/integration_ws.rs` - comprehensive testing

### Fáze 4: Polish & Extensions (volitelně)
13. HTTP API, PostgreSQL backend, Docker support
14. Advanced templating, logging, monitoring

## 🚀 QUICK START 

```bash
# 1. Instalace toolchain
cargo install espup
espup install  
source ~/export-esp.sh

# 2. Clone a setup
git clone https://github.com/sparesparrow/mcp-prompts-rs
cd mcp-prompts-rs
chmod +x scripts/*.sh

# 3. Build pro ESP32
./scripts/build_esp32.sh

# 4. Flash na zařízení  
./scripts/flash_esp32.sh /dev/ttyUSB0

# 5. Test připojení
# WebSocket na ws://[ESP32_IP]:9000
# MCP client nebo Claude Desktop
```

## 📊 METRIKY ÚSPĚCHU

- ✅ ESP32 firmware < 3MB (fit do 8MB flash)
- ✅ WebSocket MCP server funkční na ESP32  
- ✅ Minimálně 10 embedded promptů
- ✅ WiFi + USB tethering komunikace
- ✅ CI/CD s automatickými artefakty
- ✅ Kompatibilita s Claude Desktop
- ✅ Desktop + ESP32 unified codebase

**Celkový odhad implementace: 3-4 týdny pro full featured řešení**