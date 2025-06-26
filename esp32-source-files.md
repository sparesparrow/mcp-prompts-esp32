# Klíčové zdrojové soubory pro mcp-prompts-rs ESP32

## src/embedded/main.rs

```rust
#![no_std]
#![no_main]

use esp_idf_hal::{
    gpio::*,
    peripherals::Peripherals,
    prelude::*,
    wifi::{AuthMethod, BlockingWifi, ClientConfiguration, Configuration, EspWifi},
};
use esp_idf_sys as _; // If using the `binstart` feature of `esp-idf-sys`, always keep this module imported

use crate::{
    api::websocket::EmbeddedWebSocketServer,
    storage::littlefs::LittleFsStorage,
    model::prompt::PromptManager,
    embedded::prompts::EMBEDDED_PROMPTS,
};

mod prompts; // Auto-generated prompts

const WIFI_SSID: &str = env!("WIFI_SSID");
const WIFI_PASS: &str = env!("WIFI_PASS");
const WS_PORT: u16 = 9000;

#[main]
async fn main() -> ! {
    // Initialize peripherals
    let peripherals = Peripherals::take().unwrap();
    let sys_loop = EspSystemEventLoop::take().unwrap();
    
    // Initialize WiFi
    let mut wifi = init_wifi(peripherals.modem, sys_loop).await;
    
    // Initialize storage
    let storage = LittleFsStorage::new("/data").await
        .unwrap_or_else(|_| {
            log::warn!("LittleFS nedostupný, používám embedded prompts");
            LittleFsStorage::embedded_only()
        });
    
    // Initialize prompt manager
    let mut prompt_manager = PromptManager::new(storage);
    
    // Load embedded prompts
    for prompt in EMBEDDED_PROMPTS {
        if let Err(e) = prompt_manager.add_prompt(prompt.clone()).await {
            log::warn!("Nepodařilo se načíst prompt {}: {}", prompt.id, e);
        }
    }
    
    // Start WebSocket server
    let mut ws_server = EmbeddedWebSocketServer::new(WS_PORT, prompt_manager);
    
    log::info!("🚀 MCP Prompts ESP32 server started on port {}", WS_PORT);
    log::info!("📡 WiFi IP: {:?}", wifi.sta_netif().get_ip_info().unwrap().ip);
    
    // Main loop
    loop {
        if let Err(e) = ws_server.handle_connections().await {
            log::error!("WebSocket error: {}", e);
            esp_idf_hal::delay::FreeRtos::delay_ms(1000);
        }
    }
}

async fn init_wifi(
    modem: impl esp_idf_hal::peripheral::Peripheral<P = esp_idf_hal::modem::Modem> + 'static,
    sys_loop: EspSystemEventLoop,
) -> BlockingWifi<EspWifi<'static>> {
    let mut esp_wifi = EspWifi::new(modem, sys_loop.clone(), None).unwrap();
    
    let mut wifi = BlockingWifi::wrap(&mut esp_wifi, sys_loop).unwrap();
    
    wifi.set_configuration(&Configuration::Client(ClientConfiguration {
        ssid: WIFI_SSID.into(),
        bssid: None,
        auth_method: AuthMethod::WPA2Personal,
        password: WIFI_PASS.into(),
        channel: None,
    })).unwrap();
    
    wifi.start().unwrap();
    log::info!("📶 WiFi started");
    
    wifi.connect().unwrap();
    log::info!("📶 WiFi connected");
    
    wifi.wait_netif_up().unwrap();
    log::info!("📶 WiFi netif up");
    
    wifi
}
```

## src/api/websocket.rs

