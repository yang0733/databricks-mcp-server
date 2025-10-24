"""Git repository management tools for Databricks."""

from typing import Optional


def register_tools(mcp, get_wrapper):
    """Register repository management tools with the MCP server."""
    
    @mcp.tool()
    def create_repo(
        url: str,
        provider: str,
        path: Optional[str] = None,
        context=None
    ) -> dict:
        """Link a Git repository to Databricks workspace.
        
        Args:
            url: Git repository URL (e.g., https://github.com/user/repo)
            provider: Git provider (gitHub, gitHubEnterprise, bitbucketCloud, bitbucketServer, azureDevOpsServices, gitLab, gitLabEnterpriseEdition)
            path: Optional workspace path for the repo (auto-generated if not provided)
            
        Returns:
            Dictionary with repo ID and details
        """
        wrapper = get_wrapper(context)
        
        repo_config = {
            "url": url,
            "provider": provider,
        }
        
        if path:
            repo_config["path"] = path
        
        response = wrapper.client.repos.create(**repo_config)
        
        return {
            "id": response.id,
            "path": response.path,
            "url": url,
            "provider": provider,
            "branch": response.branch,
            "head_commit_id": response.head_commit_id,
            "status": "created",
            "message": f"Repository linked at {response.path}"
        }
    
    @mcp.tool()
    def update_repo(
        repo_id: int,
        branch: Optional[str] = None,
        tag: Optional[str] = None,
        context=None
    ) -> dict:
        """Update a repository to a specific branch or tag.
        
        Args:
            repo_id: Repository ID
            branch: Branch name to checkout
            tag: Tag name to checkout (mutually exclusive with branch)
            
        Returns:
            Dictionary with update status
        """
        wrapper = get_wrapper(context)
        
        update_config = {"repo_id": repo_id}
        
        if branch:
            update_config["branch"] = branch
        elif tag:
            update_config["tag"] = tag
        else:
            return {"error": "Either branch or tag must be specified"}
        
        response = wrapper.client.repos.update(**update_config)
        
        return {
            "id": response.id,
            "branch": response.branch,
            "tag": response.tag,
            "head_commit_id": response.head_commit_id,
            "status": "updated",
            "message": f"Repository updated to {branch or tag}"
        }
    
    @mcp.tool()
    def delete_repo(
        repo_id: int,
        context=None
    ) -> dict:
        """Delete a linked repository.
        
        Args:
            repo_id: Repository ID to delete
            
        Returns:
            Dictionary with deletion status
        """
        wrapper = get_wrapper(context)
        
        wrapper.client.repos.delete(repo_id)
        
        return {
            "id": repo_id,
            "status": "deleted",
            "message": f"Repository {repo_id} has been deleted"
        }
    
    @mcp.tool()
    def list_repos(
        path_prefix: Optional[str] = None,
        next_page_token: Optional[str] = None,
        context=None
    ) -> dict:
        """List all linked repositories.
        
        Args:
            path_prefix: Optional filter by path prefix
            next_page_token: Token for pagination
            
        Returns:
            Dictionary with list of repositories
        """
        wrapper = get_wrapper(context)
        
        list_config = {}
        if path_prefix:
            list_config["path_prefix"] = path_prefix
        if next_page_token:
            list_config["next_page_token"] = next_page_token
        
        repos = wrapper.client.repos.list(**list_config)
        
        repo_list = []
        for repo in repos:
            repo_list.append({
                "id": repo.id,
                "path": repo.path,
                "url": repo.url,
                "provider": repo.provider,
                "branch": repo.branch,
                "head_commit_id": repo.head_commit_id,
            })
        
        return {
            "repos": repo_list,
            "count": len(repo_list)
        }
    
    @mcp.tool()
    def get_repo(
        repo_id: int,
        context=None
    ) -> dict:
        """Get detailed information about a specific repository.
        
        Args:
            repo_id: Repository ID to query
            
        Returns:
            Dictionary with detailed repository information
        """
        wrapper = get_wrapper(context)
        
        repo = wrapper.client.repos.get(repo_id)
        
        return {
            "id": repo.id,
            "path": repo.path,
            "url": repo.url,
            "provider": repo.provider,
            "branch": repo.branch,
            "tag": repo.tag,
            "head_commit_id": repo.head_commit_id,
        }

