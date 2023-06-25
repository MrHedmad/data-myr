# Mimir

Solve locally saving files with FAIR metadata and structure.

## The idea
- Save local config in `mimir.toml`
- The data proper is stored in some other folder, specified in `mimir.toml`.
- Each data file must have an universally unique name.
- The metadata is stored in `.mimir`.
- Allow "remote" data (as a link?), to integrate with remote databases.
- Each file is linked with metadata in `.toml` format.
- Each metadata/data blob is an `artifact`.
- Metadata is a series of `fields`:
    - The `type` field is in every data. Represents what the data is.
        - E.g. `expression_matrix`, `metadata_table`, `protocol`, `specification`, etc...
    - Fields that start with an `@` represent other artifacts with that type.
        - E.g. `@specification: sam.txt` points to a file named `sam.txt` with `type: specification` somewhere in the file tree.
        - E.g. `@protocol: imaging_protocol_1.md` points to `imaging_protocol_1.md`
        - These links can be used to reuse information from other files.
    - All other fields are simple metadata fields. They do not link to anything else, but are just there to describe the data.
        - E.g. `date: 2023-01-30`
- Internally, mimir saves hashes of the files that it tracks, in the `.mimir` folder. The metadata is also saved in `.mimir`.
- `mimir` has no state, all depending on what is in `.mimir`, like `git`.

## Example

Assume this is the data:
```
,s1,s2,s3
gene1,1,2,1
gene2,0.2,0,1.3
gene3,1.3,0,2.5
```

The config might look like this:
```toml
type = "expression_matrix"

@specification = "expression_matrix_specification.md"
@column_descriptors = "experiment_1.csv"
date = 2023-01-30
```

Mimir will warn that there is no such thing as a `sam.txt` file with the `specification` type, or the `experiment_1.csv` file with the `column_descriptor` type. If those file are included:

```
# In expression_matrix_specification.md
An expression matrix is a numerical matrix with genes as rows and samples as columns.
The first row has column names, the first column has row names.

# In experiment_1.csv
column,description
s1,Sample one
s2,Sample two
s3,Sample three
```

And the respective configurations:
```toml
# For expression_matrix_specification.md
type = "specification"
created_by = "Someone important"

# For experiment_1.csv
type = "column_descriptor"
```

The idea is that you can go as deep as you need to, and reuse the things that you need. The result is a network of data that describes itself.
