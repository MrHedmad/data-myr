> **Important Note**: This project is still a WIP and therefore nothing is definitive. Please take a look at [the plan](https://github.com/MrHedmad/data-myr#the-plan) below. It is not recommended to use it for production work, but you are welcome to try it out and give feedback.

![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/MrHedmad/data-myr/python-package.yml?style=flat-square&logo=github)

# Data Myr
> We can't quite determine what they're doing, but they seem to be doing it quite well.
> — <cite> [Myr Galvanizer](https://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=220364) </cite>

A data myr is a simple way to locally manage data following [FAIR principles](https://www.go-fair.org/fair-principles/).

This is the Python implementation of `myr`, a tool to create, check and freeze
myr-data bundles. You can read about myr-data bundles in [mrhedmad/data-myr-spec](https://github.com/mrhedmad/data-myr-spec).

## Installation
You will need Python 3.10 +. Install data-myr with:
```bash
# Optional, but highly encouraged to install in a virtual environment
python -m venv env
source env/bin/activate
pip install @ git+https://github.com/mrhedmad/data-myr.git
```
If everything goes well, you can now use `myr`. Start with `myr --help`.

## Usage
`myr` is still under development. This section will be filled out when a sensible
version is realeased.

For now, you should **not** be using `myr`!

# Contributing
Contributions are welcome! Please open an issue or a pull request.
If you have comments or suggestions, please open an issue, I'd love to hear from you.

To contribute, [fork the repository](https://docs.github.com/en/get-started/quickstart/fork-a-repo),
then clone it locally with `git clone`. Once you do, you can setup your work
environment by running:
```bash
cd data-myr
python -m venv env
source env/bin/activate
pip install -r requirements_dev.txt
pre-commit install
pre-commit install -t commit-msg # Install the commit message hooks too!
pip install -e . # Install the package in editable form
```
You will now have `black` and other linters on commit, plus the ability to
run `pytest` to run the whole suite of tests.

You can look at [TODO issues](https://github.com/MrHedmad/data-myr/labels/todo)
for things that need to be implemented yet, or at all issues for things that
need fixing.

You can use `myr` in the virtual environment to test your changes immediately.

Please test that `pytest` checks pass before opening a pull request.

# License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
Please let me know if you use this project in your work, I'd love to hear about it!
