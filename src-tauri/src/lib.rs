use tauri_plugin_shell::ShellExt;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            let handle = app.handle().clone();
            tauri::async_runtime::spawn(async move {
                let (mut _rx, mut _child) = handle
                    .shell()
                    .sidecar("stream")
                    .expect("Failed to setup 'camera' sidecar")
                    .spawn()
                    .expect("Failed to spawn packed flask");
                println!("Starting...")
            });
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
