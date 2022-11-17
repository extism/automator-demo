#![no_main]

use extism_pdk::*;
use serde::Serialize;

#[derive(Serialize)]
struct ActionArgument {
    name: String,
    description: String,
    r#type: String,
}

#[derive(Serialize)]
struct Action {
    name: String,
    description: String,
    arguments: Vec<ActionArgument>,
}

#[derive(Serialize)]
struct PluginMetadata {
    name: String,
    r#type: String,
    actions: Vec<Action>,
}

#[function]
pub unsafe fn get_metadata(_: ()) -> FuncResult<Json<PluginMetadata>> {
    let metadata = PluginMetadata {
        name: "echo".to_string(),
        r#type: "action".to_string(),
        actions: vec![
           Action{
               name: "print_to_stdout".to_string(),
               description: "Print to standard out".to_string(),
               arguments: vec![
                ActionArgument{
                    name: "input".to_string(),
                    description: "The line to print to the output".to_string(),
                    r#type: "string".to_string(),
                }
               ]
           },
        ],
    };

    Ok(Json(metadata))
}

#[function]
pub unsafe fn print_to_stdout(data: String) -> FuncResult<()> {
    println!("{}", data);
    Ok(())
}
