"""Contains all functions needed when generating a route object, its associated network, and any associated path/route attributes"""

from ipaddress import IPv4Address, IPv4Network
from random import choices, randint

from jargen.objects import Route


# The tests are defined as such:
# def test_{testname}(address: IPv4Address) -> bool
# Ensure that the test returns True/False based on the result
# Add the function object itself for the test as a value to the enabledTest dict (key = description of the test)
def test_global(address: IPv4Address) -> bool:
    """Test to make sure that the address is a valid globally routable address"""
    if not address.is_global:
        return False
    return True


def runTests(address: IPv4Address) -> bool:
    """Function to run the enabled tests and handle/raise failures/exceptions as required"""
    enabledTests = {
        "Test to make sure that the address is a valid globally routable address": test_global
    }
    for test in enabledTests:
        if not enabledTests[test](address):
            return False
    return True


def generate_network(min_prefix_length: int = 8, max_prefix_length: int = 30) -> str:
    """Generate a randomized IPv4/IPv6 network, based on provided constraints in the configuration"""
    while True:
        # Generate random IP address between 1.0.0.0 and 223.255.255.255 (0.0.0.0/8 = reserved, 224.0.0.0/4 = multicast, 240.0.0.0/4 = reserved) and make sure that it passes all defined tests
        address = IPv4Address(randint(16777216, 3758096383))
        if not runTests(address=address):
            continue

        prefixLength = randint(min_prefix_length, max_prefix_length)

        return f"{str(address)}/{prefixLength}"


def generate_aspath(mode: str, include_privateAS: bool, maxLength: int) -> list[int]:
    """Generate a random AS-PATH sequence containing 2 and/or 4-byte private and/or public ASNs, based on provided constraints in the configuration"""
    aspath = []
    minAS = -1
    maxAS = -1

    # TODO: implement mode enum
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

    # Prevent invalid cases
    assert minAS != -1 and maxAS != -1

    for _ in range(randint(1, maxLength)):
        aspath.append(randint(minAS, maxAS))

    return aspath


def generate_communities() -> list[str]:
    """Generate BGP communities for the route"""
    raise NotImplementedError("Generate communities is not yet implemented")


def generate_origin(probabilities: list[int]) -> str:
    """Randomly choose an origin code for the route based on the provided probabilities"""
    originCodes = ["igp", "egp", "incomplete"]

    return choices(originCodes)[0]


def generateRoutes() -> Route:
    """Construct a route object"""
    network = generate_network(8, 30)
    aspath = generate_aspath("2Byte", True, 10)
    communities = generate_communities()
    origin = generate_origin(aspath)

    return Route(
        network=IPv4Network(network, strict=False),
        aspath=aspath,
        communities=communities,
        origin=origin,
    )
