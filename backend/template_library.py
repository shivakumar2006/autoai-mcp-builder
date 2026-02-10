"""
Template Library - 6 Ready-to-Use MCP Templates
NO LLM - Pure Python templates with placeholders
"""

class TemplateLibrary:
    """Store all MCP templates"""
    
    @staticmethod
    def database_analyzer_template() -> str:
        """Template for Database Analyzer MCP"""
        
        return '''
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any
from datetime import datetime
import re

app = FastAPI(
    title="{{MCP_NAME}}",
    description="Database Query Analyzer",
    version="1.0.0"
)

class QueryAnalysisRequest(BaseModel):
    query: str
    database_type: str = "sql"
    connection_params: Dict = {}

class QueryAnalysisResponse(BaseModel):
    status: str
    analysis: Dict[str, Any]
    timestamp: str

class DatabaseAnalyzer:
    """Analyze database queries - NO LLM!"""
    
    def __init__(self):
        self.slow_query_threshold = 1000  # ms
    
    async def analyze_query(self, query: str, db_type: str) -> Dict:
        """
        Analyze SQL query
        Pure logic analysis - NO AI!
        """
        
        analysis = {
            "query": query,
            "database_type": db_type,
            "complexity": self._analyze_complexity(query),
            "performance_metrics": self._extract_metrics(query),
            "optimization_suggestions": self._suggest_optimizations(query),
            "indexes_recommended": self._recommend_indexes(query),
            "potential_issues": self._detect_issues(query),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return analysis
    
    def _analyze_complexity(self, query: str) -> Dict:
        """Analyze query complexity"""
        
        query_upper = query.upper()
        
        complexity_score = 0
        
        # Count JOINs
        joins = len(re.findall(r'\\bJOIN\\b', query_upper))
        complexity_score += joins * 2
        
        # Count WHERE conditions
        where_conditions = len(re.findall(r'\\bAND\\b|\\bOR\\b', query_upper))
        complexity_score += where_conditions
        
        # Count subqueries
        subqueries = query.count('(SELECT')
        complexity_score += subqueries * 3
        
        # Count GROUP BY
        if 'GROUP BY' in query_upper:
            complexity_score += 1
        
        # Count ORDER BY
        if 'ORDER BY' in query_upper:
            complexity_score += 1
        
        return {
            "score": min(complexity_score, 10),
            "joins": joins,
            "conditions": where_conditions,
            "subqueries": subqueries,
            "level": "high" if complexity_score > 5 else "medium" if complexity_score > 2 else "low"
        }
    
    def _extract_metrics(self, query: str) -> Dict:
        """Extract query metrics"""
        
        query_upper = query.upper()
        
        return {
            "type": self._detect_query_type(query),
            "tables_involved": len(re.findall(r'\\bFROM\\s+(\\w+)', query_upper)),
            "columns_selected": query.count(',') + 1 if 'SELECT' in query_upper else 0,
            "estimated_rows": "unknown",
            "execution_plan": "not available without execution"
        }
    
    def _suggest_optimizations(self, query: str) -> List[str]:
        """Suggest query optimizations"""
        
        suggestions = []
        query_upper = query.upper()
        
        # Check for SELECT *
        if 'SELECT *' in query_upper:
            suggestions.append("Avoid SELECT * - specify needed columns only")
        
        # Check for functions in WHERE
        if re.search(r'WHERE.*\\(', query):
            suggestions.append("Avoid functions in WHERE clause - use indexes")
        
        # Check for LIKE with leading %
        if "LIKE '%%" in query_upper:
            suggestions.append("Leading % in LIKE is slow - consider full-text search")
        
        # Check for missing WHERE
        if 'DELETE' in query_upper and 'WHERE' not in query_upper:
            suggestions.append("CRITICAL: DELETE without WHERE clause detected!")
        
        # Check for UPDATE without WHERE
        if 'UPDATE' in query_upper and 'WHERE' not in query_upper:
            suggestions.append("CRITICAL: UPDATE without WHERE clause detected!")
        
        # Check for IN with many values
        in_count = len(re.findall(r'IN\\s*\\(', query))
        if in_count > 0:
            values = re.findall(r'IN\\s*\\((.*?)\\)', query)
            if values and len(values[0].split(',')) > 10:
                suggestions.append("Large IN clause detected - consider JOIN instead")
        
        return suggestions if suggestions else ["Query looks optimized"]
    
    def _recommend_indexes(self, query: str) -> List[str]:
        """Recommend indexes"""
        
        recommendations = []
        query_upper = query.upper()
        
        # Extract WHERE columns
        where_match = re.search(r'WHERE\\s+(.*?)(?:GROUP|ORDER|LIMIT|$)', query_upper)
        if where_match:
            where_clause = where_match.group(1)
            # Simple: recommend indexing columns in WHERE
            columns = re.findall(r'(\\w+)\\s*[=<>]', where_clause)
            for col in columns[:3]:  # Top 3
                recommendations.append(f"CREATE INDEX idx_{col} ON table({col})")
        
        # Extract JOIN columns
        join_columns = re.findall(r'ON\\s+(\\w+)\\.(\\w+)\\s*=', query)
        for table, col in join_columns[:2]:
            recommendations.append(f"CREATE INDEX idx_{col} ON {table}({col})")
        
        return recommendations if recommendations else ["No immediate index needs detected"]
    
    def _detect_issues(self, query: str) -> List[str]:
        """Detect potential issues"""
        
        issues = []
        query_upper = query.upper()
        
        # Check for dangerous operations
        if 'DROP' in query_upper:
            issues.append("CRITICAL: DROP detected - ensure this is intentional")
        
        if 'TRUNCATE' in query_upper:
            issues.append("CRITICAL: TRUNCATE detected - will delete all data")
        
        if query.count(';') > 1:
            issues.append("Multiple statements detected - ensure this is intentional")
        
        # Check for N+1 pattern
        if 'SELECT' in query_upper and 'WHERE' in query_upper:
            if query_upper.count('SELECT') > 1:
                issues.append("Possible N+1 query pattern detected")
        
        return issues
    
    def _detect_query_type(self, query: str) -> str:
        """Detect query type"""
        
        query_upper = query.upper().strip()
        
        if query_upper.startswith('SELECT'):
            return 'SELECT'
        elif query_upper.startswith('INSERT'):
            return 'INSERT'
        elif query_upper.startswith('UPDATE'):
            return 'UPDATE'
        elif query_upper.startswith('DELETE'):
            return 'DELETE'
        else:
            return 'UNKNOWN'

analyzer = DatabaseAnalyzer()

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "{{MCP_NAME}}",
        "type": "database_analyzer"
    }

@app.get("/info")
async def info():
    return {
        "name": "{{MCP_NAME}}",
        "type": "database_analyzer",
        "features": [
            "Query complexity analysis",
            "Performance metrics",
            "Optimization suggestions",
            "Index recommendations",
            "Issue detection"
        ]
    }

@app.post("/analyze")
async def analyze(request: QueryAnalysisRequest) -> QueryAnalysisResponse:
    """Analyze database query"""
    
    try:
        analysis = await analyzer.analyze_query(
            request.query,
            request.database_type
        )
        
        return QueryAnalysisResponse(
            status="success",
            analysis=analysis,
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    @staticmethod
    def api_monitor_template() -> str:
        """Template for API Monitor MCP"""
        
        return '''
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any
from datetime import datetime
import time
import re

