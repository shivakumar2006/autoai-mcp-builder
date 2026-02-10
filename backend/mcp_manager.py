# Copy-paste into: backend/mcp_manager.py

from typing import Dict, List, Optional
from datetime import datetime
import uuid
from database import MongoDB

class MCPManager:
    """
    Manage generated MCP servers
    Store in MongoDB
    Track deployments
    """
    
    def __init__(self):
        pass
    
    async def create_mcp_record(
        self,
        mcp_name: str,
        mcp_type: str,
        mcp_id: str,
        endpoint: str,
        port: int,
        project_dir: str,
        generated_code: Dict[str, str],
        customizations: Dict
    ) -> Dict:
        """Create MCP record in MongoDB"""
        
        record = {
            "mcp_id": mcp_id,
            "mcp_name": mcp_name,
            "mcp_type": mcp_type,
            "endpoint": endpoint,
            "port": port,
            "project_dir": project_dir,
            "generated_code": generated_code,
            "customizations": customizations,
            "status": "active",
            "created_at": datetime.utcnow(),
            "last_accessed": datetime.utcnow(),
            "analytics": {
                "calls": 0,
                "errors": 0,
                "avg_response_time": 0
            }
        }
        
        try:
            result = await MongoDB.mcp_servers.insert_one(record)
            return {
                "success": True,
                "mcp_id": mcp_id,
                "db_id": str(result.inserted_id)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_mcp(self, mcp_id: str) -> Optional[Dict]:
        """Get MCP details"""
        
        try:
            return await MongoDB.mcp_servers.find_one({"mcp_id": mcp_id})
        except:
            return None
    
    async def list_mcps(self) -> List[Dict]:
        """List all generated MCPs"""
        
        try:
            cursor = MongoDB.mcp_servers.find().sort("created_at", -1)
            return await cursor.to_list(length=None)
        except:
            return []
    
    async def update_mcp_status(self, mcp_id: str, status: str) -> Dict:
        """Update MCP status"""
        
        try:
            result = await MongoDB.mcp_servers.update_one(
                {"mcp_id": mcp_id},
                {"$set": {"status": status, "last_accessed": datetime.utcnow()}}
            )
            
            return {
                "success": True,
                "modified": result.modified_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_mcp(self, mcp_id: str) -> Dict:
        """Delete MCP record"""
        
        try:
            result = await MongoDB.mcp_servers.delete_one({"mcp_id": mcp_id})
            
            return {
                "success": True,
                "deleted": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def track_call(self, mcp_id: str, response_time: float, success: bool) -> None:
        """Track MCP API call"""
        
        try:
            if success:
                await MongoDB.mcp_servers.update_one(
                    {"mcp_id": mcp_id},
                    {
                        "$inc": {"analytics.calls": 1},
                        "$set": {"analytics.last_response_time": response_time}
                    }
                )
            else:
                await MongoDB.mcp_servers.update_one(
                    {"mcp_id": mcp_id},
                    {"$inc": {"analytics.errors": 1}}
                )
        except:
            pass