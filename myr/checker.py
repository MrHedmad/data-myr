from enum import Enum
from typing import Optional, Union, Literal, Any, NoReturn
from functools import partial
from dataclasses import dataclass
from sys import exit
from copy import copy

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
    # Type specification errors
    MISSING_TYPE_QUALIFIER = "A type has no `qualifier`."
    MISSING_TYPE_DESCRIPTION = "The type has no `description`."
    MISSING_TYPE_VALID_KEYS = "The type has no `valid_keys` key."
    MISSING_TYPE_KEY_REQUIRED = "The type key has no `required` field."
    # Key specification errors
    MISSING_KEY_QUALIFIER = "A key has no `qualifier`."
    MISSING_KEY_DESCRIPTION = "The key has no `description`."
    MISSING_KEY_VALUE = "The key has no `value`."
    # Double qualifier errors
    DUPLICATED_QUALIFIER = "The qualifier for this object is duplicated."
    # Invalid specification constants
    MISSING_REQUIRED_KEY = "The object is missing a required key, {}."
    # Invalid checks errors
    UNKOWN_KEY = "Key was not found in the specification"
    WRONG_KEY_TYPE = "Key has type {}, but expected {}."


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


class SpecificationViolation:
    def __init__(
        self, location: Optional[str], violation_type: Optional[ViolationType], severity: ViolationSeverity,
        context: Optional[dict] = None
    ):
        self.location: Optional[str] = location
        self.violation_type: Optional[ViolationType] = violation_type
        self.severity: ViolationSeverity = severity
        self.context: Optional[dict] = context


class InvalidSpecificationError(InvalidBundleError):
    """Raised when loading a specification fails"""

    def __init__(self, violation: SpecificationViolation, *args, **kwargs) -> None:
        self.violation: SpecificationViolation = violation

class MyrBundle:
    def __init__(self, data):
        self.specification = data["specification"]

PossibleViolations = Union[list[SpecificationViolation], None]

def violation(violation_type: ViolationType, severity: ViolationSeverity, location: Optional[str]) -> InvalidSpecificationError:
    """Wrapper to make violation errors quickly"""
    return InvalidSpecificationError(
        violation=SpecificationViolation(
            location=location,
            violation_type=violation_type,
            severity=severity
        )
    )

critical_violation = partial(violation, severity = ViolationSeverity.CRITICAL)
error_violation = partial(violation, severity = ViolationSeverity.ERROR)
warning_violation = partial(violation, severity = ViolationSeverity.WARNING)
note_violation = partial(violation, severity = ViolationSeverity.NOTE)

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

def get_or_raise(dictionary: dict, key: str, error: Exception) -> Any:
    try:
        return dictionary[key]
    except KeyError:
        raise error

def raise_violations(violations: list[InvalidSpecificationError]) -> None:
    """Raise a list of specifications, ending the program if errors are found."""
    output_str = f" --- FOUND {len(violations)} VIOLATIONS ---\n\n"
    stop = False
    for i, violation in enumerate(violations):
        violation_context = violation.violation.context
        output_str += (
            f"[{i} / {len(violations)}]"
            f"@ {violation.violation.location} "
            f"-- {violation.violation.severity.value}:"
            f"{violation.violation.violation_type.value}\n"
        )
        if violation.violation.severity in [ViolationSeverity.ERROR, ViolationSeverity.CRITICAL]:
            stop = True
    print(output_str)
    if stop:
        exit(1)

    return None

class Specification:
    def __init__(self, specification: dict) -> None:
        """Parse a specification to a specification object.

        Will raise InvalidSpecificationError if some are found, with
        criticality CRITICAL.
        """
        # Get these out of the way.
        if "types" not in specification:
            raise critical_violation(ViolationType.TYPES_UNDEFINED, location = f"/")
        if "keys" not in specification:
            raise critical_violation(ViolationType.KEYS_UNDEFINED, location = f"/")

        # Step 1 - Load the keys
        # We do this first to load them in each MyrType object.
        violations = []
        keys: dict[str, MyrKey] = {}
        for value in specification["keys"]:
            # First of all, check if we have the valid keys.
            if "qualifier" not in value:
                violations.append(error_violation(ViolationType.MISSING_KEY_QUALIFIER, location=f"keys/"))
                continue
            key = value["qualifier"]
            if "description" not in value:
                violations.append(error_violation(ViolationType.MISSING_KEY_DESCRIPTION, location=f"keys/{key}/"))
                continue
            if "value" not in value:
                violation.append(error_violation(ViolationType.MISSING_KEY_VALUE, location=f"keys/{key}/"))
                continue
            keys[key] = MyrKey(
                qualifier=value["qualifier"], description=value["description"], value=value["value"],
                valid_values=value.get("valid_values")
            )

        types: list[MyrType] = []
        # Step 2 - Load the types
        # Since we know of the keys, we can make the types.
        for value in specification["types"]:
            # Again, check first if we have the keys.
            if "qualifier" not in value:
                violations.append(error_violation(ViolationType.MISSING_TYPE_QUALIFIER, location=f"types/"))
                continue
            key = value["qualifier"]
            if "description" not in value:
                violations.append(error_violation(ViolationType.MISSING_TYPE_DESCRIPTION, location=f"types/{key}/"))
                continue
            if "valid_keys" not in value:
                violations.append(error_violation(ViolationType.MISSING_TYPE_VALID_KEYS, location=f"types/{key}/"))
                continue
            # Check if we have all the keys we need in valid_keys
            required_keys = []
            optional_keys = []
            for key_obj in value["valid_keys"]:
                if "qualifier" not in key_obj:
                    violations.append(error_violation(ViolationType.MISSING_TYPE_KEY_REQUIRED, location=f"types/{key}/valid_keys/"))
                    continue
                if key_obj["qualifier"] not in keys:
                    violations.append(error_violation(ViolationType.UNKOWN_KEY, location=f"types/{key}/valid_keys/{key_obj['qualifier']}"))
                    continue
                if key_obj["required"] is True:
                    required_keys.append(keys[key_obj["qualifier"]])
                else:
                    optional_keys.append(keys[key_obj["qualifier"]])
            types.append(
                MyrType(
                    qualifier=value["qualifier"],
                    description=value["description"],
                    required_keys=required_keys,
                    optional_keys=optional_keys
                )
            )

        if violations:
            raise_violations(violations)

        # Step 3 - Check if the keys mention valid types
        # We have a sort of circular dependency here, since the keys
        # may list valid types in the specification. We check them here.



        # Step 4 - Package types in the object
        self.types: dict[str, MyrType]
        self.original_specification: dict = specification
