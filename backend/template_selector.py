from typing import Dict, Optional
from pathlib import Path
import json

class TemplateSelector:
    """
    Select and manage MCP templates
    Pure template system - NO LLM!
    """
    
    def __init__(self, templates_dir: str = "backend/templates"):
        self.templates_dir = Path(templates_dir)
        self.available_templates = self._load_available_templates()
    
    def _load_available_templates(self) -> Dict[str, Dict]:
        """Load all available templates"""
        
        return {
            "database_analyzer": {
                "name": "Database Analyzer",
                "description": "Analyzes database queries and performance",
                "type": "database",
                "languages": ["python"],
                "features": [
                    "query analysis",
                    "performance metrics",
                    "index suggestions",
                    "slow query detection"
                ],
                "base_file": "database_analyzer_template.py"
            },
            "api_monitor": {
                "name": "API Monitor",
                "description": "Monitors API endpoints and performance",
                "type": "api",
                "languages": ["python"],
                "features": [
                    "endpoint monitoring",
                    "response time analysis",
                    "error rate tracking",
                    "health checks"
                ],
                "base_file": "api_monitor_template.py"
            },
            "log_analyzer": {
                "name": "Log Analyzer",
                "description": "Analyzes application logs",
                "type": "logs",
                "languages": ["python"],
                "features": [
                    "log parsing",
                    "error detection",
                    "pattern matching",
                    "anomaly detection"
                ],
                "base_file": "log_analyzer_template.py"
            },
            "security_scanner": {
                "name": "Security Scanner",
                "description": "Scans for security vulnerabilities",
                "type": "security",
                "languages": ["python"],
                "features": [
                    "vulnerability scanning",
                    "secret detection",
                    "code analysis",
                    "compliance checks"
                ],
                "base_file": "security_scanner_template.py"
            },
            "performance_profiler": {
                "name": "Performance Profiler",
                "description": "Profiles application performance",
                "type": "performance",
                "languages": ["python"],
                "features": [
                    "cpu profiling",
                    "memory analysis",
                    "bottleneck detection",
                    "optimization suggestions"
                ],
                "base_file": "performance_profiler_template.py"
            },
            "generic_agent": {
                "name": "Generic Agent",
                "description": "Generic customizable agent",
                "type": "custom",
                "languages": ["python"],
                "features": [
                    "custom analysis",
                    "configurable logic",
                    "extensible framework"
                ],
                "base_file": "generic_agent_template.py"
            }
        }
    
    def select_template(self, template_name: str) -> Optional[Dict]:
        """Get template by name"""
        
        return self.available_templates.get(template_name)
    
    def get_templates_for_type(self, mcp_type: str) -> list:
        """Get all templates for specific MCP type"""
        
        matching = [
            (name, template)
            for name, template in self.available_templates.items()
            if template.get("type") == mcp_type
        ]
        
        return matching
    
    def get_template_content(self, template_name: str) -> str:
        """Read template file content"""
        
        template = self.available_templates.get(template_name)
        if not template:
            return ""
        
        template_file = self.templates_dir / template.get("base_file", "")
        
        if template_file.exists():
            return template_file.read_text()
        
        return ""
    
    def list_all_templates(self) -> list:
        """List all available templates"""
        
        return [
            {
                "name": name,
                "description": template.get("description"),
                "type": template.get("type"),
                "features": template.get("features", [])
            }
            for name, template in self.available_templates.items()
        ]