COMPLEX_MYR_DATA = {
    "type": "myr-bundle",
    "specification": {
        "types": [
            {
                "qualifier": "myr-bundle",
                "description": "A bundle of data and metadata",
                "valid_keys": [{"qualifier": "content", "required": True}],
            },
            {
                "qualifier": "file",
                "description": "A file on disk",
                "valid_keys": [
                    {"qualifier": "path", "required": True},
                    {"qualifier": "MIME_type", "required": True},
                    {"qualifier": "author", "required": False},
                    {"qualifier": "date", "required": False},
                ],
            },
            {
                "qualifier": "person",
                "description": "A real person",
                "valid_keys": [
                    {"qualifier": "name", "required": True},
                    {"qualifier": "email", "required": False},
                    {"qualifier": "ORCID", "required": False},
                ],
            },
        ],
        "keys": [
            {
                "qualifier": "content",
                "value": "any",
                "description": "The content of the bundle.",
            },
            {
                "qualifier": "path",
                "value": "text",
                "description": "The path to the file.",
            },
            {
                "qualifier": "MIME_type",
                "value": "text",
                "description": "The MIME type of the file.",
                "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types",
            },
            {
                "qualifier": "author",
                "value": "text",
                "description": "The author of the file.",
            },
            {
                "qualifier": "date",
                "value": "text",
                "description": "The date the file was created.",
            },
            {
                "qualifier": "author",
                "value": "person",
                "description": "The author of the file.",
            },
            {
                "qualifier": "name",
                "value": "text",
                "description": "The name of a real person.",
            },
            {
                "qualifier": "email",
                "value": "text",
                "description": "An e-mail address.",
            },
            {"qualifier": "ORCID", "value": "text", "description": "An ORCID id."},
        ],
    },
    "content": [
        {
            "type": "file",
            "path": "README.md",
            "MIME_type": "text/markdown",
            "author": {
                "type": "person",
                "name": "Luca Visentin",
                "ORCID": "0000-0003-2568-5694",
            },
            "date": "2023-07-11",
        }
    ],
}
