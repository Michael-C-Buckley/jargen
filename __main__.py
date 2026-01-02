import ipaddress as ip
from src.generate_routes import generateRoutes
from src.generate_config import platforms
from os import path
from yaml import safe_load

def main() -> None:
    routes = []
    existingPrefixes = []

    with open("config.yml") as configFile:
        config = safe_load(configFile)

    counter = 0
    while counter < config["basic"]["desiredNumOfRoutes"]:
        route = generateRoutes()
        if route.network not in existingPrefixes:
            routes.append(route)
            existingPrefixes.append(route.network)
            counter += 1

    platforms[config["basic"]["platform"]](path=path.join(path.dirname(__file__), "output"), routes=routes)

if __name__ == "__main__":
    main()