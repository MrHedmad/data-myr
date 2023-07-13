use std::{path::Path, fs::File, error::Error, io::Read};
use serde_json::Value;
use reqwest;


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

fn resolve(object: Value) -> Result<Value, Box<dyn Error>> {
    let resolved_object = match object {
        Value::Object(map) => {
            let mut resolved_map = serde_json::Map::new();
            for (key, value) in map {
                if key.starts_with("@") {
                    let url = value.as_str().ok_or("Expected a string.")?;
                    let resolved_value = fetch_remote(url.to_string())?;
                    resolved_map.insert(key.trim_start_matches("@").to_string(), resolve(resolved_value)?);
                } else {
                    resolved_map.insert(key, resolve(value)?);
                }
            }
            Value::Object(resolved_map)
        },
        Value::Array(array) => {
            let mut resolved_array = Vec::new();
            for value in array {
                let resolved_value = resolve(value)?;
                resolved_array.push(resolved_value);
            }
            Value::Array(resolved_array)
        },
        _ => object,
    };

    Ok(resolved_object)
}

#[cfg(test)]
mod tests {
    use serde_json::json;
    use super::*;

    #[test]
    fn test_resolve() {
    let object = json!({
        "@specification": "https://gist.githubusercontent.com/MrHedmad/541007818984a54a79eaf7cf15c24e2c/raw/ff2d630e1d4bd2e07076f2b3e0300ac687e20169/test_json.json",
        "test": {
            "foo": "bar",
            "@baz": "https://gist.githubusercontent.com/MrHedmad/541007818984a54a79eaf7cf15c24e2c/raw/ff2d630e1d4bd2e07076f2b3e0300ac687e20169/test_json.json",
        },
    });

    let resolved_object = resolve(object).unwrap();

    println!("{}", serde_json::to_string_pretty(&resolved_object).unwrap());

    assert_eq!(resolved_object, json!({
        "specification": {
            "hello": "hello.txt"
        },
        "test": {
            "foo": "bar",
            "baz": {
                "hello": "hello.txt",
            },
        },
    }));
    }
}
