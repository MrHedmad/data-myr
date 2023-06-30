use std::error::Error;
use std::fmt;

#[derive(Debug, PartialEq)]
pub struct Descriptor {
    relative: bool,
    key: String,
    value: String,
}

#[derive(Debug, PartialEq)]
pub struct Metadata {
    type_string: String,
    file_path: Option<String>,
    other_keys: Vec<Descriptor>,
}

#[derive(Debug, Clone)]
pub enum InvalidMetadataError {
    MissingTypeAnnotation,
    InvalidFileAnnotation(String),
    InvalidKey(String),
}

impl fmt::Display for InvalidMetadataError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match &self {
            Self::InvalidFileAnnotation(reason) => write!(f, "Invalid file annotation: {}", reason),
            Self::MissingTypeAnnotation => write!(f, "Missing Type annotation."),
            _ => todo!(),
        }
    }
}

impl Error for InvalidMetadataError {}

pub fn parse_metadata(meta: String) -> Result<Metadata, InvalidMetadataError> {
    let iter = meta
        .split("\n")
        .into_iter()
        .map(|x| x.split("=").collect::<Vec<&str>>());

    let keys = iter.map(|x| {
        let key = x.get(0).unwrap().to_owned().trim();
        let value = x.get(1).unwrap().to_owned().trim();

        Descriptor {
            value: value.to_string(),
            key: key.strip_prefix("@").unwrap_or(key).to_string(),
            relative: key.starts_with("@"),
        }
    });

    let type_desc = keys
        .clone()
        .into_iter()
        .find(|x| x.key == "type")
        .ok_or(InvalidMetadataError::MissingTypeAnnotation)?;

    let file_desc = keys.clone().into_iter().find(|x| x.key == "file");

    Ok(Metadata {
        type_string: type_desc.value,
        file_path: file_desc.map(|x| x.value.to_string()),
        other_keys: keys
            .clone()
            .filter(|x| ! ((x.key == "type") | (x.key == "file")))
            .collect(),
    })
}

// ----------------------------------------------------------------------------

pub fn test() {
    let meta_string = "type =   data\nfile  =  /path/to/file    \n  test =   test1 \n  banana=fruit".to_string();

    println!("{:?}", parse_metadata(meta_string))
}

#[cfg(test)]
mod tests {
    use crate as mimir;

    #[test]
    fn test_parsing() {
        let meta_string = "type =   data\nfile  =  /path/to/file    \n  test =   test1 \n  @banana=fruit".to_string();

        let result = mimir::parse_metadata(meta_string).unwrap();

        assert_eq!(result,
        mimir::Metadata{
            file_path: Some("/path/to/file".to_string()),
            type_string: "data".to_string(),
            other_keys: vec![
                mimir::Descriptor{
                    key: "test".to_string(),
                    value: "test1".to_string(),
                    relative: false
                },
                mimir::Descriptor{
                    key: "banana".to_string(),
                    value: "fruit".to_string(),
                    relative: true
                }
            ]
        })
    }
}
