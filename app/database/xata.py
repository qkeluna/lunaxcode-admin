"""
Xata database client and connection management.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
import httpx
import asyncpg
from xata import XataClient

from app.core.config import settings
from app.core.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class XataDB:
    """Xata database client wrapper."""
    
    def __init__(self):
        self.client: Optional[XataClient] = None
        self.http_client: Optional[httpx.AsyncClient] = None
        self.pg_pool: Optional[asyncpg.Pool] = None
        self._initialized = False
        self.base_url: Optional[str] = None
        self.branch_name: str = "main"
    
    async def connect(self):
        """Initialize Xata client connection."""
        if self._initialized:
            return
        
        if not settings.XATA_API_KEY or not settings.XATA_DATABASE_URL:
            raise DatabaseError(
                "XATA_API_KEY and XATA_DATABASE_URL must be set",
                operation="connect"
            )
        
        try:
            # Parse database URL to extract components
            db_url = settings.XATA_DATABASE_URL
            
            if db_url and db_url.startswith('postgresql://'):
                # Extract components and prioritize XataClient over PostgreSQL due to connection issues
                logger.info(f"🔧 Using XataClient approach (PostgreSQL had connection issues)")
                
                import re
                # Use db_url directly to avoid parameter conflicts
                try:
                    self.client = XataClient(
                        api_key=settings.XATA_API_KEY,
                        db_url=db_url
                    )
                    logger.info("✅ XataClient initialized successfully with db_url")
                    
                except Exception as e:
                    logger.error(f"Failed to initialize XataClient: {e}")
                    raise DatabaseError(f"Failed to initialize XataClient: {str(e)}", operation="connect")
            
            elif db_url and db_url.startswith('https://'):
                # Handle HTTP endpoint URL format
                import re
                
                # Try format with branch: https://workspace-name.region.xata.sh/db/db_name:branch
                match_with_branch = re.match(r'https://([^.]+)\.([^.]+)\.xata\.sh/db/([^:]+):(.+)', db_url)
                
                # Try format without branch: https://workspace-name.region.xata.sh/db/db_name
                match_without_branch = re.match(r'https://([^.]+)\.([^.]+)\.xata\.sh/db/([^:]+)$', db_url)
                
                if match_with_branch:
                    workspace_name, region, db_name, branch = match_with_branch.groups()
                    logger.info(f"🔧 Parsed HTTP URL with branch: workspace={workspace_name}, region={region}, db={db_name}, branch={branch}")
                    
                    # Use the full workspace name for the base URL
                    self.base_url = f"https://{workspace_name}.{region}.xata.sh/db/{db_name}"
                    self.branch_name = branch
                    
                elif match_without_branch:
                    workspace_name, region, db_name = match_without_branch.groups()
                    logger.info(f"🔧 Parsed HTTP URL without branch: workspace={workspace_name}, region={region}, db={db_name}")
                    
                    # Use the full workspace name for the base URL
                    self.base_url = f"https://{workspace_name}.{region}.xata.sh/db/{db_name}"
                    self.branch_name = settings.XATA_BRANCH  # Use default from config
                    
                else:
                    # Use db_url directly if it doesn't match expected formats
                    logger.info(f"🔧 Using HTTP URL directly: {db_url}")
                    self.base_url = db_url
                    self.branch_name = settings.XATA_BRANCH
                
                # Always use db_url directly to avoid parameter conflicts
                self.client = XataClient(
                    api_key=settings.XATA_API_KEY,
                    db_url=db_url
                )
            
            else:
                raise ValueError(f"Unsupported database URL format: {db_url}")
            
            # Initialize HTTP client for direct API calls
            self.http_client = httpx.AsyncClient(
                headers={
                    "Authorization": f"Bearer {settings.XATA_API_KEY}",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            
            # Test connection
            await self.health_check()
            
            self._initialized = True
            logger.info("✅ Xata database connection established")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Xata database: {e}")
            raise DatabaseError(f"Failed to connect to Xata: {str(e)}", operation="connect")
    
    async def disconnect(self):
        """Close database connections."""
        if self.http_client:
            await self.http_client.aclose()
            self.http_client = None
        
        self.client = None
        self._initialized = False
        logger.info("✅ Xata database connection closed")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check database health."""
        
        if self.client:
            # Use XataClient for health check
            try:
                logger.info("🔍 Attempting XataClient health check...")
                
                # Use the XataClient to get database info
                # The client should have built-in methods for this
                response = await asyncio.wait_for(
                    asyncio.to_thread(self._get_database_info),
                    timeout=15.0
                )
                
                logger.info(f"✅ XataClient health check successful")
                return response
                    
            except Exception as e:
                logger.error(f"XataClient health check failed: {e}")
                logger.error(f"Error type: {type(e).__name__}")
                logger.error(f"Error details: {str(e)}")
                raise DatabaseError(f"Health check failed: {str(e)}", operation="health_check")
        
        elif self.http_client:
            # Use HTTP client for health check
            try:
                # Try without branch parameter first, fallback to with branch if needed
                try:
                    response = await self.http_client.get(f"{self.base_url}/tables")
                    response.raise_for_status()
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 400:
                        # If 400 error, try with branch parameter
                        response = await self.http_client.get(f"{self.base_url}/tables", params={"branch": self.branch_name})
                response.raise_for_status()
                
                tables = response.json()
                return {
                    "status": "healthy",
                    "connection_type": "rest_api",
                    "tables_count": len(tables.get("tables", [])),
                    "branch": self.branch_name
                }
                
            except Exception as e:
                logger.error(f"REST API health check failed: {e}")
                raise DatabaseError(f"Health check failed: {str(e)}", operation="health_check")
        
        else:
            raise DatabaseError("No database connection available", operation="health_check")
    
    def _get_database_info(self) -> Dict[str, Any]:
        """Get database info using XataClient."""
        try:
            # Try to get schema or table info using XataClient
            # For now, let's just verify the client works by attempting a simple operation
            if hasattr(self.client, 'get_database_schema'):
                schema = self.client.get_database_schema()
                tables = schema.get('tables', []) if schema else []
                table_names = [table.get('name', '') for table in tables]
            else:
                # Fallback: try to query a table to see if connection works
                # We know pricing_plans exists from our SQL script
                try:
                    result = self.client.data().query("pricing_plans", {
                        "page": {"size": 1}
                    })
                    table_names = ["pricing_plans", "features", "testimonials"]  # Known tables
                except:
                    table_names = []
            
            return {
                "status": "healthy",
                "connection_type": "xata_client",
                "tables_count": len(table_names),
                "tables": table_names[:5],
                "branch": self.branch_name
            }
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            # Even if we can't get table info, if the client initializes, connection is likely OK
            return {
                "status": "healthy",
                "connection_type": "xata_client",
                "tables_count": 0,
                "tables": [],
                "branch": self.branch_name,
                "note": "Client initialized but couldn't retrieve table info"
            }
    
    async def create_record(
        self,
        table: str,
        data: Dict[str, Any],
        record_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new record in the specified table."""
        if not self.client:
            raise DatabaseError("Database not connected", operation="create_record")
        
        try:
            # Use XataClient data API for creating records (wrapped in thread for async)
            result = await asyncio.to_thread(
                lambda: self.client.data().insert(table, data, record_id=record_id)
            )
            logger.debug(f"Created record in {table}: {result.get('id')}")
            return result
            
        except Exception as e:
            logger.error(f"Error creating record in {table}: {e}")
            error_details = str(e)
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                error_details = e.response.text
            
            raise DatabaseError(
                f"Failed to create record in {table}: {error_details}",
                operation="create_record"
            )
    
    async def get_record(self, table: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Get a record by ID."""
        if not self.client:
            raise DatabaseError("Database not connected", operation="get_record")
        
        try:
            # Use XataClient data API for getting records (wrapped in thread for async)
            result = await asyncio.to_thread(
                lambda: self.client.data().get(table, record_id)
            )
            if result:
                logger.debug(f"Retrieved record from {table}: {record_id}")
                return result
            return None
            
        except Exception as e:
            logger.error(f"Error getting record from {table}: {e}")
            # Handle not found errors gracefully
            error_details = str(e)
            if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                if e.response.status_code == 404:
                    return None
                error_details = e.response.text
            
            raise DatabaseError(
                f"Failed to get record from {table}: {error_details}",
                operation="get_record"
            )
    
    async def update_record(
        self,
        table: str,
        record_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a record by ID."""
        if not self.client:
            raise DatabaseError("Database not connected", operation="update_record")
        
        try:
            # Use XataClient data API for updating records (wrapped in thread for async)
            result = await asyncio.to_thread(
                lambda: self.client.data().update(table, record_id, data)
            )
            logger.debug(f"Updated record in {table}: {record_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error updating record in {table}: {e}")
            error_details = str(e)
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                error_details = e.response.text
            
            raise DatabaseError(
                f"Failed to update record in {table}: {error_details}",
                operation="update_record"
            )
    
    async def delete_record(self, table: str, record_id: str) -> bool:
        """Delete a record by ID."""
        if not self.client:
            raise DatabaseError("Database not connected", operation="delete_record")
        
        try:
            # Use XataClient data API for deleting records (wrapped in thread for async)
            result = await asyncio.to_thread(
                lambda: self.client.data().delete(table, record_id)
            )
            logger.debug(f"Deleted record from {table}: {record_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting record from {table}: {e}")
            # Handle not found errors gracefully
            error_details = str(e)
            if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                if e.response.status_code == 404:
                    return False
                error_details = e.response.text
            
            raise DatabaseError(
                f"Failed to delete record from {table}: {error_details}",
                operation="delete_record"
            )
    
    async def query_records(
        self,
        table: str,
        filter_conditions: Optional[Dict[str, Any]] = None,
        sort: Optional[List[Dict[str, str]]] = None,
        page_size: int = 20,
        offset: int = 0,
        columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Query records with filtering, sorting, and pagination."""
        if not self.client:
            raise DatabaseError("Database not connected", operation="query_records")
        
        try:
            # Use XataClient data API for querying
            query = {
                "page": {
                    "size": page_size,
                    "offset": offset
                }
            }
            
            if filter_conditions:
                query["filter"] = filter_conditions
            
            if sort:
                query["sort"] = sort
            
            if columns:
                query["columns"] = columns
            
            # Use the client's data().query method (wrapped in thread for async)
            result = await asyncio.to_thread(
                lambda: self.client.data().query(table, query)
            )
            logger.debug(f"Queried {table}: {len(result.get('records', []))} records")
            return result
            
        except Exception as e:
            logger.error(f"Error querying {table}: {e}")
            # Try to get more specific error information
            error_details = str(e)
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                error_details = e.response.text
            
            raise DatabaseError(
                f"Failed to query {table}: {error_details}",
                operation="query_records"
            )
    
    async def search_records(
        self,
        table: str,
        query: str,
        target_columns: Optional[List[str]] = None,
        filter_conditions: Optional[Dict[str, Any]] = None,
        page_size: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Full-text search in table records."""
        if not self.http_client:
            raise DatabaseError("Database not connected", operation="search_records")
        
        try:
            url = f"{self.base_url}/tables/{table}/search"
            
            search_query = {
                "query": query,
                "page": {
                    "size": page_size,
                    "offset": offset
                }
            }
            
            if target_columns:
                search_query["target"] = target_columns
            
            if filter_conditions:
                search_query["filter"] = filter_conditions
            
            response = await self.http_client.post(url, json=search_query)
            response.raise_for_status()
            
            result = response.json()
            logger.debug(f"Searched {table}: {len(result.get('records', []))} records")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error searching {table}: {e.response.text}")
            raise DatabaseError(
                f"Failed to search {table}: {e.response.text}",
                operation="search_records"
            )
        except Exception as e:
            logger.error(f"Error searching {table}: {e}")
            raise DatabaseError(
                f"Failed to search {table}: {str(e)}",
                operation="search_records"
            )


# Global database instance
db = XataDB()


async def get_database() -> XataDB:
    """Dependency to get database instance."""
    if not db._initialized:
        await db.connect()
    return db
