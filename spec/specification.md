# Data Myr Specification

The words MUST, SHOULD, MUST NOT, SHOULD NOT and MAY follow [RFC2119](https://datatracker.ietf.org/doc/html/rfc2119).

## Rationale

The idea is to specify a format to package data and metadata together. 
[Research Object crate (RO-Crate)](https://www.researchobject.org/ro-crate/) is a way to do this but:
- There is no RO-Crate validator. So it's up to the packager to get it right.
    - They provide a Python package that makes RO-crates but I question its usefulness. Why does it exist? The actual people who would need to write these RO-crate metadata are not programmers.
- It does not (look like, to me) that it is widely accepted as a standard.
- It boils down to a simple set of words-to-definitions, i.e. schema.org + bioschema.org + other vocabularies.
- It **needs** to be scaled down with so-called profiles to be useful.
- Profile enforcement is still not a thing.
    - But without a validator, how would you enforce it?
- It has a lot of boilerplate:
    - Do you really need an entry for the root folder?
    - Do you really need an entry for the metadata file itself?
- It should be usable and writable by anyone, even without any (and I mean any) knowledge of how computers work.

### What is wrong with catch-all specifications
I more generally feel like RO-crate and similar specifications fail at being *usable*.
The JSON format and the specification is fine and dandy, but specifications are *for humans*, not solely for machines.

Take a step back. FAIR data should be machine-readable, and for this:
- It must be in a *semantic* format that machines understand (and we get this for free by writing JSON).
- Its content must be structured identically between different data bundles.

RO-crate - in theory - fixes both, but the key thing to notice is that the second point above gives no meaning to the "structure".
If my JSON metadata were to be:

```json
{
    "id": "000111222",
    "banana": "Yes"
}
```
And the same schema is used by all my data bundles, any tool could easily fetch the JSON, read it, and see that the `N` different data bundles have these `N` different `id` values, and that there are many values for the key `banana`.

But the idea is that a human will sooner or later have to read the specification and implement something that reads it.
Stating that "the content structure must be shared" means nothing without a manual.

RO-crate wants to be that manual, but it actually isn't: it's a place where other standard get linked in (mostly from schema.org).
It's fine to want to be a cover-all specification but if you bit off more than you can chew, it's hard then to actually follow through with useful tools.

I feel like something like RO-crate (and probably RO-crate itself) will be the future standard, but for the reasons above I cannot see myself or my team adopting it.

For this reason, I think we can take the general idea of RO-crate and simplify it quite a bit:
- Fix the structure of the metadata file (like RO-crate does).
    - I.e. the `"@id"`, `@type` keywords having special meaning, etc...
- Produce the custom "profile" - in this case a schema - first, specific for a use-case.
    - This kind of profile should be readable by a machine and a human, and a machine that reads it should be perfectly capable to then digest any other file that follows the specification and check its validity.
- Refer to the above schema in each metadata file.
- Make it easy enough to write it down in a text file and then pass it to some tool / person that will then produce the actual metadata file.
- Allow some more fluidity and ease-of-use for the working-copy of the metadata, but then enforce the schema when the data bundle is actually created.

I think that the above is a good compromise between usability and machine-readability.

The idea is to do a three-step process:
1. The wet-lab user writes down the metadata in a simple format, like a text file or a spreadsheet, or a piece of paper.
2. This simple format is then formalized in a working-copy of the metadata file, which is flexible and easy to use, but still somewhat structured.
3. Upon archiving the data bundle, the working-copy is then converted to a frozen metadata file, which is then archived with the data bundle. This frozen copy is then the one that is used by any tool that needs to read the metadata: it is guaranteed to be valid and to follow the specification.

# Myr

Following is the above but coalesced into something actionable.

## Myr specifications - core

### Definitions
- **Data bundle**: a folder containing data and metadata.
- **Metadata file**: a JSON file containing metadata about the data bundle.
- **Specification**: a JSON file containing the specification of the metadata file.
- **Data File**: Any file in the data bundle other than the metadata file.
- **Frozen metadata file**: a metadata file that has been archived.
- **Frozen data bundle**: a data bundle that has been archived in a single file.

Those are the only things that are defined in the specification. See the following sections for the rules governing them.

### Data bundle structure
- The data bundle MUST be a folder containing at least one metadata file and any other files.

### Metadata file structure
- The metadata file MUST be a JSON, UTF-8 encoded file.
- The metadata file MUST be named `metadata.json`.
- The metadata file MUST be in the root of the data bundle.
- Each data bundle may contain at most one metadata file.

Regarding the content of the metadata file:
- The metadata file MUST contain a valid JSON object. See the JSON specification for what a valid JSON object is.
- Each key in the JSON payload MUST be one of the following:
    - `KEY`, where `KEY` is a valid JSON string. This key will be referred to as "simple".
    - `@KEY`, where `KEY` is a valid JSON string. This key will be referred to as "relative".
    - `>KEY`, where `KEY` is a valid JSON string. This key will be referred to as "remote".
- The value of a simple key MUST be either a valid JSON value, another JSON object, or a JSON array of JSON values or JSON objects.
- The value of a remote key MUST be an absolute URL.
- Remote keys URL MUST point to a valid JSON file that can be retrieved by following the URL.
- Each JSON object MUST have the following keys:
    - `id`: a valid JSON string. The value of this key MUST be globally unique, meaning that for every `id` key, regardless of depth, its value must be different from any other `id` key.
    - `type`: a valid JSON string.`
- The `id` key MUST be a simple key.
- The `type` key MAY be a simple key, a relative key, or a remote key.
- The value of relative keys MUST be a valid JSON string, and MUST be the same of one and only one `id` key in the same JSON object.
- The top-level object MUST additionally contain the following keys:
    - `specification`: a specification JSON object.
    - `content`: a JSON array of JSON objects, where each object is a file in the data bundle.

An example `metadata.json` file following the specification is as follows:
```json
{
    "id": "my_data_bundle",
    "type": "DataBundle",
    "@specification": "https://example.com/specification.json",
    "content": [
        {
            "id": "experimental_data",
            "type": "DataFile",
            "path": "./my_data_file.txt",
        }
    ]
}
```

### Frozen data bundle structure
- The frozen data bundle MUST be a `.tar.gz` file with at least one frozen metadata file in it.

### Frozen metadata file structure
The frozen metadata follows all the rules of the metadata file, with the following additions:
- The remote or relative keys must be resolved to their actual value.

### Specification file structure
The specification file MUST be a JSON file, and MUST follow the following rules:
- The specification file MUST contain a valid JSON object. See the JSON specification for what a valid JSON object is.
- The specification file MUST contain the following keys:
    - `version`: a valid JSON string representing the SEMVER version of the specification.
    - `types`: a JSON list of JSON objects, where each object is a type specification.
    - `keys`: a JSON list of JSON objects, where each object is a key specification.
- Each type specification MUST contain the following keys:
    - `qualifier`: a valid JSON string. This will be the value of the `type` key in the metadata file.
    - `description`: a valid JSON string. The human-readable description of the type.
    - `valid_keys`: a JSON list of JSON objects, where each object MUST have the following structure:
        - `qualifier`: A valid JSON string. This MUST be one `qualifier` value in key specification.
        - `required`: A valid JSON boolean. If `true`, the key MUST be present in the metadata file's usage of this type. If `false`, the key MAY be present instead.
        - `structure`: Either "shallow", "list" or "object_list". If "shallow", the value of the key MUST be a valid JSON value. If "list", the value of the key MUST be a JSON array of valid JSON values. If "object_list", the value of the key MUST be a JSON array of JSON objects.
- Each key specification MUST contain the following keys:
    - `qualifier`: a valid JSON string.
    - `description`: a valid JSON string. The human-readable description of the key. MAY be an URL to a human-readable description (for example, a schema.org specification).

An example specification:
```json
{
    "version": "1.0.0",
    "types: [
        {
            "qualifier": "DataBundle",
            "description": "A collection of data and metadata.",
            "valid_keys": [
                {
                    "qualifier": "content",
                    "required": true
                }
            ]
        },
        {
            "qualifier": "DataFile",
            "description": "A file containing data.",
            "valid_keys": [
                {
                    "qualifier": "path",
                    "required": true
                },
                {
                    "qualifier": "author",
                    "required": false
                },
                {
                    "qualifier": "fileType",
                    "required": false
                }
            ]
        }
    ],
    "keys": {
        {
            "qualifier": "content",
            "description": "The content of the data bundle.",
            "structure": "object_list"
        },
        {
            "qualifier": "author",
            "description": "The author of the object.",
            "structure": "shallow"
        },
        {
            "qualifier": "fileType",
            "description": "The type of the file, following the MIME media type specification.",
            "structure": "shallow"
        },
        {
            "qualifier": "path",
            "description": "The path to the file, relative to the metadata file.",
            "structure": "shallow"
        }
    }
}
```
