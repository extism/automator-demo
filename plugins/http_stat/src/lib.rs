#![no_main]

use extism_pdk::*;
use serde::{Serialize, Deserialize};
use std::time::{Instant};

#[derive(Serialize)]
struct TriggerArgument {
    name: String,
    description: String,
    r#type: String,
}

#[derive(Serialize)]
struct Trigger {
    name: String,
    description: String,
    arguments: Vec<TriggerArgument>,
}

#[derive(Serialize)]
struct PluginMetadata {
    name: String,
    r#type: String,
    poll_time: u32,
    triggers: Vec<Trigger>,
}

#[derive(Serialize)]
struct Stats {
    url: String,
    time_ms: u32,
    resolved: bool
}

#[derive(Deserialize)]
struct Payload {
    url: String
}

#[function]
pub unsafe fn get_metadata(_: ()) -> FuncResult<Json<PluginMetadata>> {
    let metadata = PluginMetadata {
        name: "http_stat".to_string(),
         r#type: "service".to_string(),
         poll_time: 10000, // every 10 seconds
         triggers: vec![
            Trigger{
                name: "check".to_string(),
                description: "Checks the url given and publishes the stats".to_string(),
                arguments: vec![
                    TriggerArgument{
                        name: "url".to_string(),
                        description: "The url to check".to_string(),
                        r#type: "string".to_string(),
                    }
                ]
            },
         ],
    };
    
    Ok(Json(metadata))
}

#[function]
pub unsafe fn check(Json(payload): Json<Payload>) ->  FuncResult<Json<Stats>> {
    let req = HttpRequest::new(payload.url.clone());
    let now = Instant::now();
    let _res = http::request::<()>(&req, None).unwrap();

    let stats = Stats{
        url: payload.url,
        time_ms: (now.elapsed().as_secs() * 1000) as u32,
        resolved: true
    };

    Ok(Json(stats))
}