"""Contains all the exceptions used by the package"""


class ConfigValidationTestFailedError(Exception):
    """Exception raised when a test fails"""

    def __init__(self, test: str) -> None:
        self.test = test

    def __str__(self) -> str:
        return f"Test failed during configuration validation: {self.test}"
