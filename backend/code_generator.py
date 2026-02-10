import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import uuid
import shutil

class CodeGenerator:
    """
    Generate actual MCP server code
    Uses templates + string replacement
    NO LLM!
    """
    
    def __init__(self, templates_dir: str = "backend/templates"):
        self.templates_dir = Path(templates_dir)
    
    async def generate_mcp_server(
        self,
        mcp_name: str,
        template_name: str,
        mcp_type: str,
        requirements: List[str],
        customizations: Dict[str, bool],
        technologies: List[str],
        on_progress=None
    ) -> Dict:
        """
        Generate complete MCP server
        Returns: path to generated code directory
        """
        
        on_progress = on_progress or (lambda x: None)
        
        try:
            on_progress("📝 Starting code generation...")
            
            # Step 1: Create temp directory
            on_progress("📁 Creating project directory...")
            temp_dir = tempfile.mkdtemp(prefix="mcp_")
            
            # Step 2: Load template
            on_progress(f"📚 Loading {template_name} template...")
            template_content = self._load_template(template_name)
            
            if not template_content:
                return {
                    "success": False,
                    "error": f"Template {template_name} not found"
                }
            
            # Step 3: Customize code
            on_progress("🎨 Customizing code...")
            customized_code = self._customize_code(
                template_content,
                mcp_name,
                mcp_type,
                requirements,
                customizations
            )
            
            # Step 4: Generate server.py
            on_progress("✍️  Generating server.py...")
            server_file = Path(temp_dir) / "server.py"
            server_file.write_text(customized_code)
            
            # Step 5: Generate requirements.txt
            on_progress("📦 Generating requirements.txt...")
            requirements_content = self._generate_requirements(
                mcp_type,
                technologies,
                customizations
            )
            requirements_file = Path(temp_dir) / "requirements.txt"
            requirements_file.write_text(requirements_content)
            
            # Step 6: Generate Dockerfile
            on_progress("🐳 Generating Dockerfile...")
            dockerfile_content = self._generate_dockerfile()
            dockerfile = Path(temp_dir) / "Dockerfile"
            dockerfile.write_text(dockerfile_content)
            
            # Step 7: Generate .dockerignore
            on_progress("📄 Generating .dockerignore...")
            dockerignore = Path(temp_dir) / ".dockerignore"
            dockerignore.write_text("__pycache__\n*.pyc\n.env\n.git\n")
            
            # Step 8: Generate config.json
            on_progress("⚙️  Generating config.json...")
            config_content = self._generate_config(
                mcp_name,
                mcp_type,
                requirements,
                customizations
            )
            config_file = Path(temp_dir) / "config.json"
            config_file.write_text(config_content)
            
            # Step 9: Generate README
            on_progress("📖 Generating README.md...")
            readme_content = self._generate_readme(
                mcp_name,
                mcp_type,
                requirements,
                customizations
            )
            readme_file = Path(temp_dir) / "README.md"
            readme_file.write_text(readme_content)
            
            on_progress("✅ Code generation complete!")
            
            return {
                "success": True,
                "mcp_name": mcp_name,
                "mcp_type": mcp_type,
                "project_dir": temp_dir,
                "files": self._list_files(temp_dir),
                "file_count": len(list(Path(temp_dir).glob("*")))
            }
        
        except Exception as e:
            on_progress(f"❌ Generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _load_template(self, template_name: str) -> Optional[str]:
        """Load template file"""
        
        template_map = {
            "database_analyzer": "database_analyzer_template.py",
            "api_monitor": "api_monitor_template.py",
            "log_analyzer": "log_analyzer_template.py",
            "security_scanner": "security_scanner_template.py",
            "performance_profiler": "performance_profiler_template.py",
            "generic_agent": "generic_agent_template.py"
        }
        
        template_file = template_map.get(template_name)
        if not template_file:
            return None
        
        template_path = self.templates_dir / template_file
        
        if template_path.exists():
            return template_path.read_text()
        
        # Return default template if not found
        return self._get_default_template()
    
    def _customize_code(
        self,
        template: str,
        mcp_name: str,
        mcp_type: str,
        requirements: List[str],
        customizations: Dict[str, bool]
    ) -> str:
        """Customize template with placeholders"""
        
        # Generate class name from MCP name
        class_name = "".join(word.capitalize() for word in mcp_name.split())
        
        # Replace placeholders
        code = template
        code = code.replace("{{MCP_NAME}}", mcp_name)
        code = code.replace("{{CLASS_NAME}}", class_name)
        code = code.replace("{{MCP_TYPE}}", mcp_type)
        
        # Add requirements as comments
        requirements_comment = "\n".join(f"# - {req}" for req in requirements)
        code = code.replace("{{REQUIREMENTS}}", requirements_comment)
        
        # Add customizations
        if customizations.get("visualization"):
            code += self._add_visualization_feature()
        
        if customizations.get("alerting"):
            code += self._add_alerting_feature()
        
        if customizations.get("reporting"):
            code += self._add_reporting_feature()
        
        if customizations.get("real_time"):
            code += self._add_realtime_feature()
        
        return code
    
    def _generate_requirements(
        self,
        mcp_type: str,
        technologies: List[str],
        customizations: Dict[str, bool]
    ) -> str:
        """Generate requirements.txt"""
        
        requirements = [
            "fastapi==0.109.0",
            "uvicorn==0.27.0",
            "pydantic==2.5.0",
            "httpx==0.25.0"
        ]
        
        # Add type-specific requirements
        if mcp_type == "database":
            requirements.extend([
                "sqlalchemy==2.0.23",
                "psycopg2-binary==2.9.9",
                "pymongo==4.6.0"
            ])
        elif mcp_type == "api":
            requirements.extend([
                "aiohttp==3.9.1",
                "httpx==0.25.0"
            ])
        elif mcp_type == "logs":
            requirements.extend([
                "python-json-logger==2.0.7",
                "elasticsearch==8.11.0"
            ])
        elif mcp_type == "security":
            requirements.extend([
                "bandit==1.7.5",
                "safety==2.3.5"
            ])
        elif mcp_type == "performance":
            requirements.extend([
                "psutil==5.9.6",
                "memory-profiler==0.61.0"
            ])
        
        # Add visualization if needed
        if customizations.get("visualization"):
            requirements.append("plotly==5.18.0")
        
        # Add caching if needed
        if customizations.get("caching"):
            requirements.append("redis==5.0.1")
        
        return "\n".join(requirements)
    
    def _generate_dockerfile(self) -> str:
        """Generate Dockerfile"""
        
        return """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    
    def _generate_config(
        self,
        mcp_name: str,
        mcp_type: str,
        requirements: List[str],
        customizations: Dict[str, bool]
    ) -> str:
        """Generate config.json"""
        
        import json
        
        config = {
            "name": mcp_name,
            "type": mcp_type,
            "version": "1.0.0",
            "requirements": requirements,
            "customizations": customizations,
            "endpoints": {
                "health": "/health",
                "analyze": "/analyze",
                "info": "/info"
            },
            "metadata": {
                "created_by": "AutoAI MCP Builder",
                "auto_generated": True
            }
        }
        
        return json.dumps(config, indent=2)
    
    def _generate_readme(
        self,
        mcp_name: str,
        mcp_type: str,
        requirements: List[str],
        customizations: Dict[str, bool]
    ) -> str:
        """Generate README.md"""
        
        readme = f"""# {mcp_name}

## Overview
Auto-generated MCP Server

**Type:** {mcp_type}  
**Generated by:** AutoAI MCP Builder

## Features
{chr(10).join(f"- {req}" for req in requirements)}

## Customizations
"""
        
        for key, value in customizations.items():
            if value:
                readme += f"- {key}: ✓\\n"
        
        readme += """
## Installation

### Build Docker Image
```bash
docker build -t {{mcp_name}} .
```

### Run Container
```bash
docker run -p 8000:8000 {{mcp_name}}
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Analyze
```bash
POST /analyze
Content-Type: application/json

{
  "data": "your data here"
}
```

### Info
```bash
GET /info
```

## Usage Example
```bash
curl -X POST http://localhost:8000/analyze \\
  -H "Content-Type: application/json" \\
  -d '{"data": "test"}'
```

## Auto-Generated

This MCP server was automatically generated by **AutoAI MCP Builder**.

No manual coding required!
"""
        
        return readme
    
    def _get_default_template(self) -> str:
        """Default template if file not found"""
        
        return '''
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

app = FastAPI(
    title="{{MCP_NAME}}",
    description="Auto-generated MCP Server",
    version="1.0.0"
)

class AnalysisRequest(BaseModel):
    data: Dict[str, Any]

class AnalysisResponse(BaseModel):
    status: str
    result: Dict[str, Any]
    timestamp: str

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "{{MCP_NAME}}",
        "type": "{{MCP_TYPE}}"
    }

@app.get("/info")
async def info():
    """Get service info"""
    return {
        "name": "{{MCP_NAME}}",
        "type": "{{MCP_TYPE}}",
        "version": "1.0.0",
        "requirements": [
            {{REQUIREMENTS}}
        ]
    }

@app.post("/analyze")
async def analyze(request: AnalysisRequest) -> AnalysisResponse:
    """Analyze data"""
    
    try:
        # Basic analysis
        result = {
            "input_keys": list(request.data.keys()),
            "data_type": type(request.data).__name__,
            "analysis": "Auto-generated analysis"
        }
        
        return AnalysisResponse(
            status="success",
            result=result,
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    def _add_visualization_feature(self) -> str:
        """Add visualization feature code"""
        
        return '''

# VISUALIZATION FEATURE
from fastapi.responses import HTMLResponse

@app.get("/visualize")
async def visualize():
    """Generate visualization"""
    
    html = """
    <html>
        <head>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        </head>
        <body>
            <div id="chart"></div>
            <script>
                // Visualization code here
            </script>
        </body>
    </html>
    """
    
    return HTMLResponse(content=html)
'''
    
    def _add_alerting_feature(self) -> str:
        """Add alerting feature code"""
        
        return '''

# ALERTING FEATURE
import asyncio

async def send_alert(message: str, level: str = "info"):
    """Send alert notification"""
    
    # Implementation here
    print(f"[{level.upper()}] {message}")
'''
    
    def _add_reporting_feature(self) -> str:
        """Add reporting feature code"""
        
        return '''

# REPORTING FEATURE
from datetime import datetime

def generate_report(data: Dict) -> Dict:
    """Generate analysis report"""
    
    report = {
        "generated_at": datetime.utcnow().isoformat(),
        "summary": "Auto-generated report",
        "data": data
    }
    
    return report
'''
    
    def _add_realtime_feature(self) -> str:
        """Add real-time feature code"""
        
        return '''

# REAL-TIME FEATURE
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            # Process and send back
            await websocket.send_text(f"Received: {data}")
    
    except Exception as e:
        await websocket.close()
'''
    
    def _list_files(self, directory: str) -> list:
        """List generated files"""
        
        files = []
        for file_path in Path(directory).glob("*"):
            if file_path.is_file():
                files.append({
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "type": file_path.suffix
                })
        
        return files