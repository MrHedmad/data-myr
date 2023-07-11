# Mimir

A way to locally manage data in a FAIR way.

## The idea

The idea is to have a folder with data and metadata inside, just like RO-crate, but in a thinner, more self-contained and simpler way.

It would allow everyone to have their own metadata system, catered to their own need. If you want to follow a more centralized, structured method, you can implement and use RO-crate, but it seems to me that it is too much for most people.

Ideally, everyone should follow a single, standardized metadata format, but this is not going to happen anytime soon. So, the idea is to locally define a structure, perhaps for just your own lab, and use it to manage your data.
Then, once (and if) a global standard is defined, you can migrate your data to that standard (in some way).

## The plan
- [ ] Define a simple, self-contained metadata format.
- [ ] Implement a metadata validator for the format.
- [ ] Start using the format in my own work.
- [ ] ???
- [ ] Profit

## The format
You can read about the format specification in [spec/README.md](spec/README.md).
