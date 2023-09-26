import pytest
from myr.checker import Specification

def test_test():
    assert True

BASE_MYR_DATA = {
    "type": "myr-bundle",
    "specification": {
        "types": [
            {
                "qualifier": "myr-bundle",
                "valid_keys": [{"qualifier": "content", "required": True}],
                "description": "A bundle of data and metadata."
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

def test_minimal_specification():
    spec = Specification(BASE_MYR_DATA["specification"])
