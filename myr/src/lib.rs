#![allow(dead_code)]
use reqwest;
use serde_json::Value;
use std::{collections::HashMap, error::Error, fs::File, io::Read, path::Path};

pub fn new_bundle_at(path: &Path) {
    println!("Creating new data bundle at {:?}", path);

    todo!("Implement new.");
}

pub fn validate_bundle_at(path: &Path) {
    println!("Validating data bundle at {:?}", path);

    let file = match File::open(path.join("myr-metadata.json")) {
        Ok(file) => file,
        Err(error) => panic!("Problem opening file: {:?}", error),
    };

    let object: Value = match serde_json::from_reader(file) {
        Ok(object) => object,
        Err(error) => panic!("Problem reading file: {:?}", error),
    };

    match validate(object) {
        Ok(_) => println!("Bundle is valid."),
        Err(error) => panic!("Bundle is invalid: {:?}", error),
    }
}

pub fn freeze_bundle_at(path: &Path) {
    println!("Freezing data bundle at {:?}", path);

    todo!("Implement freeze.");
}

fn validate(object: Value) -> Result<Value, Box<dyn Error>> {
    match object {
        Value::Object(map) => {
            let specification = map.get("specification").ok_or("Missing specification.")?;
            let objects = map.get("").ok_or("Missing objects.")?;
        }
        _ => return Err("Expected a top-level object.".into()),
    }
    todo!("Implement validate.")
}

fn fetch_remote(url: String) -> Result<Value, Box<dyn Error>> {
    let mut remote = reqwest::blocking::get(url)?;
    let mut body = String::new();
    remote.read_to_string(&mut body)?;

    let object: Value = serde_json::from_str(&body)?;

    Ok(object)
}

fn resolve_remote(object: Value) -> Result<Value, Box<dyn Error>> {
    let resolved_object = match object {
        Value::Object(map) => {
            let mut resolved_map = serde_json::Map::new();
            for (key, value) in map {
                if key.starts_with("@") {
                    let url = value.as_str().ok_or("Expected a string.")?;
                    let resolved_value = fetch_remote(url.to_string())?;
                    resolved_map.insert(
                        key.trim_start_matches("@").to_string(),
                        resolve_remote(resolved_value)?,
                    );
                } else {
                    resolved_map.insert(key, resolve_remote(value)?);
                }
            }
            Value::Object(resolved_map)
        }
        Value::Array(array) => {
            let mut resolved_array = Vec::new();
            for value in array {
                let resolved_value = resolve_remote(value)?;
                resolved_array.push(resolved_value);
            }
            Value::Array(resolved_array)
        }
        _ => object,
    };

    Ok(resolved_object)
}

fn extract_objects(object: Value) -> Vec<Value> {
    let mut objects: Vec<Value> = Vec::new();

    let object = object.as_object().expect("Expected an object.").to_owned();

    for (_, value) in object {
        match value {
            Value::Object(_) => {
                objects.push(value.clone());
                objects.extend(extract_objects(value));
            }
            Value::Array(array) => {
                for value in array {
                    if value.is_object() {
                        objects.push(value.clone());
                        objects.extend(extract_objects(value));
                    }
                }
            }
            _ => {}
        }
    }
    objects
}

fn strip_id(value: Value) -> Value {
    match value {
        Value::Object(mut map) => {
            map.remove("id");
            Value::Object(map)
        }
        _ => value,
    }
}