app = FastAPI(
    title="{{MCP_NAME}}",
    description="API Performance Monitor",
    version="1.0.0"
)

class APIRequest(BaseModel):
    endpoint: str
    method: str
    response_time: float
    status_code: int
    error: str = None

class APIAnalysisResponse(BaseModel):
    status: str
    analysis: Dict[str, Any]
    timestamp: str

class APIMonitor:
    """Monitor API performance - NO LLM!"""
    
    def __init__(self):
        self.response_time_threshold = 1000  # ms
        self.error_rate_threshold = 5  # percent
    
    async def analyze_endpoints(self, endpoints: List[Dict]) -> Dict:
        """Analyze multiple API endpoints"""
        
        analysis = {
            "total_endpoints": len(endpoints),
            "healthy_endpoints": 0,
            "slow_endpoints": [],
            "error_endpoints": [],
            "performance_metrics": self._calculate_metrics(endpoints),
            "recommendations": self._generate_recommendations(endpoints),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for endpoint in endpoints:
            if endpoint.get('status_code', 200) >= 400:
                analysis["error_endpoints"].append(endpoint)
            elif endpoint.get('response_time', 0) > self.response_time_threshold:
                analysis["slow_endpoints"].append(endpoint)
            else:
                analysis["healthy_endpoints"] += 1
        
        return analysis
    
    def _calculate_metrics(self, endpoints: List[Dict]) -> Dict:
        """Calculate performance metrics"""
        
        if not endpoints:
            return {}
        
        response_times = [e.get('response_time', 0) for e in endpoints]
        status_codes = [e.get('status_code', 200) for e in endpoints]
        
        errors = sum(1 for code in status_codes if code >= 400)
        error_rate = (errors / len(endpoints)) * 100 if endpoints else 0
        
        return {
            "avg_response_time": sum(response_times) / len(response_times),
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "error_rate": round(error_rate, 2),
            "uptime_percent": 100 - error_rate
        }
    
    def _generate_recommendations(self, endpoints: List[Dict]) -> List[str]:
        """Generate recommendations"""
        
        recommendations = []
        
        slow_count = sum(1 for e in endpoints if e.get('response_time', 0) > 1000)
        if slow_count > len(endpoints) * 0.2:
            recommendations.append("More than 20% endpoints are slow - consider optimization")
        
        error_count = sum(1 for e in endpoints if e.get('status_code', 200) >= 400)
        if error_count > 0:
            recommendations.append(f"{error_count} endpoints returning errors")
        
        if not recommendations:
            recommendations.append("All endpoints performing well")
        
        return recommendations

monitor = APIMonitor()

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "{{MCP_NAME}}"
    }