```rust
use crate::model::{prompt::PromptManager, schema::McpMessage};

#[cfg(feature = "std")]
use tokio_tungstenite::{accept_async, WebSocketStream};

#[cfg(feature = "embedded")]
use esp_idf_hal::{
    tcp::{TcpListener, TcpStream},
    io::{Read, Write},
};

pub struct WebSocketServer<S> {
    port: u16,
    prompt_manager: PromptManager<S>,
}

#[cfg(feature = "std")]
impl<S> WebSocketServer<S> 
where 
    S: crate::storage::Storage + Send + Sync + 'static
{
    pub fn new(port: u16, prompt_manager: PromptManager<S>) -> Self {
        Self { port, prompt_manager }
    }
    
    pub async fn start(&self) -> Result<(), Box<dyn std::error::Error>> {
        let addr = format!("0.0.0.0:{}", self.port);
        let listener = tokio::net::TcpListener::bind(&addr).await?;
        
        println!("🌐 WebSocket server listening on {}", addr);
        
        while let Ok((stream, _)) = listener.accept().await {
            let prompt_manager = self.prompt_manager.clone();
            tokio::spawn(async move {
                if let Err(e) = handle_connection(stream, prompt_manager).await {
                    eprintln!("Connection error: {}", e);
                }
            });
        }
        
        Ok(())
    }
}

#[cfg(feature = "embedded")]
pub struct EmbeddedWebSocketServer<S> {
    port: u16,
    prompt_manager: PromptManager<S>,
    listener: Option<TcpListener>,
}

#[cfg(feature = "embedded")]
impl<S> EmbeddedWebSocketServer<S>
where
    S: crate::storage::Storage
{
    pub fn new(port: u16, prompt_manager: PromptManager<S>) -> Self {
        Self {
            port,
            prompt_manager,
            listener: None,
        }
    }
    
    pub async fn handle_connections(&mut self) -> Result<(), esp_idf_hal::io::EspIOError> {
        if self.listener.is_none() {
            self.listener = Some(TcpListener::bind(("0.0.0.0", self.port))?);
            log::info!("🌐 Embedded WebSocket server listening on port {}", self.port);
        }
        
        if let Some(ref listener) = self.listener {
            if let Ok(stream) = listener.accept() {
                if let Err(e) = self.handle_single_connection(stream.0).await {
                    log::error!("Connection error: {:?}", e);
                }
            }
        }
        
        Ok(())
    }
    
    async fn handle_single_connection(&self, mut stream: TcpStream) -> Result<(), esp_idf_hal::io::EspIOError> {
        // Simplified WebSocket-like protocol for ESP32
        let mut buffer = [0u8; 1024];
        
        loop {
            match stream.read(&mut buffer) {
                Ok(0) => break, // Connection closed
                Ok(n) => {
                    let request = core::str::from_utf8(&buffer[..n])
                        .map_err(|_| esp_idf_hal::io::EspIOError::from_raw_os_error(22))?;
                    
                    if let Ok(response) = self.process_mcp_request(request).await {
                        stream.write_all(response.as_bytes())?;
                    }
                }
                Err(e) => {
                    log::error!("Read error: {:?}", e);
                    break;
                }
            }
        }
        
        Ok(())
    }
    
    async fn process_mcp_request(&self, request: &str) -> Result<String, Box<dyn core::error::Error>> {
        // Parse JSON-RPC request
        if let Ok(mcp_msg) = serde_json::from_str::<McpMessage>(request) {
            match mcp_msg {
                McpMessage::ListPrompts => {
                    let prompts = self.prompt_manager.list_prompts().await?;
                    Ok(serde_json::to_string(&prompts)?)
                }
                McpMessage::GetPrompt { id } => {
                    let prompt = self.prompt_manager.get_prompt(&id).await?;
                    Ok(serde_json::to_string(&prompt)?)
                }
                _ => Ok(r#"{"error": "Unsupported method"}"#.to_string())
            }
        } else {
            Ok(r#"{"error": "Invalid JSON-RPC"}"#.to_string())
        }
    }
}

#[cfg(feature = "std")]
async fn handle_connection<S>(
    raw_stream: tokio::net::TcpStream, 
    prompt_manager: PromptManager<S>
) -> Result<(), Box<dyn std::error::Error>>
where 
    S: crate::storage::Storage + Send + Sync
{
    let ws_stream = accept_async(raw_stream).await?;
    let (mut ws_sender, mut ws_receiver) = ws_stream.split();
    
    use futures_util::{SinkExt, StreamExt};
    use tokio_tungstenite::tungstenite::Message;
    
    while let Some(message) = ws_receiver.next().await {
        match message? {
            Message::Text(text) => {
                if let Ok(mcp_msg) = serde_json::from_str::<McpMessage>(&text) {
                    let response = process_mcp_message(mcp_msg, &prompt_manager).await?;
                    ws_sender.send(Message::Text(response)).await?;
                }
            }
            Message::Close(_) => break,
            _ => {}
        }
    }
    
    Ok(())
}

#[cfg(feature = "std")]
async fn process_mcp_message<S>(
    message: McpMessage, 
    prompt_manager: &PromptManager<S>
) -> Result<String, Box<dyn std::error::Error>>
where 
    S: crate::storage::Storage + Send + Sync
{
    match message {
        McpMessage::ListPrompts => {
            let prompts = prompt_manager.list_prompts().await?;
            Ok(serde_json::to_string(&prompts)?)
        }
        McpMessage::GetPrompt { id } => {
            let prompt = prompt_manager.get_prompt(&id).await?;
            Ok(serde_json::to_string(&prompt)?)
        }
        McpMessage::ApplyTemplate { id, variables } => {
            let result = prompt_manager.apply_template(&id, &variables).await?;
            Ok(serde_json::to_string(&result)?)
        }
    }
}
```

