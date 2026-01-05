from typing import Any, Callable
from src.exceptions import ConfigValidationTestFailedError
from re import fullmatch

# The tests are defined as such:
# def validate_{topLevelConfig}(relevantConfig: {correct type}) -> bool:
# where "topLevelConfig" is replaced by the name of every single top level key (e.g., basics, bgp, container, etc.)
# Ensure that the test returns True/False based on the result
# Add the function object itself for the test as a value to the enabledTest dict (key = description of the test)

def basic_validation_caller(config: dict | list, schema: dict | list, types: dict | list):

    def basic_validation_dict():
        # Check to see whether there are any invalid keys
        if not all([x in schema for x in config]):
            return False
        # Check to see whether all required keys are present
        if not all([x in config for x in schema["required"]]):
            return False

        return True

    def basic_validation_list():
        # Check whether any duplicate items exist in the list
        try:
            # Works for all non-hashable types (e.g., str, int)
            if len(set(config)) != len(config):
                return False
        except TypeError:
            # Works for non-hashable/mutable types (in this context, namely dicts)
            if len([dict(t) for t in {tuple(d.items()) for d in config}]) != len(config):
                return False

        return True

    subroutines = {dict: basic_validation_dict, list: basic_validation_list}
    if not subroutines[type(config)]():
        return False
    for item in config:
        if isinstance(config, dict):
            dataContent = config[item]
            dataSchema = schema[item]
            dataType = types[item]
        elif isinstance(config, list):
            dataContent = item
            dataSchema = schema[0]
            dataType = types[0]

        if not isinstance(dataContent, type(dataType)):
            return False

        if isinstance(dataType, (dict, list)):
            if not basic_validation_caller(config=dataContent, schema=dataSchema, types=dataType):
                return False
        else:
            if not fullmatch(dataSchema["regex"], str(dataContent)):
                return False

    return True

def validate_base(key: str) -> Callable:
    def wrapper(f: Callable):
        def inner(config: dict[str, Any], schema: dict[str, Any], types: dict[str, Any]):
            if not basic_validation_caller(config=config[key], schema=schema[key], types=types[key]):
                return False
            return f(config=config[key], schema=config[key], types=config[key])
        return inner
    return wrapper

@validate_base("basic")
def validate_basic(config: dict[str, Any], schema: dict[str, Any], types: dict[str, Any]) -> bool:
    """Test to validate the configuration included in the basic top-level section"""
    pass

@validate_base("mrt")
def validate_mrt(config: dict[str, Any], schema: dict[str, Any], types: dict[str, Any]) -> bool:
    """Test to validate the configuration included in the mrt top-level section"""
    pass

@validate_base("prefixes")
def validate_prefixes(config: dict[str, Any], schema: dict[str, Any], types: dict[str, Any]) -> bool:
    """Test to validate the configuration included in the prefixes top-level section"""
    pass

@validate_base("bgp")
def validate_bgp(config: dict[str, Any], schema: dict[str, Any], types: dict[str, Any]) -> bool:
    """Test to validate the configuration included in the bgp top-level section"""
    pass

@validate_base("ospf")
def validate_ospf(config: dict[str, Any], schema: dict[str, Any], types: dict[str, Any]) -> bool:
    """Test to validate the configuration included in the ospf top-level section"""
    pass

@validate_base("device")
def validate_device(config: dict[str, Any], schema: dict[str, Any], types: dict[str, Any]) -> bool:
    """Test to validate the configuration included in the device top-level section"""
    pass

@validate_base("container")
def validate_container(config: dict[str, Any], schema: dict[str, Any], types: dict[str, Any]) -> bool:
    """Test to validate the configuration included in the container top-level section"""
    # Validate that it is an eBGP peering
    pass

@validate_base("policy")
def validate_policy(config: dict[str, Any], schema: dict[str, Any], types: dict[str, Any]) -> bool:
    """Test to validate the configuration included in the policy top-level section"""
    pass

def validateConfig(config: dict[str, Any], schema: dict[str, Any], types: dict[str, Any]) -> None:
    """Run all enabled tests against the provided configuration and handle/raise failures/exceptions as required"""
    enabledTests = {
        "Test to validate basic configuration": validate_basic
    }
    for test in enabledTests:
        if not enabledTests[test](config=config, schema=schema, types=types):
            raise ConfigValidationTestFailedError(test=test)