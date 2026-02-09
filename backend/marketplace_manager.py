# Copy-paste into: backend/marketplace_manager.py

from typing import List, Dict, Optional
from models import Agent, AgentStatus
from database import MongoDB
from datetime import datetime
import uuid

class MarketplaceManager:
    """Manage agent marketplace with MongoDB"""
    
    def __init__(self):
        self.agents_catalog = self._load_catalog()
        self.deployed_agents: Dict[str, Agent] = {}
    
    def _load_catalog(self) -> List[Agent]:
        """Load all available agents"""
        return [
            Agent(
                id="code_quality",
                name="Code Quality Analyzer",
                description="Analyzes code complexity, duplication, and quality metrics",
                template_path="agent_templates/code_quality_analyzer",
                tags=["analysis", "code", "quality"],
                dependencies=[]
            ),
            Agent(
                id="security",
                name="Security Scanner",
                description="Detects vulnerabilities, secrets, and security issues",
                template_path="agent_templates/security_scanner",
                tags=["security", "scanning", "vulnerabilities"],
                dependencies=[]
            ),
            Agent(
                id="performance",
                name="Performance Profiler",
                description="Profiles and optimizes application performance",
                template_path="agent_templates/performance_profiler",
                tags=["performance", "profiling", "optimization"],
                dependencies=["code_quality"]
            ),
            Agent(
                id="documentation",
                name="Documentation Generator",
                description="Auto-generates documentation from code",
                template_path="agent_templates/documentation_generator",
                tags=["documentation", "generation"],
                dependencies=["code_quality"]
            ),
            Agent(
                id="architecture",
                name="Architecture Analyzer",
                description="Analyzes system architecture and design patterns",
                template_path="agent_templates/architecture_analyzer",
                tags=["architecture", "patterns", "design"],
                dependencies=["code_quality"]
            ),
            Agent(
                id="test_coverage",
                name="Test Coverage Analyzer",
                description="Analyzes test coverage and identifies gaps",
                template_path="agent_templates/test_coverage_analyzer",
                tags=["testing", "coverage"],
                dependencies=[]
            ),
            Agent(
                id="dependencies",
                name="Dependency Scanner",
                description="Scans and analyzes dependencies and vulnerabilities",
                template_path="agent_templates/dependency_scanner",
                tags=["dependencies", "vulnerabilities"],
                dependencies=[]
            ),
            Agent(
                id="api_monitor",
                name="API Monitor",
                description="Monitors and analyzes API performance",
                template_path="agent_templates/api_monitor",
                tags=["api", "monitoring", "performance"],
                dependencies=[]
            ),
        ]
    
    def browse_agents(self, tags: List[str] = None) -> List[Dict]:
        """Browse available agents"""
        agents = self.agents_catalog
        
        if tags:
            agents = [
                a for a in agents 
                if any(tag in a.tags for tag in tags)
            ]
        
        return [
            {
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "tags": a.tags,
                "status": a.status.value,
                "dependencies": a.dependencies,
                "deployed": a.id in self.deployed_agents
            }
            for a in agents
        ]
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        for agent in self.agents_catalog:
            if agent.id == agent_id:
                return agent
        return None
    
    def get_deployed_agents(self) -> List[Dict]:
        """Get all deployed agents"""
        return [
            {
                "id": a.id,
                "name": a.name,
                "endpoint": a.endpoint,
                "port": a.port,
                "status": a.status.value,
                "container_id": a.container_id
            }
            for a in self.deployed_agents.values()
        ]
    
    def register_deployed_agent(self, agent: Agent):
        """Register deployed agent"""
        self.deployed_agents[agent.id] = agent
    
    def unregister_agent(self, agent_id: str):
        """Unregister agent"""
        if agent_id in self.deployed_agents:
            del self.deployed_agents[agent_id]
    
    async def save_deployment_to_db(self, agent_id: str, deployment_info: Dict):
        """Save deployment to MongoDB"""
        doc = {
            "deployment_id": str(uuid.uuid4()),
            "agent_id": agent_id,
            "container_id": deployment_info.get("container_id"),
            "port": deployment_info.get("port"),
            "endpoint": deployment_info.get("endpoint"),
            "status": deployment_info.get("status", "running"),
            "deployed_at": datetime.utcnow(),
            "metadata": deployment_info
        }
        
        result = await MongoDB.deployments.insert_one(doc)
        return result.inserted_id
    
    async def save_analysis_to_db(
        self, 
        analysis_id: str, 
        repo_url: str, 
        agents: List[str],
        results: Dict,
        final_report: Dict
    ):
        """Save analysis to MongoDB"""
        doc = {
            "analysis_id": analysis_id,
            "repo_url": repo_url,
            "agents": agents,
            "results": results,
            "final_report": final_report,
            "created_at": datetime.utcnow()
        }
        
        result = await MongoDB.analyses.insert_one(doc)
        return result.inserted_id
    
    async def get_analysis_history(self, limit: int = 10) -> List[Dict]:
        """Get analysis history from MongoDB"""
        cursor = MongoDB.analyses.find().sort("created_at", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def get_deployment_history(self, limit: int = 10) -> List[Dict]:
        """Get deployment history from MongoDB"""
        cursor = MongoDB.deployments.find().sort("deployed_at", -1).limit(limit)
        return await cursor.to_list(length=limit)