# Copy-paste into: backend/intent_parser.py

import re
from typing import Dict, List, Tuple
from enum import Enum

class MCPType(str, Enum):
    """Types of MCP servers we can generate"""
    DATABASE = "database"
    API = "api"
    LOGS = "logs"
    SECURITY = "security"
    PERFORMANCE = "performance"
    CUSTOM = "custom"

class IntentParser:
    """
    Parse user natural language input
    Extract intent without using any LLM!
    Pure keyword matching + regex
    """
    
    def __init__(self):
        # Define keywords for each MCP type
        self.type_keywords = {
            MCPType.DATABASE: [
                "database", "query", "sql", "mongodb", "postgres",
                "mysql", "elasticsearch", "redis", "cassandra",
                "schema", "table", "index", "optimize"
            ],
            MCPType.API: [
                "api", "http", "endpoint", "rest", "graphql",
                "response", "request", "status", "latency",
                "performance", "monitoring", "health"
            ],
            MCPType.LOGS: [
                "logs", "logging", "error", "trace", "debug",
                "event", "monitoring", "tracking", "audit",
                "syslog", "application log"
            ],
            MCPType.SECURITY: [
                "security", "vulnerability", "exploit", "auth",
                "password", "encryption", "ssl", "tls",
                "attack", "threat", "malware", "intrusion"
            ],
            MCPType.PERFORMANCE: [
                "performance", "speed", "optimize", "bottleneck",
                "profile", "benchmark", "latency", "throughput",
                "memory", "cpu", "cache", "efficiency"
            ]
        }
        
        # Define features/customizations
        self.feature_keywords = {
            "visualization": ["chart", "graph", "dashboard", "visual", "report"],
            "alerting": ["alert", "notification", "warning", "email", "slack"],
            "reporting": ["report", "summary", "analysis", "insights"],
            "real_time": ["real-time", "realtime", "live", "streaming", "instant"],
            "machine_learning": ["ml", "machine learning", "prediction", "ai"],
            "caching": ["cache", "caching", "redis", "memcached"]
        }
    
    def parse(self, user_input: str) -> Dict:
        """
        Parse user input and extract:
        1. MCP type
        2. Specific functionality
        3. Customizations
        4. Technologies mentioned
        """
        
        user_input_lower = user_input.lower()
        
        # Step 1: Detect MCP type
        detected_type = self._detect_mcp_type(user_input_lower)
        
        # Step 2: Extract specific requirements
        requirements = self._extract_requirements(user_input_lower, detected_type)
        
        # Step 3: Detect customizations
        customizations = self._detect_customizations(user_input_lower)
        
        # Step 4: Extract technologies mentioned
        technologies = self._extract_technologies(user_input_lower)
        
        # Step 5: Generate MCP name
        mcp_name = self._generate_mcp_name(user_input, detected_type)
        
        return {
            "mcp_type": detected_type,
            "mcp_name": mcp_name,
            "description": user_input,
            "requirements": requirements,
            "customizations": customizations,
            "technologies": technologies,
            "template": self._get_template_for_type(detected_type),
            "confidence": self._calculate_confidence(user_input_lower, detected_type)
        }
    
    def _detect_mcp_type(self, text: str) -> MCPType:
        """Detect which type of MCP server is needed"""
        
        scores = {}
        
        for mcp_type, keywords in self.type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            scores[mcp_type] = score
        
        # Return type with highest score
        detected_type = max(scores, key=scores.get)
        
        # Default to CUSTOM if no clear match
        if scores[detected_type] == 0:
            detected_type = MCPType.CUSTOM
        
        return detected_type
    
    def _extract_requirements(self, text: str, mcp_type: MCPType) -> List[str]:
        """Extract specific requirements based on type"""
        
        requirements = []
        
        if mcp_type == MCPType.DATABASE:
            # Database-specific requirements
            db_keywords = [
                ("optimize queries", "optimization"),
                ("analyze performance", "performance analysis"),
                ("detect slow queries", "slow query detection"),
                ("index suggestions", "index optimization"),
                ("query statistics", "statistics"),
                ("explain plan", "execution analysis")
            ]
            
            for pattern, requirement in db_keywords:
                if pattern in text:
                    requirements.append(requirement)
        
        elif mcp_type == MCPType.API:
            api_keywords = [
                ("response time", "response time monitoring"),
                ("error rate", "error rate tracking"),
                ("endpoint health", "endpoint health monitoring"),
                ("slow endpoints", "slow endpoint detection"),
                ("status codes", "status code analysis"),
                ("latency", "latency monitoring")
            ]
            
            for pattern, requirement in api_keywords:
                if pattern in text:
                    requirements.append(requirement)
        
        elif mcp_type == MCPType.SECURITY:
            security_keywords = [
                ("vulnerability", "vulnerability scanning"),
                ("secrets", "secret detection"),
                ("hardcoded", "hardcoded credential detection"),
                ("authentication", "authentication check"),
                ("encryption", "encryption verification"),
                ("ssl", "ssl/tls verification")
            ]
            
            for pattern, requirement in security_keywords:
                if pattern in text:
                    requirements.append(requirement)
        
        elif mcp_type == MCPType.LOGS:
            log_keywords = [
                ("error", "error detection"),
                ("anomaly", "anomaly detection"),
                ("pattern", "pattern matching"),
                ("filtering", "log filtering"),
                ("aggregation", "log aggregation"),
                ("correlation", "log correlation")
            ]
            
            for pattern, requirement in log_keywords:
                if pattern in text:
                    requirements.append(requirement)
        
        elif mcp_type == MCPType.PERFORMANCE:
            perf_keywords = [
                ("bottleneck", "bottleneck detection"),
                ("memory", "memory profiling"),
                ("cpu", "cpu profiling"),
                ("optimization", "performance optimization"),
                ("benchmark", "benchmarking"),
                ("profiling", "profiling")
            ]
            
            for pattern, requirement in perf_keywords:
                if pattern in text:
                    requirements.append(requirement)
        
        return requirements if requirements else ["basic analysis"]
    
    def _detect_customizations(self, text: str) -> Dict[str, bool]:
        """Detect additional customizations user wants"""
        
        customizations = {}
        
        for feature, keywords in self.feature_keywords.items():
            customizations[feature] = any(kw in text for kw in keywords)
        
        return customizations
    
    def _extract_technologies(self, text: str) -> List[str]:
        """Extract specific technologies mentioned"""
        
        tech_list = [
            "python", "javascript", "java", "go", "rust",
            "postgresql", "mongodb", "mysql", "elasticsearch",
            "kafka", "redis", "rabbitmq", "docker",
            "kubernetes", "aws", "gcp", "azure"
        ]
        
        found_techs = [tech for tech in tech_list if tech in text]
        
        return found_techs if found_techs else ["python"]
    
    def _generate_mcp_name(self, original_input: str, mcp_type: MCPType) -> str:
        """Generate a nice name for the MCP server"""
        
        # Extract important words from input
        words = re.findall(r'\b\w+\b', original_input.lower())
        
        # Remove common words
        common = {"i", "a", "an", "the", "for", "and", "or", "in", "on", "at"}
        words = [w for w in words if w not in common and len(w) > 2]
        
        if len(words) >= 2:
            name = " ".join(words[:3]).title()
        else:
            name = mcp_type.value.title() + " Analyzer"
        
        # Add "MCP" if not present
        if "mcp" not in name.lower():
            name += " MCP"
        
        return name
    
    def _get_template_for_type(self, mcp_type: MCPType) -> str:
        """Get template name for MCP type"""
        
        template_map = {
            MCPType.DATABASE: "database_analyzer",
            MCPType.API: "api_monitor",
            MCPType.LOGS: "log_analyzer",
            MCPType.SECURITY: "security_scanner",
            MCPType.PERFORMANCE: "performance_profiler",
            MCPType.CUSTOM: "generic_agent"
        }
        
        return template_map.get(mcp_type, "generic_agent")
    
    def _calculate_confidence(self, text: str, mcp_type: MCPType) -> float:
        """Calculate confidence in type detection (0-1)"""
        
        # Count keyword matches
        if mcp_type == MCPType.CUSTOM:
            return 0.6  # Lower confidence for custom
        
        keywords = self.type_keywords.get(mcp_type, [])
        matches = sum(1 for kw in keywords if kw in text)
        
        # Max confidence 0.95, min 0.7
        confidence = min(0.95, 0.7 + (matches * 0.05))
        
        return confidence