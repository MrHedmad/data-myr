from enum import Enum
from typing import Optional, Union, Literal, Any, NoReturn
from functools import partial, total_ordering
from dataclasses import dataclass
from sys import exit
from copy import copy
import logging

log = logging.getLogger(__name__)


class InvalidBundleError(Exception):
    """Raised when loading a bundle fails"""

    pass


class ViolationType(Enum):
    METADATA_NOT_FOUND = "The `myr-metadata.json` file was not found."
    INVALID_SPEC_FORMAT = "The `myr-metadata.json` file could not be loaded."
    # Remote / relative keys error
    ID_COLLISION = "Id is not unique."
    ID_NOT_FOUND = "Id was not found."
    INVALID_REMOTE = "The key did not point to a valid URL"
    REMOTE_NOT_JSON = "Response from remote key was not in valid JSON"
    # Gross object errors
    TYPE_NOT_FOUND = "Object did not have the `type` key"
    TYPES_UNDEFINED = "The specification does not have the `types` key."
    KEYS_UNDEFINED = "The specification does not have the `keys` key."
    KEYS_VALUE_INVALID = "The `keys` key does not specify a list of values."
    TYPES_VALUE_INVALID = "The `types` key does not specify a list of values."
    # Type specification errors
    MISSING_TYPE_QUALIFIER = "A type has no `qualifier`."
    MISSING_TYPE_DESCRIPTION = "The type has no `description`."
    MISSING_TYPE_VALID_KEYS = "The type has no `valid_keys` key."
    MISSING_TYPE_KEY_REQUIRED = "The type key has no `required` field."
    MISSING_TYPE_KEY_QUALIFIER = "The type key has no `qualifier`."
    # Key specification errors
    MISSING_KEY_QUALIFIER = "A key has no `qualifier`."
    MISSING_KEY_DESCRIPTION = "The key has no `description`."
    MISSING_KEY_VALUE = "The key has no `value`."
    UNKNOWN_KEY_VALUE = "The key has unknown `value`."
    MALFORMED_KEY_VALID_VALUES = "The entry of valid values for this key is wrong."
    # Double qualifier errors
    DUPLICATED_QUALIFIER = "The qualifier for this object is duplicated."
    # Invalid specification constants
    MISSING_REQUIRED_KEY = "The object is missing a required specification key."
    # Invalid checks errors
    MISSING_TYPE_KEY = "The object has no 'type' key."
    UNKNOWN_TYPE = "The object has a type which is not in the specification."
    UNKOWN_KEY = "Key was not found in the specification."
    WRONG_KEY_TYPE = "Key has unexpected type."


@total_ordering
class ViolationSeverity(Enum):
    CRITICAL = "Critical"
    """
    The violation causes the check process to halt immediately.
    """
    ERROR = "Error"
    """
    The violation makes the bundle invalid, but does not block the inspection
    of the rest of the specification.
    """
    WARNING = "Warning"
    """
    The specification was not violated, but something could be going wrong.
    """
    NOTE = "Note"
    """
    There is nothing wrong, but the user should be notified nonetheless.
    """

    def __lt__(self, other):
        values = {self.CRITICAL: 3, self.ERROR: 2, self.WARNING: 1, self.NOTE: 0}
        if self.__class__ is other.__class__:
            return values[self] < values[other]
        return NotImplemented


class SpecificationViolation:
    def __init__(
        self,
        location: Optional[str],
        violation_type: Optional[ViolationType],
        severity: ViolationSeverity,
        context: Optional[dict] = None,
    ):
        self.location: Optional[str] = location
        self.violation_type: Optional[ViolationType] = violation_type
        self.severity: ViolationSeverity = severity
        self.context: Optional[dict] = context


class InvalidSpecificationError(InvalidBundleError):
    """Raised when loading a specification fails"""

    def __init__(self, violation: SpecificationViolation, *args, **kwargs) -> None:
        self.violation: SpecificationViolation = violation


