# Myr data bundle specification

The words MUST, SHOULD, MUST NOT, SHOULD NOT and MAY follow [RFC2119](https://datatracker.ietf.org/doc/html/rfc2119).

For examples of the specification, see the [examples](example) folder.

## Definitions
- **Data bundle**: a folder on disk containing data and metadata.
- **Metadata file**: a JSON file containing metadata about the data bundle, present in the data bundle.
- **Specification**: a JSON object containing the specification of the metadata file.
- **Data File**: Any file in the data bundle other than the metadata file. MUST be in the data bundle.
- **Frozen metadata file**: a metadata file in a frozen data bundle.
- **Frozen data bundle**: a data bundle that has been archived in a single file for long term storage.
- **JSON payload**: The topmost JSON object in the metadata file or the frozen metadata file.

## File specifications
The following sections describe the structure of the data bundle, the metadata file, the frozen data bundle, the frozen metadata file and the specification file.

### Data bundle
- The data bundle MUST be a folder containing at least one metadata file.
- The data bundle MAY contain any number of data files.

### Metadata file
- The metadata file MUST be a JSON, UTF-8 encoded file.
- The metadata file MUST be named `metadata.json`.
- The metadata file MUST be in the root of the data bundle.
- Each data bundle MUST contain at most one metadata file.
- The metadata file MUST contain a valid JSON object, the JSON payload.

### The JSON payload
- Each key in the JSON payload MUST adhere to one of the following patterns:
    - `KEY`, where `KEY` is a valid JSON string. This key will be referred to as "simple".
    - `>KEY`, where `KEY` is a valid JSON string. This key will be referred to as "relative".
    - `@KEY`, where `KEY` is a valid JSON string. This key will be referred to as "remote".
- The value of a simple key MUST be either a valid JSON value, another JSON object, or a JSON array of JSON values or JSON objects.
- The value of a remote key MUST be an absolute URL.
- Remote keys' URLs MUST point to a valid JSON file that can be retrieved by following the URL.
- Each JSON object MUST have the `type` key. Its value MUST be a valid JSON string.
- Each JSON object MAY have the `id` key. Its value MUST be a valid JSON string. If an `id` is specified, it MUST be globally unique in the JSON payload, at every level.
    - Clarification: this means that, if you take **every** `id` key in every object at every level of the JSON payload, they MUST all have different values.
    - This will include remote keys (with @) too, at freezing time. Keep this in mind when you fetch remote keys, and when you define new `id` keys. Using a UUID as an `id` is a good idea.
- The `id` and `type` keys MUST be simple.
- The value of relative keys MUST be a valid JSON string, and MUST be the same of one `id` key in the same JSON object.
- The top-level object MUST have a `type` of `"myr-bundle"`.
- The top-level object MUST have a `specification` key with a valid specification (see below).
    - The `specification` key MAY be a remote key (`@specification`).
    - The `@specification` key MAY be a list of URLs. If it is, the resultnig specification is the sum of the retrieved specifications created by combining the respective `keys` and `types` lists into a new list each.
        - Note how the various `id`s of the summed specifications must still be universally unique.

### Frozen data bundle
- The frozen data bundle MUST be a `.tar.gz` file with at least one frozen metadata file in it.

### Frozen metadata file
The frozen metadata follows all the rules of the metadata file, with the following additions:
- The remote or relative keys must be resolved to their actual value.

### Specification object
- The specification object MUST contain the following keys:
    - `types`: a JSON list of JSON objects, where each object is a type specification.
    - `keys`: a JSON list of JSON objects, where each object is a key specification.
- Each type specification MUST contain the following keys:
    - `qualifier`: a valid JSON string. This will be the value of the `type` key in the metadata file.
    - `description`: a valid JSON string. The human-readable description of the type.
    - `valid_keys`: a JSON list of JSON objects, where each object MUST have the following structure:
        - `qualifier`: A valid JSON string. This MUST be one `qualifier` value in one key specification.
        - `required`: A valid JSON boolean. If `true`, the key MUST be present in the metadata file's usage of this type. If `false`, the key MAY be present instead.
- Each key specification MUST contain the following keys:
    - `qualifier`: a valid JSON string.
    - `description`: a valid JSON string. The human-readable description of the key. MAY be an URL to a human-readable description (for example, a schema.org specification).
    - `value`: The type of value for the key. It MUST fall into one of the following categories:
        - `text`: The key MUST specify a valid JSON string.
        - `TYPE`: A valid `TYPE` value in the `types` list. The key MUST specify a valid JSON object with that `type`.
        - `any`: The key MAY specify any valid JSON value.
- Each key specification MAY contain the following keys:
    - `valid_values`: a JSON list of valid JSON values. If present, the value of the key MUST be one of the values in the list.
- Each specification MUST have at least one type, the `myr-bundle` type.
    - The `myr-bundle` type MUST have as qualifier the string `"myr-bundle"`.
    - The `myr-bundle` type MUST specify at least one valid key, with the qualifier `"content"` and `required` set to `true`.
- Each specification MUST have at least one key, the `content` key.
    - The `content` key MUST have as qualifier the string `"content"`.
    - The `content` key MUST specify as value the string `"any"`.
    - The `content` key MAY specify anything as `description`, but it SHOULD specify "the content of the bundle".

## Observations

Some observations about the above specification:
- There is no mention of specifying keys in objects that are not covered by the specification. You can add as many or as few keys as you want, as long as the keys that are covered by the specification are valid. This means that you can add keys that are not covered by the specification, but they will be ignored by any tool that reads the metadata file.
- There is no limit on which keys may be shallow (with just one value) or lists (with multiple values). For this reason, some keys may behave weirdly:
    - Any key, like `author`, may be interpreted freely in its plural form. So `author` may instead by a list of authors (but the key must still be just `author`, singular).
    - The `valid_values` filter effectively makes the value shallow, as it must be just one of the (shallow) values in the list.
    - Some keys make sense only as lists, like `content` in the example above. Some keys make sense only as shallow values, like `path` in the example above. How to interpret lists on keys that make sense only as shallow values and vice-versa is up to the end-user: read the meaning of the key and come up with a sensible interpretation.
- You can have URLs in non-remote keys, but they will be interpreted as strings. This means that you can still cite `schema.org` or whatever other site you want, but it will be just for human consumption.
- You need to have a remote specification, i.e. `@specification`. You can just declare a `specification`, and write it locally. This is fine, but having the specification as remote can allow easier reuse.
- Since the bundle is self-contained, versioning is irrelevant: everything is in the bundle, so you can just archive it and forget about it.
- There is not limit of the top-level keys in a metadata file. These keys can be used to describe the data bundle as a whole, and not just the content of the data bundle. You just need to declare valid keys in the specification (under the `bundle` type). This is to allow for maximum flexibility.
- In theory, one can specify any key for any meaning. However, specifying keys with common meaning is encouraged, as it allows for easier reuse. Using keys from things like `schema.org` may be a good idea.
- You could create a specification that is identical to RO-Crate, with all of its keys and values. However, note that such a specification must be self-contained: links to the outside meaning of each key is allowed, but a frozen specification must be self-contained and understandable just from what is locally contained in the specification.
- You need not connect to the internet to validate a frozen data bundle: the specification is in the bundle, and the specification is self-contained. The bundle is therefore self-validating.
- The frozen metadata file will probably be very verbose. This is a sacrifice I'm willing to make: the frozen metadata file is the one that is archived, and it is the one that is used by any tool that needs to read the metadata. It is therefore important that it is self-contained and that it is easy to read and understand, even years from now, after `version 2.3.1` of some remote specification has been forgotten.
- There is no specific way to check if the value of a key is actually what the key meant. For example, the object:
  ```json
  {
    "author": {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "orcid": "0000-0000-0000-0000"
    }
  }
  ```
  is perfectly OK, but so is this:
  ```json
  {
    "author": {
        "name": "022212-blurb?",
        "email": "something that is not an email",
        "orcid": "a string that is not an ORCID"
    }
  }
  ```
  So, the actual values of the keys will not be checked. Why? It's way too hard to come up with a way to check the values of the keys. For example, take the `ORCID` key. You could check it against a regex, but what if the user specifies another object instead? What if you find a list of values? Or a list of orcids? It might be that - for some obscure reason - that person actually has two valid ORCID identifiers. So, the value of the key is not checked. It is up to the end-user to check the values of the keys, if they want to. The specification only assure that an `author` has the keys `name`, `email` and `orcid`. It does not say anything about the values of these keys.
  It is up to the packager to specify the values in a sensible way, and it is up to the end-user to check the values if they want to.


This last point is debatable. One may say that checking the values of every key is essential for this to be an useful specification. I both agree and disagree with this. If you write every little detail in the specification, you might end up with something that is unusable by both a machine and a man. If you say too little, however, you end up with something that is too flexible and that is not useful. I think that the above specification is a good compromise between the two. It is flexible enough to be useful, but it is also strict enough to be machine-readable and parseable.

I'm sure this will be a point of contention, so I'm open to discussion.
