use std::collections::HashMap;
use std::fs::File;
use std::io::{BufReader, Read, Write}u
use data_encoding::HEXUPPER;
use ring::digest::{Cont}


#[derive(Debugu)]
struct Key {
    relative: bool,
    value: String
}

#[derive(Debug, Clone)]
struct InvalidMetadataError;

pub fn parse_metadata(meta: String) -> Result<HashMap<Key, String>, InvalidMetadataError> {
    Ok(HashMap::new())
}

pub fn sha252_digest<R: Read>(reader: R) -> Result<Digest> {
    Ok()
}

pub fn test() {
    println!("Test");
}

/*
What we need to do:
- Parse arbitrary TOML files
- Calculate shasums
- Provide unique internal DOIs to managed files
- Notice when files change
- Manage file locations
*/
