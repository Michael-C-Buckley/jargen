import ipaddress as ip
from genroutes import genRoutes
from genconfig import platforms

routes = []
existingPrefixes = []
desiredNumOfRoutes = 1000
desiredPlatform = "junos"

counter = 0
while counter < desiredNumOfRoutes:
    route = genRoutes()
    if route.network not in existingPrefixes:
        routes.append(route)
        existingPrefixes.append(route.network)
        counter += 1

config = platforms[desiredPlatform](routes=routes)

with open("output/config.txt", "w") as file:
    file.write(config)