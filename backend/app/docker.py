import docker
import atexit
from app.config import CONTAINER_NAME, CONTAINER_USER 

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
    container.start()
    
    # TODO: some security can be done here 
    commands = [
        f"useradd -m -s /bin/rbash {CONTAINER_USER}",
        f"deluser {CONTAINER_USER} sudo"
    ]

    joined_commands = " && ".join(commands)

    container.exec_run(
        cmd=f"bash -c '{joined_commands}'",
        user="root"
    )

atexit.register(lambda: container.stop())