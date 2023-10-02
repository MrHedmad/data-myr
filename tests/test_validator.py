import pytest
from myr.checker import *
from tests.data import COMPLEX_MYR_DATA
import logging

root_logger = logging.getLogger("myr")
for handler in root_logger.handlers:
    handler.setLevel(logging.DEBUG)


def test_test():
    assert True


BASE_MYR_DATA = {
    "type": "myr-bundle",
    "specification": {
        "types": [
            {
                "qualifier": "myr-bundle",
                "valid_keys": [{"qualifier": "content", "required": True}],
                "description": "A bundle of data and metadata.",
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


def test_complex_specification():
    spec = Specification(COMPLEX_MYR_DATA["specification"])


def test_violation_ordering():
    crit = ViolationSeverity.CRITICAL
    error = ViolationSeverity.ERROR
    warn = ViolationSeverity.WARNING
    note = ViolationSeverity.NOTE

    assert crit > error
    assert error > warn
    assert warn > note
    assert crit == crit
    assert error == error
    assert warn == warn
    assert note == note


@pytest.mark.xfail
def test_failure_violation_ordering():
    crit = ViolationSeverity.CRITICAL
    error = ViolationSeverity.ERROR
    warn = ViolationSeverity.WARNING
    note = ViolationSeverity.NOTE

    # The ordering of the severities with non-severities casuses errors
    assert crit > 2


def test_basic_parsing_validity():
    spec = {"types": [], "keys": []}
    check_parsing_validity(spec)

    assert True


def test_failure_basic_parsing_validity_keys():
    spec = {"types": []}
    try:
        check_parsing_validity(spec)
    except InvalidSpecificationError as e:
        assert e.violation.location == "/"
        assert e.violation.severity == ViolationSeverity.CRITICAL
        assert e.violation.violation_type == ViolationType.KEYS_UNDEFINED


def test_failure_basic_parsing_validity_types():
    spec = {"keys": []}
    try:
        check_parsing_validity(spec)
    except InvalidSpecificationError as e:
        assert e.violation.location == "/"
        assert e.violation.severity == ViolationSeverity.CRITICAL
        assert e.violation.violation_type == ViolationType.TYPES_UNDEFINED


def test_specification_key_general():
    keys = [
        {"qualifier": "test", "description": "Some description", "value": "some_value"}
    ]

    result, violations = parse_specification_keys(keys)

    assert len(result) == 1
    expected = {
        "test": MyrKey(
            qualifier="test",
            description="Some description",
            value="some_value",
            valid_values=None,
        )
    }
    assert result == expected


def test_multiple_keys():
    keys = [
        {"qualifier": "test", "description": "Some description", "value": "some_value"},
        {
            "qualifier": "test2",
            "description": "More descriptions",
            "value": "text",
            "valid_values": ["babba", "bollo"],
        },
    ]

    result, violations = parse_specification_keys(keys)

    assert len(violations) == 0
    assert len(result) == 2
    expected = {
        "test": MyrKey(
            qualifier="test",
            description="Some description",
            value="some_value",
            valid_values=None,
        ),
        "test2": MyrKey(
            qualifier="test2",
            description="More descriptions",
            value="text",
            valid_values=["babba", "bollo"],
        ),
    }
    assert result == expected


def test_specification_key_violations_qualifier():
    no_qualifier = [{"description": "Some description", "value": "some_value"}]

    result, violations = parse_specification_keys(no_qualifier)
    assert len(result) == 0
    assert len(violations) == 1

    violation = violations[0].violation
    assert violation.severity == ViolationSeverity.ERROR
    assert violation.violation_type == ViolationType.MISSING_KEY_QUALIFIER
    assert violation.location == "/keys/"


def test_specification_key_violations_description():
    no_description = [{"qualifier": "test", "value": "some_value"}]

    result, violations = parse_specification_keys(no_description)
    assert len(result) == 0
    assert len(violations) == 1

    violation = violations[0].violation
    assert violation.severity == ViolationSeverity.ERROR
    assert violation.violation_type == ViolationType.MISSING_KEY_DESCRIPTION
    assert violation.location == "/keys/test/"


def test_specification_key_violations_value():
    no_value = [
        {
            "qualifier": "test",
            "description": "Some description",
        }
    ]

    result, violations = parse_specification_keys(no_value)
    assert len(result) == 0
    assert len(violations) == 1

    violation = violations[0].violation
    assert violation.severity == ViolationSeverity.ERROR
    assert violation.violation_type == ViolationType.MISSING_KEY_VALUE
    assert violation.location == "/keys/test/"


def test_specification_key_violations_malformed_validvalues():
    no_value = [
        {
            "qualifier": "test",
            "description": "Some description",
            "value": "some_value",
            "valid_values": "",
        }
    ]

    result, violations = parse_specification_keys(no_value)
    assert len(result) == 0
    assert len(violations) == 1

    violation = violations[0].violation
    assert violation.severity == ViolationSeverity.ERROR
    assert violation.violation_type == ViolationType.MALFORMED_KEY_VALID_VALUES
    assert violation.location == "/keys/test/valid_values/"


def test_specification_key_violations_malformed_validvalues_content():
    no_value = [
        {
            "qualifier": "test",
            "description": "Some description",
            "value": "some_value",
            "valid_values": [3, 12, ViolationType.KEYS_UNDEFINED],
        }
    ]

    result, violations = parse_specification_keys(no_value)
    assert len(result) == 0
    assert len(violations) == 1

    violation = violations[0].violation
    assert violation.severity == ViolationSeverity.ERROR
    assert violation.violation_type == ViolationType.MALFORMED_KEY_VALID_VALUES
    assert violation.location == "/keys/test/valid_values/"


def test_specification_key_mixed():
    keys = [
        {"qualifier": "valid", "description": "", "value": "value"},
        {
            "qualifier": "valid2",
            "description": "",
            "value": "value",
            "valid_keys": ["one", "two"],
        },
        {"description": "", "value": "value"},
        {"value": "value", "qualifier": "nodesc"},
        {"description": "", "qualifier": "novalue"},
        {"description": "", "qualifier": "novalue2"},
    ]

    result, violations = parse_specification_keys(keys)

    assert len(result) == 2
    assert len(violations) == 4


def test_specification_types_basic():
    keys = {
        "test": MyrKey(
            qualifier="test", description=None, valid_values=None, value=None
        ),
        "test2": MyrKey(
            qualifier="test2", description=None, valid_values=None, value=None
        ),
    }
    types = [
        {
            "qualifier": "type",
            "description": "some desc",
            "valid_keys": [
                {"qualifier": "test", "required": True},
                {"qualifier": "test2", "required": False},
            ],
        }
    ]

    parsed_types, violations = parse_specification_types(types, keys)

    assert len(parsed_types) == 1
    assert len(violations) == 0
    parsed = parsed_types[0]
    assert len(parsed.optional_keys) == 1
    assert len(parsed.required_keys) == 1
    assert parsed.optional_keys[0] == keys["test2"]
    assert parsed.required_keys[0] == keys["test"]
    assert parsed.qualifier == "type"
    assert parsed.description == "some desc"
    assert len(parsed.valid_keys) == 2


def test_specification_types_violations_qualifier():
    keys = {
        "test": MyrKey(
            qualifier="test", description=None, valid_values=None, value=None
        ),
        "test2": MyrKey(
            qualifier="test2", description=None, valid_values=None, value=None
        ),
    }
    types = [
        {
            "description": "some desc",
            "valid_keys": [
                {"qualifier": "test", "required": True},
                {"qualifier": "test2", "required": False},
            ],
        }
    ]

    parsed_types, violations = parse_specification_types(types, keys)

    assert len(parsed_types) == 0
    assert len(violations) == 1
    violation = violations[0].violation
    assert violation.location == "/types/"
    assert violation.violation_type == ViolationType.MISSING_TYPE_QUALIFIER
    assert violation.severity == ViolationSeverity.ERROR


def test_specification_types_violations_description():
    keys = {
        "test": MyrKey(
            qualifier="test", description=None, valid_values=None, value=None
        ),
        "test2": MyrKey(
            qualifier="test2", description=None, valid_values=None, value=None
        ),
    }
    types = [
        {
            "qualifier": "type",
            "valid_keys": [
                {"qualifier": "test", "required": True},
                {"qualifier": "test2", "required": False},
            ],
        }
    ]

    parsed_types, violations = parse_specification_types(types, keys)

    assert len(parsed_types) == 0
    assert len(violations) == 1
    violation = violations[0].violation
    assert violation.location == "/types/type/"
    assert violation.violation_type == ViolationType.MISSING_TYPE_DESCRIPTION
    assert violation.severity == ViolationSeverity.ERROR


def test_specification_types_violations_validkeys():
    keys = {
        "test": MyrKey(
            qualifier="test", description=None, valid_values=None, value=None
        ),
        "test2": MyrKey(
            qualifier="test2", description=None, valid_values=None, value=None
        ),
    }
    types = [
        {
            "qualifier": "type",
            "description": "some desc",
        }
    ]

    parsed_types, violations = parse_specification_types(types, keys)

    assert len(parsed_types) == 0
    assert len(violations) == 1
    violation = violations[0].violation
    assert violation.violation_type == ViolationType.MISSING_TYPE_VALID_KEYS
    assert violation.location == "/types/type/"
    assert violation.severity == ViolationSeverity.ERROR


def test_specification_types_violations_key_qualifier():
    keys = {
        "test": MyrKey(
            qualifier="test", description=None, valid_values=None, value=None
        ),
        "test2": MyrKey(
            qualifier="test2", description=None, valid_values=None, value=None
        ),
    }
    types = [
        {
            "qualifier": "type",
            "description": "some desc",
            "valid_keys": [
                {"required": True},
                {"qualifier": "test2", "required": False},
            ],
        }
    ]

    parsed_types, violations = parse_specification_types(types, keys)

    assert len(parsed_types) == 0
    assert len(violations) == 1
    violation = violations[0].violation
    assert violation.violation_type == ViolationType.MISSING_TYPE_KEY_QUALIFIER
    assert violation.location == "/types/type/valid_keys/"
    assert violation.severity == ViolationSeverity.ERROR


def test_specification_types_violations_key_required():
    keys = {
        "test": MyrKey(
            qualifier="test", description=None, valid_values=None, value=None
        ),
        "test2": MyrKey(
            qualifier="test2", description=None, valid_values=None, value=None
        ),
    }
    types = [
        {
            "qualifier": "type",
            "description": "some desc",
            "valid_keys": [
                {"qualifier": "test"},
                {"qualifier": "test2", "required": False},
            ],
        }
    ]

    parsed_types, violations = parse_specification_types(types, keys)

    assert len(parsed_types) == 0
    assert len(violations) == 1
    violation = violations[0].violation
    assert violation.violation_type == ViolationType.MISSING_TYPE_KEY_REQUIRED
    assert violation.location == "/types/type/valid_keys/test/"
    assert violation.severity == ViolationSeverity.ERROR


def test_specification_types_violations_missingkeys():
    keys = {
        "test2": MyrKey(
            qualifier="test2", description=None, valid_values=None, value=None
        )
    }
    types = [
        {
            "qualifier": "type",
            "description": "some desc",
            "valid_keys": [
                {"qualifier": "test", "required": True},
                {"qualifier": "test2", "required": False},
            ],
        }
    ]

    parsed_types, violations = parse_specification_types(types, keys)

    assert len(parsed_types) == 0
    assert len(violations) == 1
    violation = violations[0].violation
    assert violation.violation_type == ViolationType.UNKOWN_KEY
    assert violation.location == "/types/type/valid_keys/test/"
    assert violation.severity == ViolationSeverity.ERROR


def test_multiple_violations_base():
    violations = [
        error_violation(violation_type=ViolationType.UNKOWN_KEY, location="/test/lol"),
        warning_violation(
            violation_type=ViolationType.MISSING_KEY_VALUE, location="/other/"
        ),
    ]
    error = MultipleViolationsError(violations)

    assert error.violations == violations
    assert error.max_severity == ViolationSeverity.ERROR
    assert error.message == (
        " --- FOUND 2 VIOLATIONS ---\n\n"
        f"[1 / 2] @ /test/lol -- {ViolationSeverity.ERROR.value}: {ViolationType.UNKOWN_KEY.value}\n"
        f"[2 / 2] @ /other/ -- {ViolationSeverity.WARNING.value}: {ViolationType.MISSING_KEY_VALUE.value}\n"
    )
