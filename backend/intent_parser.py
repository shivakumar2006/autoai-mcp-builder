class IntentParser:
    """
    parse user natural language requirements 
    map to mcp template + customization 
    """

    def __init__(self): 
        self.templates = {
            "database": "database_query_analyzer",
            "api": "api_performance_monitor",
            "logs": "logs_analysis_agent",
            "security": "security_scanner",
            "monitoring": "system_monitor",
        }

    def parse_requirements(self, user_input: str): 
        """
        parse user description and extract 
        1. what type of mcp (db, api, logs etc)
        2. what specific functionality 
        3. required inputs/outputs
        """

        keywords = {
            "database": ["database", "query", "sql", "mongodb", "postgress"],
            "api": ["api", "http", "endpoint", "rest", "graphql"],
            "logs": ["logs", "logging", "error", "trace", "debug"],
            "security": ["security", "vulnerability", "exploit", "auth"],
        }

        detected_type = None 
        for mcp_type, keyword_list in keywords.items():
            if any(kw in user_input.lower() for kw in keyword_list): 
                detected_type = mcp_type
                break 
        
        return {
            "mcp_type": detected_type or "generic",
            "requirements": user_input,
            "template": self.templates.get(detected_type),
            "customizations": self._extract_customizations(user_input)
        }
    
    def _extract_customization(self, user_input: str): 
        """extract specific customization from input"""
        return {
            "should scan for vulnerabilities": "security" in user_input.lower() or "vulnerable" in user_input.lower(),
            "should generate reports": "report" in user_input.lower(),
            "should send alerts": "alert" in user_input.lower()
        }