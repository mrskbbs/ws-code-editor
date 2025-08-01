import sys
import docker
import atexit
import docker.errors
from app.utils import logger
from app.config import CONTAINER_NAME, CONTAINER_USER 


docker_client = docker.from_env()
container = None


def createContainer(container):
    try: 
        container = docker_client.containers.create(
            "python:latest",
            command="tail -f /dev/null",
            network_disabled=True,
            privileged=False,
            name=CONTAINER_NAME,
            restart_policy={"Name": "on-failure", "MaximumRetryCount": 3},
        )
        container.start()
    
        commands = [
            f"useradd -m -s /bin/rbash {CONTAINER_USER}",
            f"deluser {CONTAINER_USER} sudo"
        ]

        joined_commands = " && ".join(commands)

        container.exec_run(
            cmd=f"bash -c '{joined_commands}'",
            user="root"
        )

    except docker.errors.DockerException as exc:
        logger.critical("Docker fatal error")
        logger.error(exc)
        sys.exit(1)


# Main logic
try:
    container = docker_client.containers.get(CONTAINER_NAME)
    
    if container.status == "running":
        container.restart()
    else:
        container.start()

except docker.errors.NotFound:
    logger.warning("Container not found, creating a new one")
    createContainer(container)

except docker.errors.DockerException as exc:
    logger.critical("Docker fatal error")
    logger.error(exc)
    sys.exit(1)

finally:
    atexit.register(lambda: container.kill())