fn resolve_relative(
    object: Value,
    objects_map: Option<HashMap<String, Value>>,
) -> Result<Value, Box<dyn Error>> {
    // Get out all the ID keys
    let objects_map = objects_map.unwrap_or({
        let objects: Vec<Value> = extract_objects(object.clone())
            .into_iter()
            .filter(|x| x.get("id").is_some())
            .collect();

        let mut object_map: HashMap<String, Value> = HashMap::new();
        for value in objects {
            let id = value.get("id").unwrap().as_str().unwrap().to_string();
            object_map.insert(id, value);
        }

        object_map
    });

    // We can now do something like `resolve_remote`, just replacing relative
    // IDs with the objects above.
    let resolved_object = match object {
        Value::Object(map) => {
            let mut resolved_map = serde_json::Map::new();
            for (key, value) in map {
                match value {
                    Value::Object(_) => {
                        resolved_map
                            .insert(key, resolve_relative(value, Some(objects_map.clone()))?);
                    }
                    Value::Array(array) => {
                        let mut resolved_array = Vec::new();
                        for value in array {
                            let resolved_value =
                                resolve_relative(value, Some(objects_map.clone()))?;
                            resolved_array.push(resolved_value);
                        }
                        resolved_map.insert(key, Value::Array(resolved_array));
                    }
                    Value::String(ref id) => {
                        if key.starts_with(">") {
                            let resolved_value = match objects_map.get(id) {
                                Some(value) => strip_id(value.to_owned()),
                                None => {
                                    return Err(
                                        format!("Could not find object with ID {}.", id).into()
                                    )
                                }
                            };
                            resolved_map.insert(
                                key.trim_start_matches("@").to_string(),
                                resolve_relative(resolved_value, Some(objects_map.clone()))?,
                            );
                        } else {
                            resolved_map.insert(key, value);
                        }
                    }
                    _ => {
                        resolved_map.insert(key, value);
                    }
                }
            }
            Value::Object(resolved_map)
        }
        Value::Array(array) => {
            let mut resolved_array = Vec::new();
            for value in array {
                let resolved_value = resolve_relative(value, Some(objects_map.clone()))?;
                resolved_array.push(resolved_value);
            }
            Value::Array(resolved_array)
        }
        _ => object,
    };

    Ok(resolved_object)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_resolve_remote() {
        let object = json!({
            "@specification": "https://gist.githubusercontent.com/MrHedmad/541007818984a54a79eaf7cf15c24e2c/raw/ff2d630e1d4bd2e07076f2b3e0300ac687e20169/test_json.json",
            "test": {
                "foo": "bar",
                "@baz": "https://gist.githubusercontent.com/MrHedmad/541007818984a54a79eaf7cf15c24e2c/raw/ff2d630e1d4bd2e07076f2b3e0300ac687e20169/test_json.json",
            },
        });

        let resolved_object = resolve_remote(object).unwrap();

        assert_eq!(
            resolved_object,
            json!({
                "specification": {
                    "hello": "hello.txt"
                },
                "test": {
                    "foo": "bar",
                    "baz": {
                        "hello": "hello.txt",
                    },
                },
            })
        );
    }

    #[test]
    fn test_extract_objects() {
        let object = json!({
            "foo": "bar",
            "baz": {
                "hello": "world",
            },
            "test": [
                {
                    "id": "test",
                    "foo": "bar",
                },
                {
                    "id": "test2",
                    "foo": "bar",
                },
            ],
            "ber": {
                "id": "testtt",
                "foo": "bull"
            }
        });

        let objects = extract_objects(object);

        // TODO: This is a bit fragile since the order counts. Unsure if rust
        // has a way to compare two arrays without caring about order, but
        // good enough for now.
        assert_eq!(
            objects,
            vec![
                json!({"hello": "world"}),
                json!({
                    "id": "testtt",
                    "foo": "bull"
                }),
                json!({
                    "id": "test",
                    "foo": "bar",
                }),
                json!({
                    "id": "test2",
                    "foo": "bar",
                }),
            ]
        );
    }

    #[test]
    fn test_resolve_relative() {
        let object = json!({
            "foo": "bar",
            "baz": {
                ">hello": "testtt",
            },
            "test": [
                {
                    "id": "test",
                    "foo": "bar",
                },
                {
                    "id": "test2",
                    "foo": "testtt",
                },
            ],
            "ber": {
                "id": "testtt",
                "foo": "bull"
            },
            ">test2": "testtt",
        });

        let resolved_object = resolve_relative(object, None).unwrap();

        assert_eq!(
            resolved_object,
            json!({
                "foo": "bar",
                "baz": {
                    ">hello": {
                        "foo": "bull"
                    }
                },
                "test": [
                    {
                        "id": "test",
                        "foo": "bar",
                    },
                    {
                        "id": "test2",
                        "foo": "testtt",
                    },
                ],
                "ber": {
                    "id": "testtt",
                    "foo": "bull"
                },
                ">test2": {
                    "foo": "bull"
                },
            })
        );
    }
}
