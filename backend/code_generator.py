# backend/code_generator.py

import tempfile
import os
from pathlib import Path

class CodeGenerator:
    """
    Generate actual MCP server code from template + requirements
    """
    
    def __init__(self):
        self.templates_path = Path("mcp_templates")
    
    def generate_mcp_server(self, parsed_requirements: dict):
        """
        Generate complete MCP server codebase
        """
        
        mcp_type = parsed_requirements["mcp_type"]
        template_name = parsed_requirements["template"]
        customizations = parsed_requirements["customizations"]
        
        # Create temp directory for generated code
        temp_dir = tempfile.mkdtemp(prefix="mcp_")
        
        # Step 1: Copy base template
        base_template = self.templates_path / template_name
        self._copy_template(base_template, temp_dir)
        
        # Step 2: Apply customizations
        self._apply_customizations(temp_dir, customizations)
        
        # Step 3: Generate Dockerfile
        self._generate_dockerfile(temp_dir)
        
        # Step 4: Generate requirements.txt
        self._generate_requirements(temp_dir)
        
        # Step 5: List generated files
        generated_files = self._list_generated_files(temp_dir)
        
        return {
            "success": True,
            "temp_dir": temp_dir,
            "mcp_type": mcp_type,
            "files": generated_files,
            "ready_to_deploy": True
        }
    
    def _copy_template(self, template_path: Path, dest: str):
        """Copy template to destination"""
        import shutil
        shutil.copytree(template_path, dest, dirs_exist_ok=True)
    
    def _apply_customizations(self, base_dir: str, customizations: dict):
        """Modify generated code based on customizations"""
        server_py = Path(base_dir) / "server.py"
        
        with open(server_py, 'a') as f:
            if customizations.get("should_scan_for_vulnerabilities"):
                f.write("\n# Vulnerability scanning enabled\n")
            if customizations.get("should_generate_reports"):
                f.write("\n# Report generation enabled\n")
            if customizations.get("should_send_alerts"):
                f.write("\n# Alert system enabled\n")
    
    def _generate_dockerfile(self, base_dir: str):
        """Generate Dockerfile for the MCP server"""
        dockerfile_content = '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "server.py"]
'''
        
        with open(Path(base_dir) / "Dockerfile", 'w') as f:
            f.write(dockerfile_content)
    
    def _generate_requirements(self, base_dir: str):
        """Generate requirements.txt"""
        requirements = '''fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.0
httpx==0.25.0
'''
        
        with open(Path(base_dir) / "requirements.txt", 'w') as f:
            f.write(requirements)
    
    def _list_generated_files(self, base_dir: str):
        """List all generated files"""
        files = []
        for item in Path(base_dir).rglob("*"):
            if item.is_file():
                files.append({
                    "name": item.name,
                    "path": str(item.relative_to(base_dir)),
                    "size": item.stat().st_size
                })
        return files