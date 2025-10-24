"""Unity Catalog management tools for Databricks."""

from typing import Optional


def register_tools(mcp, get_wrapper):
    """Register Unity Catalog tools with the MCP server."""
    
    @mcp.tool()
    def list_catalogs(context=None) -> dict:
        """List all Unity Catalog catalogs.
        
        Returns:
            Dictionary with list of catalogs
        """
        wrapper = get_wrapper(context)
        
        catalogs = wrapper.client.catalogs.list()
        
        catalog_list = []
        for catalog in catalogs:
            catalog_list.append({
                "name": catalog.name,
                "comment": catalog.comment,
                "owner": catalog.owner,
                "created_at": catalog.created_at,
                "updated_at": catalog.updated_at,
            })
        
        return {
            "catalogs": catalog_list,
            "count": len(catalog_list)
        }
    
    @mcp.tool()
    def list_schemas(
        catalog_name: str,
        context=None
    ) -> dict:
        """List all schemas in a catalog.
        
        Args:
            catalog_name: Name of the catalog
            
        Returns:
            Dictionary with list of schemas
        """
        wrapper = get_wrapper(context)
        
        schemas = wrapper.client.schemas.list(catalog_name)
        
        schema_list = []
        for schema in schemas:
            schema_list.append({
                "name": schema.name,
                "catalog_name": schema.catalog_name,
                "comment": schema.comment,
                "owner": schema.owner,
                "full_name": schema.full_name,
                "created_at": schema.created_at,
                "updated_at": schema.updated_at,
            })
        
        return {
            "catalog": catalog_name,
            "schemas": schema_list,
            "count": len(schema_list)
        }
    
    @mcp.tool()
    def list_tables(
        catalog_name: str,
        schema_name: str,
        context=None
    ) -> dict:
        """List all tables in a schema.
        
        Args:
            catalog_name: Name of the catalog
            schema_name: Name of the schema
            
        Returns:
            Dictionary with list of tables
        """
        wrapper = get_wrapper(context)
        
        tables = wrapper.client.tables.list(
            catalog_name=catalog_name,
            schema_name=schema_name
        )
        
        table_list = []
        for table in tables:
            table_list.append({
                "name": table.name,
                "catalog_name": table.catalog_name,
                "schema_name": table.schema_name,
                "table_type": table.table_type.value if table.table_type else None,
                "data_source_format": table.data_source_format.value if table.data_source_format else None,
                "comment": table.comment,
                "owner": table.owner,
                "full_name": table.full_name,
                "created_at": table.created_at,
                "updated_at": table.updated_at,
            })
        
        return {
            "catalog": catalog_name,
            "schema": schema_name,
            "tables": table_list,
            "count": len(table_list)
        }
    
    @mcp.tool()
    def get_table(
        full_name: str,
        context=None
    ) -> dict:
        """Get detailed metadata for a table.
        
        Args:
            full_name: Full table name in format catalog.schema.table
            
        Returns:
            Dictionary with detailed table information including columns
        """
        wrapper = get_wrapper(context)
        
        table = wrapper.client.tables.get(full_name)
        
        result = {
            "name": table.name,
            "catalog_name": table.catalog_name,
            "schema_name": table.schema_name,
            "table_type": table.table_type.value if table.table_type else None,
            "data_source_format": table.data_source_format.value if table.data_source_format else None,
            "storage_location": table.storage_location,
            "comment": table.comment,
            "owner": table.owner,
            "full_name": table.full_name,
            "created_at": table.created_at,
            "updated_at": table.updated_at,
        }
        
        # Include column information
        if table.columns:
            result["columns"] = [
                {
                    "name": col.name,
                    "type_text": col.type_text,
                    "type_name": col.type_name.value if col.type_name else None,
                    "position": col.position,
                    "comment": col.comment,
                    "nullable": col.nullable,
                }
                for col in table.columns
            ]
        
        return result
    
    @mcp.tool()
    def list_volumes(
        catalog_name: str,
        schema_name: str,
        context=None
    ) -> dict:
        """List all volumes in a schema.
        
        Args:
            catalog_name: Name of the catalog
            schema_name: Name of the schema
            
        Returns:
            Dictionary with list of volumes
        """
        wrapper = get_wrapper(context)
        
        volumes = wrapper.client.volumes.list(
            catalog_name=catalog_name,
            schema_name=schema_name
        )
        
        volume_list = []
        for volume in volumes:
            volume_list.append({
                "name": volume.name,
                "catalog_name": volume.catalog_name,
                "schema_name": volume.schema_name,
                "volume_type": volume.volume_type.value if volume.volume_type else None,
                "storage_location": volume.storage_location,
                "comment": volume.comment,
                "owner": volume.owner,
                "full_name": volume.full_name,
                "created_at": volume.created_at,
                "updated_at": volume.updated_at,
            })
        
        return {
            "catalog": catalog_name,
            "schema": schema_name,
            "volumes": volume_list,
            "count": len(volume_list)
        }
    
    @mcp.tool()
    def create_volume(
        catalog_name: str,
        schema_name: str,
        name: str,
        volume_type: str = "MANAGED",
        storage_location: Optional[str] = None,
        comment: Optional[str] = None,
        context=None
    ) -> dict:
        """Create a new volume in Unity Catalog.
        
        Args:
            catalog_name: Name of the catalog
            schema_name: Name of the schema
            name: Name for the volume
            volume_type: Type of volume (MANAGED or EXTERNAL)
            storage_location: Storage location (required for EXTERNAL volumes)
            comment: Optional comment
            
        Returns:
            Dictionary with created volume details
        """
        wrapper = get_wrapper(context)
        
        volume_config = {
            "catalog_name": catalog_name,
            "schema_name": schema_name,
            "name": name,
            "volume_type": volume_type,
        }
        
        if storage_location:
            volume_config["storage_location"] = storage_location
        if comment:
            volume_config["comment"] = comment
        
        response = wrapper.client.volumes.create(**volume_config)
        
        return {
            "name": response.name,
            "catalog_name": response.catalog_name,
            "schema_name": response.schema_name,
            "volume_type": response.volume_type.value if response.volume_type else None,
            "storage_location": response.storage_location,
            "full_name": response.full_name,
            "status": "created",
            "message": f"Volume {response.full_name} has been created"
        }

