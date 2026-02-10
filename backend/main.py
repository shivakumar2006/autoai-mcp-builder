# Copy-paste into: backend/main.py (COMPLETE REWRITE)

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from typing import List, Optional
from datetime import datetime
import uuid

from models import (
    Agent, DeploymentRequest, OrchestrationRequest, 
    AgentStatus
)
from orchestrator_engine import OrchestratorEngine
from websocket_manager import ConnectionManager, MessageBroadcaster
from database import connect_to_mongo, close_mongo_connection, MongoDB
from intent_parser import IntentParser
from template_selector import TemplateSelector
from code_generator import CodeGenerator
from auto_deployer import AutoDeployer
from mcp_manager import MCPManager
from archestra_integration import ArchestraIntegration

# Initialize app
app = FastAPI(
    title="AutoAI MCP Builder",
    description="Auto-generate and deploy MCP servers",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
connection_manager = ConnectionManager()
broadcaster = None
orchestrator_engine = None

# AutoAI specific managers
intent_parser = IntentParser()
template_selector = TemplateSelector()
code_generator = CodeGenerator()
auto_deployer = AutoDeployer()
mcp_manager = MCPManager()
archestra = ArchestraIntegration()

# Track generation tasks
generation_tasks: dict = {}

# ==================== STARTUP & SHUTDOWN ====================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    global orchestrator_engine, broadcaster
    
    # Connect to MongoDB
    await connect_to_mongo()
    
    # Initialize orchestrator
    async def broadcast_fn(message):
        if broadcaster:
            await broadcaster.manager.broadcast(message)
    
    orchestrator_engine = OrchestratorEngine(broadcast_fn=broadcast_fn)
    broadcaster = MessageBroadcaster(connection_manager)
    
    print("✅ AutoAI MCP Builder Started")
    print(f"✅ MongoDB connected")
    print(f"✅ Ready to generate MCPs!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    from database import close_mongo_connection
    await close_mongo_connection()

# ==================== HEALTH & INFO ====================

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "AutoAI MCP Builder",
        "timestamp": datetime.utcnow().isoformat(),
        "connections": connection_manager.get_connection_count()
    }

@app.get("/info")
async def info():
    """Service info"""
    
    mcps = await mcp_manager.list_mcps()
    
    return {
        "name": "AutoAI MCP Builder",
        "version": "1.0.0",
        "description": "Auto-generate and deploy MCP servers",
        "features": [
            "Intent parsing (NO LLM!)",
            "Template-based code generation",
            "Auto Docker build & deploy",
            "Real-time progress updates",
            "Archestra integration"
        ],
        "generated_mcps": len(mcps),
        "supported_types": [
            "database_analyzer",
            "api_monitor",
            "log_analyzer",
            "security_scanner",
            "performance_profiler",
            "custom_agent"
        ]
    }

# ==================== GENERATION ENDPOINTS ====================

@app.post("/api/generate-mcp")
async def generate_mcp(description: str):
    """
    Generate MCP server from description
    NO LLM - Pure template system!
    """
    
    task_id = str(uuid.uuid4())
    
    # Track task
    generation_tasks[task_id] = {
        "status": "generating",
        "progress": 0,
        "description": description
    }
    
    async def progress_callback(message):
        generation_tasks[task_id]["message"] = message
        await broadcaster.manager.broadcast({
            "type": "generation_progress",
            "task_id": task_id,
            "message": message
        })
    
    try:
        progress_callback("🔍 Parsing requirements...")
        
        # Step 1: Parse intent
        parsed = intent_parser.parse(description)
        
        progress_callback(f"✅ Detected: {parsed['mcp_type'].value}")
        
        # Step 2: Generate code
        progress_callback("📝 Generating code...")
        
        generation_result = await code_generator.generate_mcp_server(
            mcp_name=parsed["mcp_name"],
            template_name=parsed["template"],
            mcp_type=parsed["mcp_type"].value,
            requirements=parsed["requirements"],
            customizations=parsed["customizations"],
            technologies=parsed["technologies"],
            on_progress=progress_callback
        )
        
        if not generation_result["success"]:
            return {
                "status": "failed",
                "task_id": task_id,
                "error": generation_result.get("error")
            }
        
        progress_callback("🐳 Deploying to Docker...")
        
        # Step 3: Deploy
        mcp_id = f"mcp-{task_id[:8]}"
        
        deployment_result = await auto_deployer.deploy_mcp_server(
            generation_result["project_dir"],
            parsed["mcp_name"],
            mcp_id
        )
        
        if not deployment_result["success"]:
            return {
                "status": "failed",
                "task_id": task_id,
                "error": deployment_result.get("error")
            }
        
        progress_callback("📊 Registering with Archestra...")
        
        # Step 4: Register with Archestra
        archestra_result = await archestra.register_mcp_server(
            mcp_id=mcp_id,
            mcp_name=parsed["mcp_name"],
            mcp_endpoint=deployment_result["endpoint"],
            description=description
        )
        
        progress_callback("✅ Generation complete!")
        
        # Step 5: Save to database
        await mcp_manager.create_mcp_record(
            mcp_name=parsed["mcp_name"],
            mcp_type=parsed["mcp_type"].value,
            mcp_id=mcp_id,
            endpoint=deployment_result["endpoint"],
            port=deployment_result["port"],
            project_dir=generation_result["project_dir"],
            generated_code={},
            customizations=parsed["customizations"]
        )
        
        generation_tasks[task_id]["status"] = "completed"
        
        # Broadcast completion
        await broadcaster.manager.broadcast({
            "type": "mcp_generated",
            "task_id": task_id,
            "mcp_id": mcp_id,
            "mcp_name": parsed["mcp_name"],
            "endpoint": deployment_result["endpoint"]
        })
        
        return {
            "status": "success",
            "task_id": task_id,
            "mcp_id": mcp_id,
            "mcp_name": parsed["mcp_name"],
            "endpoint": deployment_result["endpoint"],
            "port": deployment_result["port"],
            "description": description
        }
    
    except Exception as e:
        generation_tasks[task_id]["status"] = "failed"
        return {
            "status": "failed",
            "task_id": task_id,
            "error": str(e)
        }

@app.get("/api/generation/{task_id}")
async def get_generation_status(task_id: str):
    """Get generation task status"""
    
    task = generation_tasks.get(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task

# ==================== MCP MANAGEMENT ====================

@app.get("/api/mcps")
async def list_mcps():
    """List all generated MCPs"""
    
    mcps = await mcp_manager.list_mcps()
    
    return {
        "status": "success",
        "total": len(mcps),
        "mcps": [
            {
                "mcp_id": m.get("mcp_id"),
                "mcp_name": m.get("mcp_name"),
                "mcp_type": m.get("mcp_type"),
                "endpoint": m.get("endpoint"),
                "status": m.get("status"),
                "created_at": m.get("created_at").isoformat() if m.get("created_at") else None
            }
            for m in mcps
        ]
    }

@app.get("/api/mcps/{mcp_id}")
async def get_mcp(mcp_id: str):
    """Get specific MCP details"""
    
    mcp = await mcp_manager.get_mcp(mcp_id)
    
    if not mcp:
        raise HTTPException(status_code=404, detail="MCP not found")
    
    mcp["_id"] = str(mcp["_id"])
    return {"status": "success", "mcp": mcp}

@app.delete("/api/mcps/{mcp_id}")
async def delete_mcp(mcp_id: str):
    """Delete MCP"""
    
    # Stop container
    auto_deployer.stop_mcp_server(mcp_id)
    
    # Delete from database
    result = await mcp_manager.delete_mcp(mcp_id)
    
    return result

# ==================== TEMPLATES ====================

@app.get("/api/templates")
async def list_templates():
    """List available templates"""
    
    templates = template_selector.list_all_templates()
    
    return {
        "status": "success",
        "total": len(templates),
        "templates": templates
    }

# ==================== WEBSOCKET ====================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    
    await connection_manager.connect(websocket)
    
    async def message_handler(message, ws):
        msg_type = message.get("type")
        
        if msg_type == "ping":
            return {"type": "pong"}
        elif msg_type == "get_status":
            return {
                "type": "status",
                "connections": connection_manager.get_connection_count(),
                "mcps_generated": len(await mcp_manager.list_mcps())
            }
    
    try:
        await connection_manager.receive_and_handle(websocket, message_handler)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        connection_manager.disconnect(websocket)

# ==================== STATS ====================

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    
    mcps = await mcp_manager.list_mcps()
    
    return {
        "status": "success",
        "stats": {
            "generated_mcps": len(mcps),
            "active_mcps": sum(1 for m in mcps if m.get("status") == "active"),
            "total_connections": connection_manager.get_connection_count(),
            "generation_tasks": len(generation_tasks),
            "timestamp": datetime.utcnow().isoformat()
        }
    }

# Run: uvicorn backend.main:app --reload --port 8000