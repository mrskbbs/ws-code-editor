import docker

from app.config import CONTAINER_NAME 

docker_client = docker.from_env()
container = None

try:
    container = docker_client.containers.get(CONTAINER_NAME)
    container.start()

except:
    container = docker_client.containers.create(
        "python:latest",
        command="tail -f /dev/null",
        network_disabled=True,
        privileged=False,
        name=CONTAINER_NAME,
        restart_policy={"Name": "on-failure", "MaximumRetryCount": 3},
    )