@app.post("/analyze")
async def analyze(endpoints: List[APIRequest]) -> APIAnalysisResponse:
    """Analyze API endpoints"""
    
    try:
        endpoints_data = [e.dict() for e in endpoints]
        analysis = await monitor.analyze_endpoints(endpoints_data)
        
        return APIAnalysisResponse(
            status="success",
            analysis=analysis,
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    @staticmethod
    def security_scanner_template() -> str:
        """Template for Security Scanner MCP"""
        
        return '''
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any
from datetime import datetime
import re

app = FastAPI(
    title="{{MCP_NAME}}",
    description="Security Vulnerability Scanner",
    version="1.0.0"
)

class SecurityScanRequest(BaseModel):
    code: str
    language: str = "python"

class SecurityScanResponse(BaseModel):
    status: str
    vulnerabilities: List[Dict]
    severity_score: float
    timestamp: str

class SecurityScanner:
    """Scan for security vulnerabilities - NO LLM!"""
    
    def __init__(self):
        self.vulnerability_patterns = {
            "sql_injection": r"(SELECT|INSERT|UPDATE|DELETE).*?\\$|\\?.*?(OR|AND).*?1.*?=.*?1",
            "hardcoded_password": r"password\\s*=\\s*['\\\"].*?['\\\"]",
            "hardcoded_api_key": r"(api_key|apikey|secret|token)\\s*=\\s*['\\\"].*?['\\\"]",
            "eval_usage": r"eval\\s*\\(",
            "exec_usage": r"exec\\s*\\(",
            "unsafe_pickle": r"pickle\\.(loads|load)",
            "insecure_random": r"random\\.random\\(\\)|import random",
            "weak_hash": r"(md5|sha1)\\(",
            "hardcoded_url": r"https?://[a-zA-Z0-9.-]+\\.[a-z]{2,}"
        }
    
    async def scan_code(self, code: str, language: str) -> Dict:
        """Scan code for vulnerabilities"""
        
        vulnerabilities = []
        
        for vuln_type, pattern in self.vulnerability_patterns.items():
            matches = re.finditer(pattern, code, re.IGNORECASE)
            
            for match in matches:
                line_num = code[:match.start()].count('\\n') + 1
                
                vulnerabilities.append({
                    "type": vuln_type,
                    "line": line_num,
                    "code_snippet": match.group()[:50],
                    "severity": self._calculate_severity(vuln_type),
                    "recommendation": self._get_recommendation(vuln_type)
                })
        
        # Additional checks
        if language == "python":
            vulnerabilities.extend(self._check_python_specific(code))
        
        return {
            "total_vulnerabilities": len(vulnerabilities),
            "vulnerabilities": vulnerabilities,
            "severity_score": self._calculate_score(vulnerabilities),
            "status": "secure" if len(vulnerabilities) == 0 else "vulnerable",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _check_python_specific(self, code: str) -> List[Dict]:
        """Check Python-specific issues"""
        
        issues = []
        
        # Check for os.system
        if re.search(r'os\\.system\\(', code):
            issues.append({
                "type": "os_system_usage",
                "severity": "high",
                "recommendation": "Use subprocess module instead"
            })
        
        # Check for subprocess without shell=False
        if re.search(r'subprocess\\..*shell\\s*=\\s*True', code):
            issues.append({
                "type": "unsafe_subprocess",
                "severity": "high",
                "recommendation": "Use shell=False to prevent shell injection"
            })
        
        return issues
    
    def _calculate_severity(self, vuln_type: str) -> str:
        """Calculate vulnerability severity"""
        
        critical = ["sql_injection", "eval_usage", "exec_usage"]
        high = ["hardcoded_password", "hardcoded_api_key", "unsafe_pickle"]
        medium = ["weak_hash", "insecure_random"]
        
        if vuln_type in critical:
            return "critical"
        elif vuln_type in high:
            return "high"
        elif vuln_type in medium:
            return "medium"
        else:
            return "low"
    
    def _get_recommendation(self, vuln_type: str) -> str:
        """Get fix recommendation"""
        
        recommendations = {
            "sql_injection": "Use parameterized queries",
            "hardcoded_password": "Use environment variables",
            "hardcoded_api_key": "Store in secure vault",
            "eval_usage": "Avoid eval - use safer alternatives",
            "exec_usage": "Avoid exec - use safer alternatives",
            "unsafe_pickle": "Use json instead",
            "insecure_random": "Use secrets module",
            "weak_hash": "Use SHA256 or bcrypt"
        }
        
        return recommendations.get(vuln_type, "Review this code pattern")
    
    def _calculate_score(self, vulnerabilities: List[Dict]) -> float:
        """Calculate overall severity score (0-10)"""
        
        if not vulnerabilities:
            return 0.0
        
        severity_map = {"critical": 3, "high": 2, "medium": 1, "low": 0.5}
        score = sum(severity_map.get(v.get("severity", "low"), 0.5) for v in vulnerabilities)
        
        return min(10.0, score)

scanner = SecurityScanner()

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/analyze")
async def analyze(request: SecurityScanRequest) -> SecurityScanResponse:
    """Scan code for security issues"""
    
    try:
        analysis = await scanner.scan_code(request.code, request.language)
        
        return SecurityScanResponse(
            status="success",
            vulnerabilities=analysis.get("vulnerabilities", []),
            severity_score=analysis.get("severity_score", 0),
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    @staticmethod
    def log_analyzer_template() -> str:
        """Template for Log Analyzer MCP"""
        
        return '''
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any
from datetime import datetime
import re
from collections import Counter

app = FastAPI(
    title="{{MCP_NAME}}",
    description="Application Log Analyzer",
    version="1.0.0"
)

class LogAnalysisRequest(BaseModel):
    logs: List[str]
    log_format: str = "plain"

class LogAnalysisResponse(BaseModel):
    status: str
    analysis: Dict[str, Any]
    timestamp: str

class LogAnalyzer:
    """Analyze application logs - NO LLM!"""
    
    def __init__(self):
        self.error_keywords = ["error", "exception", "failed", "critical", "panic"]
        self.warning_keywords = ["warning", "warn", "deprecated", "retry"]
    
    async def analyze_logs(self, logs: List[str]) -> Dict:
        """Analyze logs"""
        
        analysis = {
            "total_lines": len(logs),
            "error_count": 0,
            "warning_count": 0,
            "info_count": 0,
            "top_errors": [],
            "patterns": self._extract_patterns(logs),
            "timeline": self._extract_timeline(logs),
            "insights": self._generate_insights(logs),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for log in logs:
            log_lower = log.lower()
            
            if any(kw in log_lower for kw in self.error_keywords):
                analysis["error_count"] += 1
            elif any(kw in log_lower for kw in self.warning_keywords):
                analysis["warning_count"] += 1
            else:
                analysis["info_count"] += 1
        
        # Extract top errors
        error_logs = [log for log in logs if any(kw in log.lower() for kw in self.error_keywords)]
        analysis["top_errors"] = self._extract_top_errors(error_logs)[:5]
        
        return analysis
    
    def _extract_patterns(self, logs: List[str]) -> List[Dict]:
        """Extract recurring patterns"""
        
        patterns = []
        
        # Extract error messages
        error_msgs = []
        for log in logs:
            match = re.search(r'(Error|Exception|Failed):\\s*(.+?)($|\\n)', log, re.IGNORECASE)
            if match:
                error_msgs.append(match.group(2))
        
        # Find most common errors
        if error_msgs:
            error_counter = Counter(error_msgs)
            for error, count in error_counter.most_common(5):
                patterns.append({
                    "type": "error",
                    "message": error[:100],
                    "occurrences": count
                })
        
        return patterns
    
    def _extract_timeline(self, logs: List[str]) -> Dict:
        """Extract timeline information"""
        
        timestamps = []
        
        for log in logs:
            match = re.search(r'\\d{2}:\\d{2}:\\d{2}', log)
            if match:
                timestamps.append(match.group())
        
        return {
            "first_log": timestamps[0] if timestamps else "unknown",
            "last_log": timestamps[-1] if timestamps else "unknown",
            "log_entries": len(logs)
        }
    
    def _extract_top_errors(self, error_logs: List[str]) -> List[Dict]:
        """Extract top errors"""
        
        errors = []
        
        for idx, log in enumerate(error_logs):
            errors.append({
                "index": idx,
                "log": log[:200],
                "severity": self._calculate_severity(log)
            })
        
        return sorted(errors, key=lambda x: x["severity"], reverse=True)
    
    def _calculate_severity(self, log: str) -> int:
        """Calculate log severity"""
        
        severity = 1
        
        if any(kw in log.lower() for kw in ["critical", "fatal", "panic"]):
            severity = 10
        elif any(kw in log.lower() for kw in ["error", "exception"]):
            severity = 7
        elif "warning" in log.lower():
            severity = 3
        
        return severity
    
    def _generate_insights(self, logs: List[str]) -> List[str]:
        """Generate insights from logs"""
        
        insights = []
        
        total = len(logs)
        error_count = sum(1 for log in logs if any(kw in log.lower() for kw in self.error_keywords))
        error_rate = (error_count / total) * 100 if total > 0 else 0
        
        if error_rate > 50:
            insights.append("High error rate detected - investigate immediately")
        elif error_rate > 20:
            insights.append("Elevated error rate - review recent changes")
        
        if any("timeout" in log.lower() for log in logs):
            insights.append("Timeout errors detected - check service health")
        
        if any("out of memory" in log.lower() for log in logs):
            insights.append("Memory issues detected - check resource usage")
        
        if not insights:
            insights.append("Logs appear normal")
        
        return insights

analyzer = LogAnalyzer()

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/analyze")
async def analyze(request: LogAnalysisRequest) -> LogAnalysisResponse:
    """Analyze logs"""
    
    try:
        analysis = await analyzer.analyze_logs(request.logs)
        
        return LogAnalysisResponse(
            status="success",
            analysis=analysis,
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    @staticmethod
    def performance_profiler_template() -> str:
        """Template for Performance Profiler MCP"""
        
        return '''
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any
from datetime import datetime

app = FastAPI(
    title="{{MCP_NAME}}",
    description="Performance Profiler",
    version="1.0.0"
)

class PerformanceMetrics(BaseModel):
    metric_name: str
    value: float
    unit: str

class PerformanceAnalysisResponse(BaseModel):
    status: str
    analysis: Dict[str, Any]
    timestamp: str

class PerformanceProfiler:
    """Profile performance - NO LLM!"""
    
    def __init__(self):
        self.cpu_threshold = 80  # percent
        self.memory_threshold = 85  # percent
        self.latency_threshold = 1000  # ms
    
    async def analyze_performance(self, metrics: List[PerformanceMetrics]) -> Dict:
        """Analyze performance metrics"""
        
        analysis = {
            "total_metrics": len(metrics),
            "bottlenecks": [],
            "optimization_opportunities": [],
            "health_score": self._calculate_health_score(metrics),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for metric in metrics:
            if "cpu" in metric.metric_name.lower():
                if metric.value > self.cpu_threshold:
                    analysis["bottlenecks"].append({
                        "metric": metric.metric_name,
                        "value": metric.value,
                        "recommendation": "Optimize CPU usage"
                    })
            
            elif "memory" in metric.metric_name.lower():
                if metric.value > self.memory_threshold:
                    analysis["bottlenecks"].append({
                        "metric": metric.metric_name,
                        "value": metric.value,
                        "recommendation": "Check for memory leaks"
                    })
            
            elif "latency" in metric.metric_name.lower():
                if metric.value > self.latency_threshold:
                    analysis["bottlenecks"].append({
                        "metric": metric.metric_name,
                        "value": metric.value,
                        "recommendation": "Optimize slow operations"
                    })
        
        # Generate recommendations
        if analysis["bottlenecks"]:
            analysis["optimization_opportunities"] = [
                "Profile hotspots",
                "Implement caching",
                "Optimize database queries",
                "Use async operations"
            ]
        
        return analysis
    
    def _calculate_health_score(self, metrics: List[PerformanceMetrics]) -> float:
        """Calculate overall health score"""
        
        if not metrics:
            return 100.0
        
        score = 100.0
        
        for metric in metrics:
            if "cpu" in metric.metric_name.lower():
                score -= (metric.value - 50) * 0.5
            elif "memory" in metric.metric_name.lower():
                score -= (metric.value - 50) * 0.5
        
        return max(0.0, min(100.0, score))

profiler = PerformanceProfiler()

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/analyze")
async def analyze(metrics: List[PerformanceMetrics]) -> PerformanceAnalysisResponse:
    """Analyze performance"""
    
    try:
        analysis = await profiler.analyze_performance(metrics)
        
        return PerformanceAnalysisResponse(
            status="success",
            analysis=analysis,
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    @staticmethod
    def generic_agent_template() -> str:
        """Generic template for custom agents"""
        
        return '''
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

app = FastAPI(
    title="{{MCP_NAME}}",
    description="Generic Custom Agent",
    version="1.0.0"
)

class AnalysisRequest(BaseModel):
    data: Dict[str, Any]
    config: Dict[str, Any] = {}

class AnalysisResponse(BaseModel):
    status: str
    result: Dict[str, Any]
    timestamp: str

class CustomAgent:
    """Custom analysis agent - Fully customizable"""
    
    async def analyze(self, data: Dict[str, Any], config: Dict[str, Any]) -> Dict:
        """Perform custom analysis"""
        
        return {
            "input_keys": list(data.keys()),
            "analysis": "Custom analysis implementation",
            "config_used": config,
            "status": "success"
        }

agent = CustomAgent()

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "{{MCP_NAME}}"}

@app.get("/info")
async def info():
    return {
        "name": "{{MCP_NAME}}",
        "type": "custom_agent",
        "version": "1.0.0"
    }

@app.post("/analyze")
async def analyze(request: AnalysisRequest) -> AnalysisResponse:
    """Perform analysis"""
    
    try:
        result = await agent.analyze(request.data, request.config)
        
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

# Store templates as static content
TEMPLATES = {
    "database_analyzer": database_analyzer_template(),
    "api_monitor": api_monitor_template(),
    "log_analyzer": log_analyzer_template(),
    "security_scanner": security_scanner_template(),
    "performance_profiler": performance_profiler_template(),
    "generic_agent": generic_agent_template()
}