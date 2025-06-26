# ESP32 Build & Deploy Skripty pro mcp-prompts-rs

## scripts/build_esp32.sh

```bash
#!/bin/bash
# Build script pro ESP32 firmware

set -e

echo "🔧 Building mcp-prompts-rs for ESP32..."

# Kontrola prostředí
if [ ! -f "$HOME/export-esp.sh" ]; then
    echo "❌ ESP toolchain není nainstalován. Spusťte: espup install"
    exit 1
fi

# Načtení ESP toolchain
source $HOME/export-esp.sh

# Kontrola target
rustup target list --installed | grep -q "xtensa-esp32s3-none-elf" || {
    echo "❌ Target xtensa-esp32s3-none-elf není nainstalován"
    exit 1
}

# Vytvoření promptů pro embed
echo "📦 Preparing prompt catalog..."
if [ -f "scripts/export_catalog.ts" ]; then
    npx tsx scripts/export_catalog.ts
fi

# Build pro ESP32
echo "🚀 Building for ESP32-S3..."
cargo build --target xtensa-esp32s3-none-elf --features embedded,no-std --release

# Kontrola velikosti
SIZE=$(stat -f%z target/xtensa-esp32s3-none-elf/release/mcp-prompts-rs 2>/dev/null || stat -c%s target/xtensa-esp32s3-none-elf/release/mcp-prompts-rs)
echo "📊 Binary size: $(echo "scale=2; $SIZE/1024/1024" | bc)MB"

if [ $SIZE -gt 3145728 ]; then  # 3MB limit
    echo "⚠️  Warning: Binary je větší než 3MB"
fi

# Generování .bin souboru
echo "💾 Generating ESP32 binary..."
esptool.py --chip esp32s3 elf2image \
    --flash_mode dio \
    --flash_freq 80m \
    --flash_size 8MB \
    -o target/mcp-prompts-esp32.bin \
    target/xtensa-esp32s3-none-elf/release/mcp-prompts-rs

echo "✅ Build completed: target/mcp-prompts-esp32.bin"
```

## scripts/flash_esp32.sh

```bash
#!/bin/bash
# Flash script pro ESP32

PORT=${1:-"/dev/ttyUSB0"}
BINARY=${2:-"target/mcp-prompts-esp32.bin"}

echo "🔌 Flashing ESP32 on port $PORT..."

# Kontrola přípojení
if [ ! -e "$PORT" ]; then
    echo "❌ Device není připojen na $PORT"
    echo "💡 Dostupné porty:"
    ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || echo "Žádné USB porty"
    exit 1
fi

# Kontrola binárky
if [ ! -f "$BINARY" ]; then
    echo "❌ Binary $BINARY neexistuje. Spusťte nejdříve build_esp32.sh"
    exit 1
fi

# Erase flash
echo "🗑️  Erasing flash..."
esptool.py --chip esp32s3 --port $PORT erase_flash

# Flash bootloader + app
echo "📤 Flashing firmware..."
esptool.py --chip esp32s3 --port $PORT --baud 460800 \
    write_flash -z 0x0 $BINARY

# Flash filesystem (pokud existuje)
if [ -f "target/littlefs.bin" ]; then
    echo "📁 Flashing filesystem..."
    esptool.py --chip esp32s3 --port $PORT --baud 460800 \
        write_flash -z 0x110000 target/littlefs.bin
fi

echo "✅ Flash completed!"
echo "🔄 Restarting ESP32..."
esptool.py --chip esp32s3 --port $PORT run

echo "📟 Monitor serial output:"
echo "    cargo run --bin monitor -- --port $PORT"
```

## scripts/export_catalog.ts

```typescript
#!/usr/bin/env npx tsx
// Export promptů z mcp-prompts-catalog do embedded formátu

import fs from 'fs/promises';
import path from 'path';

interface Prompt {
    id: string;
    name: string;
    content: string;
    variables?: string[];
    tags?: string[];
    version?: string;
}

async function exportCatalog() {
    console.log('📦 Exporting prompt catalog...');
    
    // Načti prompty z různých zdrojů
    const catalogs = [
        '../mcp-prompts-catalog',  // Sesterský repo
        './prompts',               // Lokální prompty
    ];
    
    const allPrompts: Prompt[] = [];
    
    for (const catalog of catalogs) {
        try {
            await processDirectory(catalog, allPrompts);
        } catch (err) {
            console.warn(`⚠️  Cannot read ${catalog}: ${err}`);
        }
    }
    
    // Vytvoř embedded soubor
    const embeddedData = {
        version: "1.0.0",
        generated: new Date().toISOString(),
        prompts: allPrompts.slice(0, 50), // Limit pro ESP32
    };
    
    // Zapíš jako Rust soubor
    const rustCode = `
// Auto-generated prompt catalog
// Generated: ${embeddedData.generated}

use crate::model::Prompt;

pub const EMBEDDED_PROMPTS: &[Prompt] = &[
${allPrompts.map(p => `    Prompt {
        id: "${p.id}",
        name: "${p.name}",
        content: r#"${p.content.replace(/"/g, '\\"')}"#,
        variables: &[${(p.variables || []).map(v => `"${v}"`).join(', ')}],
        tags: &[${(p.tags || []).map(t => `"${t}"`).join(', ')}],
        version: "${p.version || '1.0.0'}",
    },`).join('\n')}
];

pub fn get_prompt_by_id(id: &str) -> Option<&'static Prompt> {
    EMBEDDED_PROMPTS.iter().find(|p| p.id == id)
}