## src/storage/littlefs.rs

```rust
#[cfg(feature = "embedded")]
use esp_idf_hal::{
    io::{Read, Write},
    fs::{File, OpenOptions},
};

use crate::model::prompt::Prompt;
use crate::storage::Storage;

#[cfg(feature = "embedded")]
pub struct LittleFsStorage {
    root_path: String,
    embedded_only: bool,
}

#[cfg(feature = "embedded")]
impl LittleFsStorage {
    pub async fn new(root_path: &str) -> Result<Self, esp_idf_hal::io::EspIOError> {
        // Try to initialize LittleFS
        match Self::init_littlefs(root_path) {
            Ok(_) => {
                log::info!("✅ LittleFS initialized at {}", root_path);
                Ok(Self {
                    root_path: root_path.to_string(),
                    embedded_only: false,
                })
            }
            Err(e) => {
                log::warn!("⚠️ LittleFS init failed: {:?}", e);
                Err(e)
            }
        }
    }
    
    pub fn embedded_only() -> Self {
        Self {
            root_path: String::new(),
            embedded_only: true,
        }
    }
    
    fn init_littlefs(root_path: &str) -> Result<(), esp_idf_hal::io::EspIOError> {
        // ESP-IDF LittleFS mounting logic
        use esp_idf_sys::{
            esp_vfs_littlefs_conf_t,
            esp_vfs_littlefs_register,
            ESP_OK,
        };
        
        let conf = esp_vfs_littlefs_conf_t {
            base_path: root_path.as_ptr() as *const i8,
            partition_label: b"storage\0".as_ptr() as *const i8,
            format_if_mount_failed: true,
            dont_mount: false,
        };
        
        let result = unsafe { esp_vfs_littlefs_register(&conf) };
        
        if result == ESP_OK {
            Ok(())
        } else {
            Err(esp_idf_hal::io::EspIOError::from_raw_os_error(result))
        }
    }
}

#[cfg(feature = "embedded")]
impl Storage for LittleFsStorage {
    type Error = esp_idf_hal::io::EspIOError;
    
    async fn get_prompt(&self, id: &str) -> Result<Option<Prompt>, Self::Error> {
        if self.embedded_only {
            // Fallback to embedded prompts
            use crate::embedded::prompts::get_prompt_by_id;
            Ok(get_prompt_by_id(id).cloned())
        } else {
            let file_path = format!("{}/prompts/{}.json", self.root_path, id);
            
            match File::open(&file_path) {
                Ok(mut file) => {
                    let mut contents = String::new();
                    file.read_to_string(&mut contents)?;
                    
                    match serde_json::from_str::<Prompt>(&contents) {
                        Ok(prompt) => Ok(Some(prompt)),
                        Err(_) => Ok(None),
                    }
                }
                Err(_) => {
                    // Fallback to embedded
                    use crate::embedded::prompts::get_prompt_by_id;
                    Ok(get_prompt_by_id(id).cloned())
                }
            }
        }
    }
    
    async fn list_prompts(&self) -> Result<Vec<Prompt>, Self::Error> {
        if self.embedded_only {
            use crate::embedded::prompts::list_prompts;
            Ok(list_prompts().to_vec())
        } else {
            // TODO: Read from LittleFS directory
            // Pro teď vrátíme embedded prompts
            use crate::embedded::prompts::list_prompts;
            Ok(list_prompts().to_vec())
        }
    }
    
    async fn save_prompt(&self, prompt: &Prompt) -> Result<(), Self::Error> {
        if self.embedded_only {
            // Read-only mode
            return Err(esp_idf_hal::io::EspIOError::from_raw_os_error(30)); // EROFS
        }
        
        let file_path = format!("{}/prompts/{}.json", self.root_path, prompt.id);
        let prompt_json = serde_json::to_string_pretty(prompt)
            .map_err(|_| esp_idf_hal::io::EspIOError::from_raw_os_error(22))?; // EINVAL
        
        let mut file = OpenOptions::new()
            .write(true)
            .create(true)
            .truncate(true)
            .open(&file_path)?;
        
        file.write_all(prompt_json.as_bytes())?;
        file.sync_all()?;
        
        Ok(())
    }
    
    async fn delete_prompt(&self, id: &str) -> Result<bool, Self::Error> {
        if self.embedded_only {
            return Ok(false); // Read-only
        }
        
        let file_path = format!("{}/prompts/{}.json", self.root_path, id);
        
        match std::fs::remove_file(&file_path) {
            Ok(_) => Ok(true),
            Err(_) => Ok(false),
        }
    }
}
```

