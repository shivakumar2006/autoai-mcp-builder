import docker 
import subprocess
import time 
from typing import Dict 

class AutoDeployer: 
    """automatically deploy generated server"""

    def __init__(self): 
        self.client = docker.from_any()
        self.deployed_servers: Dict[str, dict] = {}

    def deploy_mcp_server(self, code_dir: str, mcp_name: str) -> dict: 
        """deploy mcp server as docker container"""

        try: 
            #build docker image
            print(f"Building docker image for {mcp_name}...")
            image = self.client.images.build(
                path=code_dir,
                tag=f"mcp-{mcp_name}:latest"
            )
            print(f"✓ Image built: {image[0].tags}")

            # find available port 
            available_port = self._find_available_port(8001, 9000)
            print(f"✓ Using port: {available_port}")

            # run container
            print(f"Starting container")
            container = self.client.containers.run(
                f"mcp={mcp_name}:latest",
                ports={'8000/tcp': available_port},
                detach=True,
                name=f"mcp-{mcp_name}-{int(time.time())}"
            )
            print(f"✓ Container started: {container.id[:12]}")

            #wait for health check 
            time.sleep(3)

            # verify running 
            container.reload()
            is_running = container.status == "running"

            if is_running:
                endpoint = f"http://localhost:{available_port}"

                self.deployed_servers[mcp_name] = {
                    "container_id": container.id,
                    "port": available_port,
                    "endpoint": endpoint,
                    "status": "running"
                }

                return {
                    "success": True,
                    "mcp_name": mcp_name,
                    "container_id": container.id[:12],
                    "port": available_port,
                    "endpoint": endpoint,
                    "status": "running"
                }
            else:
                return {"success": False, "error": "Container failed to start"}
            
        except Exception as e: 
            return {"success": False, "error": str(e)}
        
    def _find_available_port(self, start: int, end: int) -> int: 
        """find available port in range"""

        for port in range(start, end):
            try:
                result = subprocess.run(
                    f"lsof -i :{port}",
                    shell=True,
                    capture_output=True
                )
                if result.returncode != 0:
                    return port
            except:
                continue
        raise Exception("No available ports")
