# Copy-paste into: backend/auto_deployer.py

import docker
import subprocess
import time
import os
from pathlib import Path
from typing import Dict, Optional, Callable

class AutoDeployer:
    """
    Automatically deploy generated MCP servers
    Build Docker image + Run container
    """
    
    def __init__(self, on_progress: Optional[Callable] = None):
        try:
            self.client = docker.from_env()
            self.docker_available = True
        except:
            self.docker_available = False
            print("⚠️  Docker not available")
        
        self.on_progress = on_progress or (lambda x: None)
        self.next_port = 8001
        self.deployed_containers = {}
    
    async def deploy_mcp_server(
        self,
        project_dir: str,
        mcp_name: str,
        mcp_id: str
    ) -> Dict:
        """
        Build and deploy generated MCP server
        """
        
        try:
            self.on_progress(f"🐳 Starting deployment of {mcp_name}...")
            
            if not self.docker_available:
                return {
                    "success": False,
                    "error": "Docker is not available"
                }
            
            # Step 1: Build Docker image
            self.on_progress(f"🔨 Building Docker image...")
            
            image_name = f"mcp-{mcp_id}:latest"
            
            try:
                self.client.images.build(
                    path=project_dir,
                    tag=image_name
                )
                self.on_progress(f"✅ Image built: {image_name}")
            except Exception as e:
                self.on_progress(f"❌ Build failed: {str(e)}")
                return {
                    "success": False,
                    "error": f"Docker build failed: {str(e)}"
                }
            
            # Step 2: Find available port
            self.on_progress(f"🔍 Finding available port...")
            port = self._find_available_port()
            self.on_progress(f"✅ Port assigned: {port}")
            
            # Step 3: Run container
            self.on_progress(f"🚀 Starting container...")
            
            try:
                container = self.client.containers.run(
                    image_name,
                    ports={'8000/tcp': port},
                    detach=True,
                    name=f"mcp-{mcp_id}-{int(time.time())}",
                    environment={
                        "MCP_ID": mcp_id,
                        "MCP_NAME": mcp_name
                    }
                )
                
                container_id = container.id[:12]
                self.on_progress(f"✅ Container started: {container_id}")
            
            except Exception as e:
                self.on_progress(f"❌ Container run failed: {str(e)}")
                return {
                    "success": False,
                    "error": f"Container run failed: {str(e)}"
                }
            
            # Step 4: Wait for health check
            self.on_progress(f"⏳ Waiting for container to be ready...")
            await self._wait_for_health(f"http://localhost:{port}", max_retries=10)
            
            endpoint = f"http://localhost:{port}"
            
            self.on_progress(f"✅ MCP Server is LIVE!")
            self.on_progress(f"📍 Endpoint: {endpoint}")
            
            # Store deployment info
            self.deployed_containers[mcp_id] = {
                "container_id": container_id,
                "port": port,
                "endpoint": endpoint,
                "image": image_name,
                "deployed_at": time.time()
            }
            
            return {
                "success": True,
                "mcp_id": mcp_id,
                "mcp_name": mcp_name,
                "container_id": container_id,
                "port": port,
                "endpoint": endpoint,
                "image": image_name,
                "status": "running"
            }
        
        except Exception as e:
            self.on_progress(f"❌ Deployment failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _wait_for_health(self, endpoint: str, max_retries: int = 10):
        """Wait for container health check"""
        
        import asyncio
        import httpx
        
        for retry in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{endpoint}/health")
                    if response.status_code == 200:
                        return True
            except:
                pass
            
            await asyncio.sleep(1)
        
        return False
    
    def _find_available_port(self) -> int:
        """Find next available port"""
        
        for port in range(self.next_port, 9000):
            try:
                result = subprocess.run(
                    f"lsof -i :{port}",
                    shell=True,
                    capture_output=True,
                    timeout=2
                )
                if result.returncode != 0:
                    self.next_port = port + 1
                    return port
            except:
                return port
        
        return self.next_port
    
    def stop_mcp_server(self, mcp_id: str) -> Dict:
        """Stop deployed MCP server"""
        
        if mcp_id not in self.deployed_containers:
            return {
                "success": False,
                "error": f"MCP {mcp_id} not found"
            }
        
        try:
            container_info = self.deployed_containers[mcp_id]
            container_id = container_info["container_id"]
            
            container = self.client.containers.get(container_id)
            container.stop()
            
            del self.deployed_containers[mcp_id]
            
            return {
                "success": True,
                "message": f"MCP {mcp_id} stopped"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_deployed_servers(self) -> list:
        """Get list of deployed MCP servers"""
        
        return [
            {
                "mcp_id": mcp_id,
                "endpoint": info["endpoint"],
                "port": info["port"],
                "container_id": info["container_id"]
            }
            for mcp_id, info in self.deployed_containers.items()
        ]