class MultipleViolationsError(InvalidBundleError):
    """Raised when multiple violations are found."""

    def __init__(self, violations: list[InvalidSpecificationError]) -> None:
        self.violations: list[InvalidSpecificationError] = violations
        """The input list of violations"""
        output_str = f" --- FOUND {len(violations)} VIOLATIONS ---\n\n"
        for i, violation in enumerate(violations, 1):
            violation_context = violation.violation.context
            output_str += (
                f"[{i} / {len(violations)}] "
                f"@ {violation.violation.location} "
                f"-- {violation.violation.severity.value}: "
                f"{violation.violation.violation_type.value}\n"
            )
        self.message: str = output_str
        """A parsed summary message of all the violations."""

        self.max_severity: ViolationSeverity = max(
            [x.violation.severity for x in violations]
        )
        """The greatest severity among all violations"""


PossibleViolations = Union[list[SpecificationViolation], None]


def violation(
    violation_type: ViolationType, severity: ViolationSeverity, location: Optional[str]
) -> InvalidSpecificationError:
    """Wrapper to make violation errors quickly"""
    log.debug(f"Making new violation: {violation_type}, {severity}, {location}")
    return InvalidSpecificationError(
        violation=SpecificationViolation(
            location=location, violation_type=violation_type, severity=severity
        )
    )


critical_violation = partial(violation, severity=ViolationSeverity.CRITICAL)
error_violation = partial(violation, severity=ViolationSeverity.ERROR)
warning_violation = partial(violation, severity=ViolationSeverity.WARNING)
note_violation = partial(violation, severity=ViolationSeverity.NOTE)


@dataclass
class MyrKey:
    qualifier: str
    description: str
    value: Union[Literal["any"], Literal["text"], str]
    valid_values: list[Any]


@dataclass
class MyrType:
    qualifier: str
    description: str
    required_keys: list[MyrKey]
    optional_keys: list[MyrKey]

    @property
    def valid_keys(self) -> list[MyrKey]:
        all_keys = copy(self.required_keys)
        all_keys.extend(self.optional_keys)
        return all_keys


def check_parsing_validity(specification: dict) -> None:
    """Check a specification for basic parsing validity.

    This includes:
        - Having the `types` and `keys` keys;
        - Both the `types` and `keys` keys have lists as values;

    Raises:
        InvalidSpecificationError if some checks fail.
    """
    if "types" not in specification:
        raise critical_violation(ViolationType.TYPES_UNDEFINED, location=f"/")
    if "keys" not in specification:
        raise critical_violation(ViolationType.KEYS_UNDEFINED, location=f"/")

    if not isinstance(specification["types"], list):
        raise critical_violation(ViolationType.TYPES_VALUE_INVALID, location=f"/types/")
    if not isinstance(specification["keys"], list):
        raise critical_violation(ViolationType.KEYS_VALUE_INVALID, location=f"/keys/")

    return None


def parse_specification_keys(
    keys: list[dict],
) -> tuple[dict[str, MyrKey], list[InvalidSpecificationError]]:
    """Parse the keys in a specification.

    Returns:
        A tuple with a dict of parsed `MyrType`s for correctly parsed keys and a
        list of `InvalidSpecificationError`s with errors for invalid keys.
    """
    violations = []
    parsed_keys: dict[str, MyrKey] = {}
    for value in keys:
        # First of all, check if we have the valid keys.
        if "qualifier" not in value:
            violations.append(
                error_violation(ViolationType.MISSING_KEY_QUALIFIER, location=f"/keys/")
            )

            continue
        key = value["qualifier"]
        if "description" not in value:
            violations.append(
                error_violation(
                    ViolationType.MISSING_KEY_DESCRIPTION, location=f"/keys/{key}/"
                )
            )
            continue
        if "value" not in value:
            violations.append(
                error_violation(
                    ViolationType.MISSING_KEY_VALUE, location=f"/keys/{key}/"
                )
            )
            continue

        if "valid_values" in value and value["valid_values"] is not None:
            if not isinstance(value["valid_values"], list):
                violations.append(
                    error_violation(
                        ViolationType.MALFORMED_KEY_VALID_VALUES,
                        location=f"/keys/{key}/valid_values/",
                    )
                )
                continue
            if not all([isinstance(x, str) for x in value["valid_values"]]):
                violations.append(
                    error_violation(
                        ViolationType.MALFORMED_KEY_VALID_VALUES,
                        location=f"/keys/{key}/valid_values/",
                    )
                )
                continue

        parsed_keys[key] = MyrKey(
            qualifier=value["qualifier"],
            description=value["description"],
            value=value["value"],
            valid_values=value.get("valid_values"),
        )

    return (parsed_keys, violations)


