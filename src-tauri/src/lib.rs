use std::sync::{Arc, Mutex};

use tauri::Manager;
use tauri_plugin_shell::ShellExt;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            let (mut _rx, sidecar_child) = app
                .shell()
                .sidecar("stream")
                .expect("Failed to setup 'camera' sidecar")
                .spawn()
                .expect("Failed to spawn packed flask");
            println!("Starting...");

            let child = Arc::new(Mutex::new(Some(sidecar_child)));
            let child_clone = Arc::clone(&child);
            let window = app.get_webview_window("main").unwrap();

            window.on_window_event(move |event| {
                if let tauri::WindowEvent::CloseRequested { .. } = event {
                    let mut child_lock = child_clone.lock().unwrap();
                    if let Some(child_process) = child_lock.take() {
                        let _ = ureq::get("http://localhost:9928/shutdown").call();
                        if let Err(e) = child_process.kill() {
                            eprintln!("Failed to kill child process: {}", e);
                        }
                    }
                }
            });

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
