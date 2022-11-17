#![no_main]

use extism_pdk::*;
use serde::Serialize;
use std::{thread, time};

#[derive(Serialize)]
struct Trigger {
    name: String,
    description: String,
}

#[derive(Serialize)]
struct PluginMetadata {
    name: String,
    r#type: String,
    poll_time: u32,
    triggers: Vec<Trigger>,
}

#[function]
pub unsafe fn get_metadata(_: ()) -> FuncResult<Json<PluginMetadata>> {
    let metadata = PluginMetadata {
        name: "cron".to_string(),
         r#type: "service".to_string(),
         poll_time: 0, // 0 ms, these actions block
         triggers: vec![
            Trigger{
                name: "every_second".to_string(),
                description: "Triggers every second".to_string(),
            },
            Trigger{
                name: "every_minute".to_string(),
                description: "Triggers every minute".to_string(),
            },
         ],
    };
    
    Ok(Json(metadata))
}

#[function]
pub unsafe fn every_second(_: ()) -> FuncResult<String> {
    thread::sleep(time::Duration::from_secs(1));
    Ok("It happened from the plugin 1 second timer".to_string())
}

#[function]
pub unsafe fn every_minute(_: ()) -> FuncResult<String> {
    thread::sleep(time::Duration::from_secs(3));
    Ok("It happened from the plugin 3 second timer".to_string())
}