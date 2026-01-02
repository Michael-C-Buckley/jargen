from ipaddress import IPv4Network

class Route:
    def __init__(self, network: IPv4Network, aspath: list[str] = [], origin: str = "igp", communities: list[str] = []):
        self.network = network
        self.aspath = aspath
        self.origin = origin
        self.communities = communities

class Neighbor:
    def __init__(self, address: str, asn: int):
        self.address = address
        self.asn = asn

class Attribute:
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value