def parse_specification_types(
    types: list[dict], keys: dict[str, MyrKey]
) -> tuple[list[MyrType], list[InvalidSpecificationError]]:
    parsed_types: list[MyrType] = []
    violations: list[InvalidSpecificationError] = []
    for value in types:
        # Again, check first if we have the keys.
        if "qualifier" not in value:
            violations.append(
                error_violation(
                    ViolationType.MISSING_TYPE_QUALIFIER, location=f"/types/"
                )
            )
            continue
        key = value["qualifier"]
        if "description" not in value:
            violations.append(
                error_violation(
                    ViolationType.MISSING_TYPE_DESCRIPTION, location=f"/types/{key}/"
                )
            )
            continue
        if "valid_keys" not in value:
            violations.append(
                error_violation(
                    ViolationType.MISSING_TYPE_VALID_KEYS, location=f"/types/{key}/"
                )
            )
            continue
        # Check if we have all the keys we need in valid_keys
        required_keys = []
        optional_keys = []
        found_violations = False
        for key_obj in value["valid_keys"]:
            if "qualifier" not in key_obj:
                violations.append(
                    error_violation(
                        ViolationType.MISSING_TYPE_KEY_QUALIFIER,
                        location=f"/types/{key}/valid_keys/",
                    )
                )
                found_violations = True
                continue
            if key_obj["qualifier"] not in keys:
                violations.append(
                    error_violation(
                        ViolationType.UNKOWN_KEY,
                        location=f"/types/{key}/valid_keys/{key_obj['qualifier']}/",
                    )
                )
                found_violations = True
                continue
            if "required" not in key_obj:
                violations.append(
                    error_violation(
                        ViolationType.MISSING_TYPE_KEY_REQUIRED,
                        location=f"/types/{key}/valid_keys/{key_obj['qualifier']}/",
                    )
                )
                found_violations = True
                continue

            if key_obj["required"] is True:
                required_keys.append(keys[key_obj["qualifier"]])
            else:
                optional_keys.append(keys[key_obj["qualifier"]])

        if found_violations:
            continue

        parsed_types.append(
            MyrType(
                qualifier=value["qualifier"],
                description=value["description"],
                required_keys=required_keys,
                optional_keys=optional_keys,
            )
        )

    return (parsed_types, violations)


class Specification:
    def __init__(self, specification: dict) -> None:
        """Parse a specification to a specification object.

        Raises:
            `MultipleViolationsError` if specification violations are found.
        """
        # Get these out of the way.
        check_parsing_validity(specification)

        keys, violations = parse_specification_keys(specification["keys"])
        types, type_violations = parse_specification_types(specification["types"], keys)
        violations.extend(type_violations)

        if violations:
            raise MultipleViolationsError(violations)

        # Step 3 - Check if the keys mention valid types
        # We have a sort of circular dependency here, since the keys
        # may list valid types in the specification. We check them here.
        loop_violations: list[InvalidSpecificationError] = []
        possible_types = [x.qualifier for x in types]
        for key, value in keys.items():
            # The "value" slot has what the key is
            if value.value in ["text", "any"]:
                continue
            if value.value not in possible_types:
                loop_violations.append(
                    error_violation(
                        ViolationType.UNKNOWN_KEY_VALUE, location=f"/keys/{key}/value"
                    )
                )
                continue
        if loop_violations:
            raise MultipleViolationsError(violations)

        # Step 4 - Package types in the object
        self.types: dict[str, MyrType]
        self.original_specification: dict = specification
