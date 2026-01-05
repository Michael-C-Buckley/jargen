import ipaddress as ip
from src.generate_routes import generateRoutes
from src.generate_config import platforms
from src.config_validation import validateConfig
from src.exceptions import ConfigValidationTestFailedError
from src.read_write_files import read_yaml
from os import path
from yaml import safe_load, YAMLError
import click as cli

@cli.command()
@cli.option("-c", "--configfile", help="Specify path (including file name) to the config YAML file. By default, routegen assumes a config.yml file in the current working directory", type=str, default="config.yml")
def main(configfile: str) -> None:
    routes = []
    existingPrefixes = []

    try:
        config = read_yaml(configfile)
        validateConfig(config=config,
                       schema=read_yaml(f"{path.dirname(__file__)}/data/config.schema.yml"),
                       types=read_yaml(f"{path.dirname(__file__)}/data/config.types.yml"))
    except ConfigValidationTestFailedError as e:
        print(e)
        exit(-1)

    counter = 0
    while counter < config["prefixes"]["quantity"]:
        route = generateRoutes()
        if route.network not in existingPrefixes:
            routes.append(route)
            existingPrefixes.append(route.network)
            counter += 1

    for platform in config["basic"]["platforms"]:
        platforms[platform](path=path.join(path.dirname(__file__), "output"), routes=routes)

if __name__ == "__main__":
    main()

