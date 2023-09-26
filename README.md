> **Important Note**: This project is still a WIP and therefore nothing is definitive. Please take a look at [the plan](https://github.com/MrHedmad/data-myr#the-plan) below. It is not recommended to use it for production work, but you are welcome to try it out and give feedback.

![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/MrHedmad/data-myr/python-package.yml?style=flat-square&logo=github)

# Data Myr
> The myr are like rusted metal: gleaming purpose hidden by a thin disguise of debris.
> — <cite> [Iron Myr](https://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=194168) </cite>

A data myr is a simple way to locally manage data following [FAIR principles](https://www.go-fair.org/fair-principles/).

## The idea

A myr **data bundle** is a folder with data and metadata inside.
It is in principle similar to [RO-Crate](https://www.researchobject.org/ro-crate/), but a lot simpler, so you can use it for your data *right now*.

It allows everyone to have their own metadata system, catered to their own need, while avoiding the need to learn a complex specification.

Ideally, everyone should follow a single, standardized metadata format, but it will take some time before such a format emerges and the community adopts it.
In the meantime, a lot of data is being produced, and a lot of it is wasted by not being even remotely FAIR.

You can use Myr to define a structure, perhaps for just your own lab, and uses it to manage your data.
Then, once (and if) a global standard is defined, you can migrate your data to that standard (in some way).

## The plan
Emoji key: 📅: Planned, 🚧: In progress, ✅: Done
- 🚧 Define a simple, self-contained metadata format.
- 📅 Implement a metadata validator for the format.
- 📅 Start using the format in our own work.
- 📅 Work out the kinks.

## The execution
- You can find examples of data myr in [examples/](examples/), so you can see if it's good for your use case.
- You can read about the format specification in [spec/README.md](spec/README.md).
- Read the formal specification [here](spec/specification.md).

# Contributing
Contributions are welcome! Please open an issue or a pull request. If you have comments or suggestions, please open an issue, I'd love to hear from you.

# License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
Please let me know if you use this project in your work, I'd love to hear about it!
