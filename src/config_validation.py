# Validate that it is an eBGP peering
from typing import Any

def validateConfig(config: dict[str, Any]) -> None:
    enabledTests = {}
    for test in enabledTests:
        enabledTests[test]()