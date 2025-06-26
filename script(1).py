# Vytvořím komplétní seznam souborů pro mcp-prompts-rs s ESP32 podporou
import json

# Struktura souborů pro mcp-prompts-rs s ESP32 podporou
file_structure = {
    "Cargo.toml": {
        "description": "Hlavní konfigurace projektu s ESP32 features",
        "priority": "CRITICAL",
        "type": "config"
    },
    ".cargo/config.toml": {
        "description": "Rust toolchain konfigurace pro ESP32",
        "priority": "CRITICAL", 
        "type": "config"
    },
    "src/main.rs": {
        "description": "Desktop/cloud entry point",
        "priority": "HIGH",
        "type": "source"
    },
    "src/lib.rs": {
        "description": "Společná logika, export všech modulů",
        "priority": "HIGH",
        "type": "source"
    },
    "src/embedded/main.rs": {
        "description": "ESP32 entry point (#![no_std])",
        "priority": "CRITICAL",
        "type": "source"
    },
    "src/embedded/build.rs": {
        "description": "Compile-time konfigurace pro ESP32",
        "priority": "HIGH",
        "type": "source"
    },
    "src/api/mod.rs": {
        "description": "API modul export",
        "priority": "MEDIUM",
        "type": "source"
    },
    "src/api/http.rs": {
        "description": "REST API pro desktop",
        "priority": "MEDIUM",
        "type": "source"
    },
    "src/api/websocket.rs": {
        "description": "WebSocket server (desktop + ESP32)",
        "priority": "CRITICAL",
        "type": "source"
    },
    "src/api/mcp.rs": {
        "description": "MCP protocol implementation",
        "priority": "CRITICAL",
        "type": "source"
    },
    "src/storage/mod.rs": {
        "description": "Storage backends export",
        "priority": "HIGH",
        "type": "source"
    },
    "src/storage/fs.rs": {
        "description": "File system storage (desktop)",
        "priority": "MEDIUM",
        "type": "source"
    },
    "src/storage/postgres.rs": {
        "description": "PostgreSQL storage (desktop)",
        "priority": "LOW",
        "type": "source"
    },
    "src/storage/littlefs.rs": {
        "description": "LittleFS storage pro ESP32",
        "priority": "CRITICAL",
        "type": "source"
    },
    "src/model/mod.rs": {
        "description": "Data models export",
        "priority": "HIGH",
        "type": "source"
    },
    "src/model/prompt.rs": {
        "description": "Prompt struktury a logika",
        "priority": "HIGH",
        "type": "source"
    },
    "src/model/schema.rs": {
        "description": "JSON schémata a validace",
        "priority": "MEDIUM",
        "type": "source"
    },
    "src/utils/mod.rs": {
        "description": "Utility funkce export",
        "priority": "MEDIUM",
        "type": "source"
    },
    "src/utils/templating.rs": {
        "description": "Template engine (Handlebars/vlastní)",
        "priority": "MEDIUM",
        "type": "source"
    },
    "src/utils/serde_ext.rs": {
        "description": "Serde rozšíření",
        "priority": "LOW",
        "type": "source"
    },
    "src/utils/logger.rs": {
        "description": "Logging abstrakce",
        "priority": "LOW",
        "type": "source"
    },
    ".github/workflows/ci.yml": {
        "description": "Continuous Integration",
        "priority": "HIGH",
        "type": "ci"
    },
    ".github/workflows/esp-build.yml": {
        "description": "ESP32 cross-compilation",
        "priority": "CRITICAL",
        "type": "ci"
    },
    ".github/workflows/release.yml": {
        "description": "Semantic release workflow",
        "priority": "MEDIUM",
        "type": "ci"
    },
    "scripts/flash_esp32.sh": {
        "description": "ESP32 flash skript",
        "priority": "CRITICAL",
        "type": "script"
    },
    "scripts/export_catalog.ts": {
        "description": "Export JSON z mcp-prompts-catalog",
        "priority": "HIGH",
        "type": "script"
    },
    "scripts/build_esp32.sh": {
        "description": "Build script pro ESP32",
        "priority": "CRITICAL",
        "type": "script"
    },
    "prompts/system/memory_cleanup.json": {
        "description": "Příklad system promptu",
        "priority": "LOW",
        "type": "data"
    },
    "prompts/iot/garage_door.json": {
        "description": "Příklad IoT promptu",
        "priority": "LOW",
        "type": "data"
    },
    "build.rs": {
        "description": "Build-time konfigurace a feature gates",
        "priority": "HIGH",
        "type": "config"
    },
    "tests/integration_http.rs": {
        "description": "HTTP API testy",
        "priority": "MEDIUM",
        "type": "test"
    },
    "tests/integration_ws.rs": {
        "description": "WebSocket testy",
        "priority": "HIGH",
        "type": "test"
    },
    "tests/storage_test.rs": {
        "description": "Storage backends testy",
        "priority": "MEDIUM",
        "type": "test"
    },
    "docker/Dockerfile": {
        "description": "Docker kontejner pro desktop",
        "priority": "LOW",
        "type": "config"
    },
    "docker/entrypoint.sh": {
        "description": "Docker entrypoint",
        "priority": "LOW",
        "type": "script"
    },
    ".env.example": {
        "description": "Env proměnné template",
        "priority": "MEDIUM",
        "type": "config"
    },
    "README.md": {
        "description": "Dokumentace projektu",
        "priority": "MEDIUM",
        "type": "docs"
    },
    "CHANGELOG.md": {
        "description": "História změn",
        "priority": "LOW",
        "type": "docs"
    }
}

# Rozdělíme soubory podle priority a typu
critical_files = []
high_files = []
medium_files = []
low_files = []

for filename, info in file_structure.items():
    file_info = f"{filename} - {info['description']}"
    if info['priority'] == 'CRITICAL':
        critical_files.append(file_info)
    elif info['priority'] == 'HIGH':  
        high_files.append(file_info)
    elif info['priority'] == 'MEDIUM':
        medium_files.append(file_info)
    else:
        low_files.append(file_info)

print("=== KRITICKÉ SOUBORY (nutné pro ESP32 funkcionalitu) ===")
for f in critical_files:
    print(f"🔴 {f}")

print("\n=== VYSOKÁ PRIORITA (základní funkcionalita) ===")    
for f in high_files:
    print(f"🟡 {f}")

print("\n=== STŘEDNÍ PRIORITA (rozšíření) ===")
for f in medium_files:
    print(f"🟢 {f}")

print("\n=== NÍZKÁ PRIORITA (nice-to-have) ===")
for f in low_files:
    print(f"⚪ {f}")

print(f"\nCELKEM: {len(file_structure)} souborů")