"""Contains a function to build the Docker container image"""
from docker import from_env

def buildContainer(dockerfilePath: str, tarballPath: str, birdConfHash: str):
    """Build the BIRD/Alpine-based Docker container image for the BGP box, clean up all artifacts, and export a tarball"""
    client = from_env()
    image = client.images.build(
        path=dockerfilePath,
        tag=f"routebox:{birdConfHash}",
        forcerm=True,
        nocache=True
    )[0]

    with open(f"{tarballPath}", "wb") as file:
        for chunk in image.save(named=True):
            file.write(chunk)

    client.images.remove(image.id)