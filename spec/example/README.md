# Example myr data bundle

This is a tiny example of a myr data bundle. It contains this file, and a few others. Just like RO-crate, you start by making a `myr-metadata.json` file.

The [specification](spec/specification.md) tells you that you have to specify two keys, `type` equalling `myr-bundle` and `specification` with a valid specification. Let's write those down.

```json
{
    "type": "myr-bundle",
    "specification": {
        ...
    }
}
```

Now, we have to make `specification` a valid specification. Turning to the specification section of the specification (ok, I'll stop, sorry), we see that it must be a json object with two keys:
- `types`: a list of valid types;
- `keys`: a list of valid keys.

We also read that we must specify the `myr-bundle` type, so let's do that:
``` json
{
    "type": "myr-bundle",
    "specification": {
        "types": [
            {
                "qualifier": "myr-bundle",
                "valid_keys": [
                    {
                        "qualifier": "content",
                        "required": true
                    }
                ]
            }
        ],
        "keys": [
            {
                "qualifier": "content",
                "value": "any",
                "description": "The content of the bundle."
            }
        ]
    }
}
```

Notice how we are describing ourselves. The root object has `type` equal to `myr-bundle`, and the `specification` object has `types` and `keys` that describe the `myr-bundle` type.

The only special thing of the root JSON object is that it has a `specification` key. In every other aspect, it is just like any other object.

You can also notice how we are violating our specification! The root object is missing the `content` key, and it is required. Let's add it.

```json
{
    "type": "myr-bundle",
    "specification": {
        "types": [
            {
                "qualifier": "myr-bundle",
                "valid_keys": [
                    {
                        "qualifier": "content",
                        "required": true
                    }
                ]
            }
        ],
        "keys": [
            {
                "qualifier": "content",
                "value": "any",
                "description": "The content of the bundle."
            }
        ]
    },
    "content": {
        ...
    }
}
```

Now, we just have to define what `content` is. In this case, we can look at the description of that key, and see that it is "the content of the bundle".
Since this very file is in the bundle, we can add it to the list. However, we don't have any `types` that can describe a file! Let's add that first:
    
```json
{
    "type": "myr-bundle",
    "specification": {
        "types": [
            {
                "qualifier": "myr-bundle",
                "valid_keys": [
                    {
                        "qualifier": "content",
                        "required": true
                    }
                ]
            },
            {
                "qualifier": "file",
                "valid_keys": [
                    {
                        "qualifier": "path",
                        "required": true
                    },
                    {
                        "qualifier": "MIME_type",
                        "required": true
                    },
                    {
                        "qualifier": "author",
                        "required": false
                    },
                    {
                        "qualifier": "date",
                        "required": false
                    }

                ] 
            }
        ],
        "keys": [
            {
                "qualifier": "content",
                "value": "any",
                "description": "The content of the bundle."
            },
            {
                "qualifier": "path",
                "value": "text",
                "description": "The path to the file."
            },
            {
                "qualifier": "MIME_type",
                "value": "text",
                "description": "The MIME type of the file.",
                "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types"
            },
            {
                "qualifier": "author",
                "value": "text",
                "description": "The author of the file."
            },
            {
                "qualifier": "date",
                "value": "text",
                "description": "The date the file was created."
            }
        ]
    },
    "content": [
        ...
    ]
}
```
We've added the `file` type and its keys:
- `path`: the path to the file;
- `MIME_type`: the MIME type of the file;
- `author`: the author of the file;
- `date`: the date the file was created.
And these are all text values.

We're now ready to add this file to the bundle:

```json
{
    "type": "myr-bundle",
    "specification": {
        / --- SNIP --- /
    },
    "content": [
        {
            "type": "file",
            "path": "README.md",
            "MIME_type": "text/markdown",
            "author": "Luca Visentin",
            "date": "2021-01-01"
        }
    ]
}
```

And that's it! We've created a valid myr data bundle. We could stop here, call it a day, get a coffee, and be happy with ourselves. But we're not going to do that, because we're going to expand the specification a bit more.

I'm also not going to get coffee, because it's late and I'm not a coffee person. I'm more of a tea person. But I digress.

## Expanding the specification

Now, the `author` being just `"Luca Visentin"` might be a bit reductive. There are surely a ton of "Luca Visentin"s out there, and we might want to specify which one we are talking about. We can do that, just by expanding the specification:
```json
    "type": "myr-bundle",
    "specification": {
        "types": [
            / --- SNIP --- /
            {
                "qualifier": "person",
                "valid_keys": [
                    {
                        "qualifier": "name",
                        "required": true
                    },
                    {
                        "qualifier": "email",
                        "required": false
                    },
                    {
                        "qualifier": "ORCID",
                        "required": false
                    }
                ]
            }
        ],
        "keys": [
            / --- SNIP --- /
            {
                "qualifier": "author",
                "value": "person",
                "description": "The author of the file."
            },
            {
                "qualifier": "name",
                "value": "text",
                "description": "The name of a real person."
            },
            {
                "qualifier": "email",
                "value": "text",
                "description": "An e-mail address."
            },
            {
                "qualifier": "ORCID",
                "value": "text",
                "description": "An ORCID id."
            }
        ]
    },
    "content": [
        {
            "type": "file",
            "path": "README.md",
            "MIME_type": "text/markdown",
            "author": {
                "type": "person",
                "name": "Luca Visentin",
                "ORCID": "0000-0003-2568-5694"
            },
            "date": "2021-01-01"
        }
    ]
```

And that's it! Let's say that the file was made by multiple people. We can just add them to the list:

```json
{
    "type": "myr-bundle",
    "specification": {
        / --- SNIP --- /
    },
    "content": [
        {
            "type": "file",
            "path": "README.md",
            "MIME_type": "text/markdown",
            "author": [
                {
                    "type": "person",
                    "name": "Luca Visentin",
                    "ORCID": "0000-0003-2568-5694"
                },
                {
                    "type": "person",
                    "name": "Jane Doe",
                }
            ],
            "date": "2021-01-01"
        }
    ]
}
```

Notice how Jane has no email or ORCID. That's because they are not required, and we can just omit them. It's also because she does not exist!

You can expand or contract the specification as much as you want to.

## Using remote keys
Even with a small example, you can see that the JSON tends to become pretty large pretty fast. That's where relative and remote keys come in handy.

We can write our specification and store it somewhere on the internet. Let's say we have a remote file with URL `http://some_awesome_specification.org/spec.json`. If the url points to the same specification as above, we can just drop it in instead:
    
```json
{
    "type": "myr-bundle",
    "@specification": "http://some_awesome_specification.org/spec.json",
    "content": [
        {
            "type": "file",
            "path": "README.md",
            "MIME_type": "text/markdown",
            "author": [
                {
                    "type": "person",
                    "name": "Luca Visentin",
                    "ORCID": "0000-0003-2568-5694"
                },
                {
                    "type": "person",
                    "name": "Jane Doe",
                }
            ],
            "date": "2021-01-01"
        }
    ]
}
```

Note that `specification` became `@specification`.

Now, let's say that the author of many files is the same. It is a bother to always have to re-write the same thing over and over again. We can just use a relative key:

```json
{
    "type": "myr-bundle",
    "@specification": "http://some_awesome_specification.org/spec.json",
    "content": [
        {
            "type": "file",
            "path": "README.md",
            "MIME_type": "text/markdown",
            "author": [
                {
                    "id": "0000-0003-2568-5694",
                    "type": "person",
                    "name": "Luca Visentin",
                    "ORCID": "0000-0003-2568-5694"
                },
                {
                    "type": "person",
                    "name": "Jane Doe",
                }
            ],
            "date": "2021-01-01"
        },
        {
            "type": "file",
            "path": "LICENSE",
            "MIME_type": "text/plain",
            ">author": "0000-0003-2568-5694",
            "date": "2021-01-01"
        }
    ]
}
```

Note how in the second file we used `>author` instead of `author`. This means that the value of `author` is the same as the value of `author` in the object with `id` equal to `0000-0003-2568-5694`. This is a relative key. Since there must be only one object with that `id`, the value of `author` is unambiguous, and we have to specify it only once.

Note that Jane has no `id`. No object has to have an `id`, but it has to if we want to have relative keys pointing to it.

The order of the files does not matter, as long as the object with `id` equal to `0000-0003-2568-5694` is defined somewhere.

Having relative and remote links allows us to write very compact JSON files, and to avoid repeating ourselves. When the package is frozen they will be inflated and resolved to their full form, so that any tool that has to parse the file will not have to deal with them.
