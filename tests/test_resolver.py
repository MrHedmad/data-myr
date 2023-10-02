import pytest
from myr.resolver import *
from copy import deepcopy


@pytest.fixture
def test_data():
    data = {
        "test_0": {"id": "wow", "a": "a", "b": {"id": "wow2", "something": "else"}},
        "test_1": {"nested": {"id": "amazing", "fad": "fred"}},
        ">relative": "wow",
        "list": [
            {"id": "list1", "abba": "good music"},
            {"proton": "exists"},
            {">listrel": "wow"},
        ],
    }
    return deepcopy(data)


def test_purge_ids(test_data):
    expected_data = {
        "test_0": {"a": "a", "b": {"something": "else"}},
        "test_1": {"nested": {"fad": "fred"}},
        ">relative": "wow",
        "list": [{"abba": "good music"}, {"proton": "exists"}, {">listrel": "wow"}],
    }

    assert purge_id_keys(test_data) == expected_data


def test_find_ids(test_data):
    expected_data = {
        "wow": {"a": "a", "b": {"something": "else"}},
        "wow2": {"something": "else"},
        "amazing": {"fad": "fred"},
        "list1": {"abba": "good music"},
    }

    assert find_ids(test_data) == expected_data


def test_resolve_relative(test_data):
    expected_data = {
        "test_0": {"id": "wow", "a": "a", "b": {"id": "wow2", "something": "else"}},
        "test_1": {"nested": {"id": "amazing", "fad": "fred"}},
        "relative": {"a": "a", "b": {"something": "else"}},
        "list": [
            {"id": "list1", "abba": "good music"},
            {"proton": "exists"},
            {"listrel": {"a": "a", "b": {"something": "else"}}},
        ],
    }

    ids = find_ids(test_data)
    assert resolve_relative(test_data, ids) == expected_data