pub fn list_prompts() -> &'static [Prompt] {
    EMBEDDED_PROMPTS
}
`;
    
    await fs.writeFile('src/embedded/prompts.rs', rustCode);
    
    // Vytvoř JSON backup
    await fs.writeFile('target/prompts.json', JSON.stringify(embeddedData, null, 2));
    
    console.log(`✅ Exported ${allPrompts.length} prompts to src/embedded/prompts.rs`);
}

async function processDirectory(dir: string, prompts: Prompt[]) {
    const files = await fs.readdir(dir, { recursive: true });
    
    for (const file of files) {
        if (file.endsWith('.json')) {
            const fullPath = path.join(dir, file);
            const content = await fs.readFile(fullPath, 'utf-8');
            
            try {
                const prompt = JSON.parse(content);
                if (prompt.id && prompt.name && prompt.content) {
                    prompts.push(prompt);
                }
            } catch (err) {
                console.warn(`⚠️  Invalid JSON in ${file}: ${err}`);
            }
        }
    }
}

// Spusť pokud je voláno přímo
if (import.meta.url === `file://${process.argv[1]}`) {
    exportCatalog().catch(console.error);
}
```

## .github/workflows/esp-build.yml

```yaml
name: ESP32 Build

on:
  push:
    branches: [ main, develop ]
    paths: [ 'src/**', 'Cargo.toml', 'scripts/**' ]
  pull_request:
    branches: [ main ]

jobs:
  esp32-build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
      with:
        submodules: recursive
        
    - name: Install Rust
      uses: dtolnay/rust-toolchain@stable
      
    - name: Install ESP toolchain
      run: |
        cargo install espup
        espup install
        echo "$HOME/.rustup/toolchains/esp/bin" >> $GITHUB_PATH
        
    - name: Install esptool
      run: pip install esptool
      
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        
    - name: Install tsx
      run: npm install -g tsx
      
    - name: Cache cargo registry
      uses: actions/cache@v3
      with:
        path: ~/.cargo/registry
        key: ${{ runner.os }}-esp32-cargo-registry-${{ hashFiles('**/Cargo.lock') }}
        
    - name: Export catalog
      run: npx tsx scripts/export_catalog.ts
      
    - name: Build for ESP32
      run: |
        source $HOME/export-esp.sh
        cargo build --target xtensa-esp32s3-none-elf --features embedded,no-std --release
        
    - name: Generate binary
      run: |
        esptool.py --chip esp32s3 elf2image \
          --flash_mode dio --flash_freq 80m --flash_size 8MB \
          -o target/mcp-prompts-esp32.bin \
          target/xtensa-esp32s3-none-elf/release/mcp-prompts-rs
          
    - name: Upload ESP32 binary
      uses: actions/upload-artifact@v3
      with:
        name: mcp-prompts-esp32-${{ github.sha }}
        path: |
          target/mcp-prompts-esp32.bin
          target/prompts.json
        retention-days: 30
        
    - name: Check binary size
      run: |
        SIZE=$(stat -c%s target/mcp-prompts-esp32.bin)
        echo "Binary size: $(echo "scale=2; $SIZE/1024/1024" | bc)MB"
        if [ $SIZE -gt 3145728 ]; then
          echo "::warning::Binary je větší než 3MB"
        fi
```

## Cargo.toml konfigurace

```toml
[package]
name = "mcp-prompts-rs"
version = "0.2.0"
edition = "2021"
authors = ["sparesparrow"]
description = "Rust MCP prompts server with ESP32 support"

[[bin]]
name = "mcp-prompts-rs"
path = "src/main.rs"
required-features = ["std"]

[[bin]]
name = "mcp-prompts-esp32"
path = "src/embedded/main.rs"
required-features = ["embedded"]

[features]
default = ["std", "tokio-runtime"]
std = ["tokio", "tokio-tungstenite", "hyper", "serde_json"]
embedded = ["no-std", "esp-idf-hal", "embedded-svc"]
no-std = ["heapless", "nb"]
postgres = ["sqlx", "std"]
tokio-runtime = ["tokio/macros", "tokio/rt-multi-thread"]

[dependencies]
# Společné závislosti
serde = { version = "1.0", default-features = false, features = ["derive"] }
serde_json = { version = "1.0", default-features = false, optional = true }
heapless = { version = "0.8", optional = true }

# Desktop/cloud závislosti
tokio = { version = "1.0", features = ["full"], optional = true }
tokio-tungstenite = { version = "0.20", optional = true }
hyper = { version = "0.14", features = ["full"], optional = true }
sqlx = { version = "0.7", features = ["postgres", "runtime-tokio-rustls"], optional = true }

# ESP32 závislosti
esp-idf-hal = { version = "0.42", optional = true }
embedded-svc = { version = "0.25", optional = true }
nb = { version = "1.0", optional = true }

# MCP závislosti
rust-mcp-schema = { version = "0.1", default-features = false }

[build-dependencies]
anyhow = "1.0"

[target.'cfg(target_arch = "xtensa")'.dependencies]
esp-idf-sys = { version = "0.33" }

[profile.release]
opt-level = "s"  # Optimalizace na velikost pro ESP32
lto = true
strip = true

[profile.dev]
debug = true
opt-level = 1
```

## Použití skriptů

```bash
# 1. Build pro ESP32
./scripts/build_esp32.sh

# 2. Flash na zařízení
./scripts/flash_esp32.sh /dev/ttyUSB0

# 3. Monitor výstup
cargo run --bin monitor -- --port /dev/ttyUSB0

# 4. Build a flash v jednom kroku
./scripts/build_esp32.sh && ./scripts/flash_esp32.sh
```