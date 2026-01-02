from ipaddress import IPv4Network, IPv4Address
from random import randint
from src.objects import Route

def test_global(address: IPv4Address) -> bool:
    if not address.is_global:
        return False
    return True

def runTests(address: IPv4Address) -> bool:
    enabledTests = {
        "Test to make sure that the address is a valid globally routable address": test_global
    }
    for test in enabledTests:
        if not enabledTests[test](address):
            return False
    return True

def generate_network() -> str:
    while True:
        # Generate random IP address between 1.0.0.0 and 223.255.255.255 (0.0.0.0/8 = reserved, 224.0.0.0/4 = multicast, 240.0.0.0/4 = reserved) and make sure that it passes all defined tests
        address = IPv4Address(randint(16777216, 3758096383))
        if not runTests(address=address):
            continue
        # Generate random prefix length between 1 and 32 (excludes /0)
        minPL = 8
        maxPL = 32
        prefixLength = randint(minPL, maxPL)

        return f"{str(address)}/{prefixLength}"
    
def generate_aspath(mode: str = "2byte", include_privateAS: bool = False, maxLength: int = 10) -> list[str]:
    # Generate random AS-PATH
    # Valid modes: 2byte, 4byte, 24byte
    aspath = []
    match (mode, include_privateAS):
        case ("2byte", True):
            minAS = 1
            maxAS = 65535
        case ("2byte", False):
            minAS = 1
            maxAS = 64512
        case ("4byte", True):
            minAS = 65536
            maxAS = 4296967294
        case ("4byte", False):
            minAS = 65536
            maxAS = 4199999999
        case ("24byte", True):
            minAS = 1
            maxAS = 4296967294
        case ("24byte", False):
            minAS = 1
            maxAS = 4199999999

    for i in range(randint(1, maxLength)):
        aspath.append(str(randint(minAS, maxAS)))
    
    return aspath

def generateRoutes() -> Route:
    network = generate_network()
    aspath = generate_aspath()
    return Route(network=IPv4Network(network, strict=False), aspath=aspath)