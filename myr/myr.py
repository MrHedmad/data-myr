import logging
from pathlib import Path
from typing import BinaryIO
import os
import json

log = logging.getLogger(__name__)

BASE_MYR_DATA = {
    "type": "myr-bundle",
    "specification": {
        "types": [
            {
                "qualifier": "myr-bundle",
                "valid_keys": [{"qualifier": "content", "required": True}],
                "description": "A bundle of data and metadata",
            }
        ],
        "keys": [
            {
                "qualifier": "content",
                "value": "any",
                "description": "The content of the bundle.",
            }
        ],
    },
    "content": [],
}


def myr_create(path: Path, overwrite: bool = False) -> None:
    log.debug(f"Invoked `myr_create` with {path}")
    if path.exists() and not overwrite:
        log.error(f"{path} exists! Will not overwrite. Pass --force to ignore.")
        return

    log.info(f"Creating new data-myr container @ {path}")
    if not path.exists():
        os.makedirs(path)
    with (path / "myr-metadata.json").open("w+") as stream:
        json.dump(BASE_MYR_DATA, stream, indent=4)


def myr_check_path(path: Path) -> None:
    log.debug(f"Invoked `myr_check` with {path}")
    raise NotImplementedError()


def myr_freeze(input_path: Path, output_path: Path) -> None:
    log.debug(
        f"Invoked `myr_freeze` with input - {input_path} - and output - {output_path}"
    )
    raise NotImplementedError()


def main() -> None:
    log.debug("Invoked myr")
    import argparse

    parser = argparse.ArgumentParser(
        prog="myr", description="Package your data in a FAIR way."
    )
    # This line is ignored as I set the verbosity in __init__.py
    # TODO: In theory I could import the same parser from __init__ and save
    # this line of code, but it seems a bit obscure. Consider it?
    parser.add_argument(
        "-v", "--verbose", action="count", help="increase verbosity", default=0
    )

    subparsers = parser.add_subparsers(dest="command", title="available commands")
    # `myr create` - sets up a new myr bundle
    create_cmd = subparsers.add_parser("create", help="create a new myr bundle.")
    create_cmd.add_argument(
        "path", default=".", type=Path, help="destination folder", nargs="?"
    )
    create_cmd.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="force creation, ignoring existing files",
    )

    # `myr check` - checks a myr bundle for validity
    check_cmd = subparsers.add_parser("check", help="check a myr bundle for validity.")
    check_cmd.add_argument(
        "path", default=".", type=Path, help="where to check", nargs="?"
    )

    # `myr freeze` - freezes a myr bundle
    freeze_cmd = subparsers.add_parser("freeze", help="freeze a myr bundle.")
    freeze_cmd.add_argument(
        "input_path", default=".", type=Path, help="bundle to freeze", nargs="?"
    )
    freeze_cmd.add_argument(
        "--output", default=None, type=Path, help="output frozen bundle filename"
    )

    args = parser.parse_args()
    log.debug(f"Parsed args: {args}")

    match args.command:
        case "create":
            myr_create(args.path.expanduser().resolve(), args.force)
        case "check":
            myr_check_path(args.path.expanduser().resolve())
        case "freeze":
            input_path = args.input_path.expanduser().resolve()
            outfile = (
                input_path.parent / f"{input_path.stem}.tar.gz"
                if args.output is None
                else args.output
            )
            myr_freeze(input_path, outfile)
        case _:
            parser.print_help()
