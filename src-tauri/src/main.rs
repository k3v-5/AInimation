// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

#[tauri::command]
fn get_orchestrator_status() -> String {
    "FastMCP Orchestrator Ready - UE5 Remote Control Port 30010".to_string()
}

#[tauri::command]
fn get_cas_storage_path() -> String {
    let home = std::env::var("USERPROFILE").unwrap_or_else(|_| ".".to_string());
    format!("{}/.cache/ianimation/cas", home)
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            get_orchestrator_status,
            get_cas_storage_path
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