## .cargo/config.toml

```toml
[target.xtensa-esp32s3-none-elf]
runner = "espflash flash --monitor"

[build]
target = "xtensa-esp32s3-none-elf"

[unstable]
build-std = ["std", "panic_abort"]

[env]
ESP_IDF_VERSION = { value = "v5.3.3" }
ESP_IDF_TOOLS_INSTALL_DIR = { value = "global" }
WIFI_SSID = { value = "YourWiFiNetwork" }
WIFI_PASS = { value = "YourWiFiPassword" }
```

## build.rs

```rust
fn main() {
    // ESP32-specific build configuration
    if cfg!(target_arch = "xtensa") {
        // ESP-IDF build settings
        embuild::build::CfgArgs::output_propagated("ESP_IDF")?;
        embuild::build::LinkArgs::output_propagated("ESP_IDF")?;
        
        // Flash layout
        println!("cargo:rustc-link-arg=-Tlinkall.x");
        println!("cargo:rustc-link-arg=-Trom_functions.x");
        
        // Memory optimization
        println!("cargo:rustc-env=ESP_IDF_SDKCONFIG_DEFAULTS=sdkconfig.defaults");
    }
    
    // Feature-based conditional compilation
    if cfg!(feature = "embedded") && !cfg!(feature = "std") {
        println!("cargo:rustc-cfg=embedded_build");
    }
    
    Ok(())
}
```

## Použití

```bash
# 1. Instalace ESP toolchainu
cargo install espup
espup install
source ~/export-esp.sh

# 2. Build embedded verze
cargo build --target xtensa-esp32s3-none-elf --features embedded,no-std --release

# 3. Flash na ESP32
esptool.py --chip esp32s3 elf2image -o firmware.bin target/xtensa-esp32s3-none-elf/release/mcp-prompts-rs
esptool.py --port /dev/ttyUSB0 write_flash 0x0 firmware.bin

# 4. Test připojení
# ESP32 vytvoří WiFi hotspot nebo se připojí k síti
# MCP klient se připojí na ws://[ESP32_IP]:9000
```