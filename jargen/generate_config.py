"""Contains all functions required to generate configuration for network devices/the routebox container"""

from collections import defaultdict
from datetime import datetime
from hashlib import sha256
from ipaddress import IPv4Address

from jinja2 import Environment, FileSystemLoader

from jargen.build_container import buildContainer
from jargen.objects import Neighbor, Route


def writeConfig(path: str, config: str, fileName: str = "config.txt") -> None:
    """Simple function to export the generated configuration to a text file on disk"""
    with open(f"{path}/{fileName}", "w") as file:
        _ = file.write(config)


def config_ios(
    routes: list[Route], path: str, localAS: int = -1, vrf: str = ""
) -> None:
    """Generate route/policy configurations for Cisco IOS and IOS-XE platforms"""
    config: list[str] = []
    baseRouteCommand = f"ip route vrf {vrf}" if vrf else "ip route"
    for route in routes:
        config.append(
            f"{baseRouteCommand} {' '.join(str(route.network.with_netmask).split('/'))} null0"
        )

    # Identify routes with identical policy configurations
    routeDict = defaultdict(list)
    for route in routes:
        routeDict[
            (" ".join(route.aspath_as_str), " ".join(route.communities), route.origin)
        ].append(route.network)

    for index, value in enumerate(routeDict):
        prefixListName = f"ROUTEGEN-PL{index + 1}"

        for prefixIndex, prefixValue in enumerate(routeDict[value]):
            config.append(
                f"ip prefix-list {prefixListName} seq {(prefixIndex + 1)} permit {prefixValue}"
            )

        config.append(f"route-map ROUTEGEN-RM permit {(index + 1)}")
        config.append(f"  match ip address prefix-list {prefixListName}")
        config.append(f"  set as-path prepend {value[0]}" if value[0] else "")
        config.append(f"  set community add {value[1]}" if value[1] else "")
        config.append(f"  set origin {value[2]}" if value[2] != "igp" else "")

        if localAS > 0:
            config.append(f"router bgp {localAS}")
            config.append("redistribute static route-map ROUTEGEN-RM")

    writeConfig(path=path, config="\n".join([x for x in config if x]))


def config_iosxr():
    """Generate route/policy configuration for Cisco IOS-XR-based platforms"""
    raise NotImplementedError("IOS-XR configuration generation is not implemented yet.")


def config_junos(
    routes: list[Route], path: str, vrf: str = "", bgpGroup: str = ""
) -> None:
    """Generate route/policy configurations for Juniper Junos-based platforms"""
    config: list[str] = []
    command = ""
    baseCommand = f"set routing-instances {vrf}" if vrf else "set"
    baseRouteCommand = " ".join([baseCommand, "routing-options static route"])
    for route in routes:
        command = f"{baseRouteCommand} {str(route.network)} discard"
        command += (
            f" community [ {' '.join(route.communities)} ]" if route.communities else ""
        )
        command += (
            f' as-path path "{" ".join(route.aspath_as_str)}"' if route.aspath else ""
        )
        command += f" as-path origin {route.origin}" if route.origin != "igp" else ""

        config.append(command)

    basePolicyCommand = "set policy-options policy-statement ROUTEGEN-POLICY term 1"
    config.append(f"{basePolicyCommand} from protocol static")
    config.append(f"{basePolicyCommand} then accept")

    if bgpGroup:
        command += (
            f"{baseCommand} protocols bgp group {bgpGroup} export ROUTEGEN-POLICY"
        )

    writeConfig(path=path, config="\n".join(config))


def config_container(
    path: str,
    outputPath: str,
    routes: list[Route],
    neighbors: list[Neighbor],
    rid: IPv4Address,
    userAttributes: dict[str, str],
) -> None:
    """Generate all required configuration to build the routebox container"""

    def load_template(filename: str):
        return Environment(loader=FileSystemLoader(path)).get_template(filename)

    birdTemplate = load_template("bird.conf.j2")
    birdContent = birdTemplate.render(rid=str(rid), routes=routes, neighbors=neighbors)

    birdContentHash = str(sha256(birdContent.encode("utf-8")).hexdigest())
    dockerTemplate = load_template("Dockerfile.j2")
    dockerContent = dockerTemplate.render(hash=birdContentHash)

    sysAttributes = {
        "Date/Time Container Created": datetime.today().strftime(
            "%m/%d/%Y at %H:%M:%S"
        ),
        "bird.conf Hash": birdContentHash,
        "Number of Routes": len(routes),
        "Number of Neighbors": len(neighbors),
        "BGP Router ID": rid,
    }
    entrypointTemplate = load_template("docker-entrypoint.sh.j2")
    entrypointContent = entrypointTemplate.render(
        neighbors=neighbors, userAttributes=userAttributes, sysAttributes=sysAttributes
    )

    for item in [f"{path}/bird.conf", f"{path}/../output/{birdContentHash}.bird.conf"]:
        with open(item, "w") as file:
            _ = file.write(birdContent)

    with open(f"{path}/docker-entrypoint.sh", "w") as file:
        _ = file.write(entrypointContent)

    with open(f"{path}/Dockerfile", "w") as file:
        _ = file.write(dockerContent)

    buildContainer(
        dockerfilePath=f"{path}/Dockerfile",
        tarballPath=outputPath,
        birdConfHash=birdContentHash,
    )


platforms = {"ios": config_ios, "junos": config_junos, "container": config_container}
