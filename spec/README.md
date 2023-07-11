# The Myr specification

This directory contains the specification for Myr bundles.
You can find it in [specification.md](specification.md).

The `myr` command line tool is the reference implementation of the specification.
It provides the following functionality:
- It reads a `myr` bundle and prints its contents.
- It can check a `myr` bundle for violations of the specification.
- It can create a frozen `myr` bundle from a directory.

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
- It is not self-contained. Every package has links to remote resources. What if the links die? What if the link content changes?

### What is wrong with catch-all specifications
I more generally feel like RO-crate and similar specifications fail at being *usable*.
The JSON format and the specification is fine and dandy, but specifications are *for humans*, not solely for machines.

Take a step back. FAIR data should be machine-readable, and for this:
- It must be in a *semantic* format that machines understand (and we get this for free by writing JSON).
- Its content must be structured identically between different data bundles.
    - This means that a specification has been written somewhere that defines the structure of the content, and everyone follows it.

RO-crate - in theory - specifies both points, but the key thing to notice is that the second point above gives no specific meaning to the "structure".
The key observation is that a human will sooner or later have to read the specification and implement something that parses it.
Stating that "the content structure must be shared" means nothing without a manual.

RO-crate wants to be that manual. It takes keywords defined elsewhere and glues them all together. The main problem in that it is so *bloated*.
It's fine to want to be a cover-all specification but if you bite off more than you can chew, it's hard then to actually follow through with useful tools.

I feel like something like RO-crate (and probably RO-crate itself) will be the future standard, but for the reasons above I cannot see myself or my team adopting it right now.

### My proposal

For this reason, I think we can take the general idea of RO-crate and simplify it quite a bit:
- Fix the structure of the metadata file (like RO-crate does).
- Produce the custom "profile" - in this case a schema - first, specific for a use-case.
    - This kind of profile should be readable by a machine and a human, and a machine that reads it should be perfectly capable to then digest any other file that follows the specification and check its validity.
    - It would be perfectly OK, and even best practice, to use a standard vocabulary like schema.org, but the key thing is that the profile should be self-contained and locally specified.
- Refer to the above schema in each metadata file, so that an automatic checker can find the specification.
- Make it easy enough so that you could write it down in a text file and then pass it to some tool / person that will then produce the actual metadata file.
- Allow some more fluidity and ease-of-use for the working-copy of the metadata, but then enforce the schema when the data bundle is actually created.

I think that the above is a good compromise between usability and machine-readability.

The idea is to do a three-step process:
1. The wet-lab user writes down the metadata in a simple format, like a text file or a spreadsheet, or a piece of paper.
    - This format is decided earlier with the data manager, and is specific to the use-case.
    - One could have a set of formats for every experiment type, or even for every experiment. It would be up to the data manager and the wet-lab user to decide.
2. This simple format is then formalized in a working-copy of the metadata file, which is flexible and easy to use, but still somewhat structured.
    - The working copy is, well, a working copy. It might be malformed, use remote resources, or be otherwise invalid.
    - It should be easy to edit and to read.
3. Upon archiving the data bundle, the working-copy is then converted to a frozen metadata file, which is then archived with the data bundle. This frozen copy is then the one that is used by any tool that needs to read the metadata: it is guaranteed to be valid and to follow the specification.
  If the working copy of the metadata is not valid, the tool that converts it to the frozen copy MUST fail and MUST not allow a frozen copy to be created.
  It is also completely self-contained, so that even when the original schema changes, or the world ends, you still have the meaning of the specific metadata file on hand.

Myr aims to:
- Be simple to write, simpler than RO-Crate;
- Be self-contained, when the package is published, every metadata is in the metadata file.
- Avoid being too verbose, otherwise readers will not be able to easily understand what the metadata is trying to say.

