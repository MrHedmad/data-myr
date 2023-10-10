import logging
import requests
import sys
import json
from copy import copy
from functools import reduce
from myr.checker import check_parsing_validity

log = logging.getLogger(__name__)


def fuse_specifications(left, right) -> dict:
    # Test if the two specifications are at least usable
    check_parsing_validity(left)
    check_parsing_validity(right)

    new_specification = {}
    new_specification["types"] = left["types"]
    new_specification["types"].extend(right["types"])
    new_specification["keys"] = left["keys"]
    new_specification["keys"].extend(right["keys"])

    return new_specification

def retrieve_json(url) -> dict:
    try:
        response = requests.get(url=url)
    except requests.exceptions.RequestException as e:
        log.exception(f"Failed to retrieve data from {value}: {e}")
        sys.exit(1)

    try:
        decoded_data = json.loads(response.content)
    except json.JSONDecodeError as e:
        log.exception(f"Content of the pointed URL was not valid JSON: {e}")

    return decoded_data


def resolve_remote(structure: dict) -> dict:
    """Resolve remote (@) keys to local keys"""

    new_data: dict = {}
    for key, value in structure.item():
        if not key.startswith("@"):
            if isinstance(value, dict):
                value = resolve_remote(value)
            new_data[key] = value
            continue

        new_key = key.strip("@")

        if new_key == "specification":
            # Edge case: specifications could be lists of URLs
            if isinstance(value, list):
                retrieved_data = [retrieve_json(x) for x in value]
                decoded_data = reduce(fuse_specifications, retrieved_data)

        if not isinstance(value, str):
            raise ValueError(f"Invalid value for remote key '@{new_key}': {value}")

        decoded_data = retrieve_json(value)
        # Ok, we successfully got our new data, now let's resolve it too
        decoded_data = resolve_remote(decoded_data)

        new_data[new_key] = decoded_data

    return new_data


class DuplicatedIDError(ValueError):
    """Raised when duplicated IDs are found in the data"""
    pass


def purge_id_keys(structure: dict) -> dict:
    new_dict = {}
    for key, value in structure.items():
        if key == "id":
            continue
        if isinstance(value, dict):
            value = purge_id_keys(value)
        if isinstance(value, list):
            value = [purge_id_keys(x) for x in value]
        new_dict[key] = value
    return new_dict


def find_ids(structure: dict, ids: dict = {}):
    ids = copy(ids)
    log.debug(f"Finding ids in {structure} with starting ids {ids}")
    for key, value in structure.items():
        if isinstance(value, dict):
            ids.update(find_ids(value, ids))
            continue
        if isinstance(value, list):
            for item in value:
                ids.update(find_ids(item, ids))
            continue
        if key != "id":
            continue
        if structure["id"] in ids:
            raise DuplicatedIDError(
                f"Id {structure['id']} was found twice in the data."
            )

        ids[structure["id"]] = purge_id_keys(structure)

    return ids


def resolve_relative(structure: dict, ids: dict) -> dict:
    # Enumerate the IDs
    resolved = {}
    for key, value in structure.items():
        if isinstance(value, dict):
            resolved[key] = resolve_relative(value, ids)
            continue
        if isinstance(value, list):
            resolved[key] = [resolve_relative(x, ids) for x in value]
            continue
        if not key.startswith(">"):
            resolved[key] = value
            continue

        new_key = key.strip(">")
        try:
            resolved[new_key] = ids[value]
        except KeyError:
            log.exception(f"Key {new_key} maps to id {value} but no such ID was found.")
            raise KeyError
    return resolved
