# Databricks CLI MCP Server - Deployment Guide

This guide covers deploying the Databricks CLI MCP Server as a Databricks App for production use.

## Prerequisites

### 1. Databricks CLI Installation

```bash
# Install Databricks CLI
brew install databricks

# Verify installation
databricks --version
```

### 2. Workspace Access

You need access to a Databricks workspace where you can:
- Create and deploy Apps
- Have appropriate permissions for your use case

### 3. Authentication Setup

```bash
# Configure Databricks CLI
databricks configure --token

# You'll be prompted for:
# - Databricks Host: https://your-workspace.cloud.databricks.com
# - Token: Your personal access token

# Test connection
databricks workspace ls /
```

## Deployment Methods

### Method 1: Quick Deploy (Recommended)

```bash
# Make deployment script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

The script will:
1. Check prerequisites
2. Verify authentication
3. Deploy the app to Databricks
4. Show you the app URL

### Method 2: Manual Deployment

```bash
# Deploy the app
databricks apps deploy databricks-cli-mcp-server --source-path .

# Monitor deployment
databricks apps logs databricks-cli-mcp-server --follow

# Check status
databricks apps get databricks-cli-mcp-server
```

## Post-Deployment

### Accessing the App

Once deployed, get the app URL:

```bash
databricks apps get databricks-cli-mcp-server
```

The MCP endpoint will be at:
```
https://your-workspace.cloud.databricks.com/apps/databricks-cli-mcp-server/mcp/
```

### Monitoring

```bash
# View real-time logs
databricks apps logs databricks-cli-mcp-server --follow

# View last 100 lines
databricks apps logs databricks-cli-mcp-server --tail 100

# Save logs to file
databricks apps logs databricks-cli-mcp-server > logs.txt
```

### Checking Status

```bash
# Get app status
databricks apps get databricks-cli-mcp-server

# Expected output includes:
# - State: RUNNING
# - URL: https://...
# - Compute size: MEDIUM
```

## Configuration

### Compute Sizing

Edit `databricks.yml` to adjust resources:

```yaml
compute:
  size: SMALL   # 1 CPU, 4GB RAM - Light usage (1-10 users)
  size: MEDIUM  # 2 CPU, 8GB RAM - Default (10-50 users)
  size: LARGE   # 4 CPU, 16GB RAM - Heavy usage (50+ users)
```

After changing, redeploy:
```bash
./deploy.sh
```

### Auto-Shutdown

Configure idle timeout in `databricks.yml`:

```yaml
compute:
  auto_shutdown_minutes: 30  # Default
  auto_shutdown_minutes: 60  # Production
  auto_shutdown_minutes: 15  # Development
```

## Updating the App

When you make code changes:

```bash
# 1. Test locally first
python server.py
python test_local.py

# 2. Commit changes
git add .
git commit -m "Description of changes"

# 3. Deploy update
./deploy.sh

# 4. Monitor logs for errors
databricks apps logs databricks-cli-mcp-server --follow
```

## Managing the App

### Restart

```bash
databricks apps restart databricks-cli-mcp-server
```

### Stop

```bash
databricks apps stop databricks-cli-mcp-server
```

### Delete

```bash
databricks apps delete databricks-cli-mcp-server
```

### Permissions

Grant access to team members:

```bash
# Via web UI:
# 1. Navigate to Apps in workspace
# 2. Click on databricks-cli-mcp-server
# 3. Click Permissions
# 4. Add users/groups with CAN_VIEW or CAN_MANAGE

# Via CLI:
databricks permissions set app/databricks-cli-mcp-server \
  --user user@company.com \
  --permission-level CAN_VIEW
```

## Production Checklist

Before deploying to production:

- [ ] Tested locally with `test_local.py`
- [ ] All linter errors resolved
- [ ] README.md is up to date
- [ ] Compute size is appropriate for expected load
- [ ] Auto-shutdown timeout is configured
- [ ] Authentication tested with real credentials
- [ ] Team members have appropriate permissions
- [ ] Monitoring/logging strategy in place

## Troubleshooting

### Issue: "App not found"

```bash
# Verify app exists
databricks apps list | grep databricks-cli-mcp-server

# If not found, create it
./deploy.sh
```

### Issue: Deployment fails

```bash
# Check authentication
databricks workspace ls /

# Check permissions
databricks apps list

# Review error logs
databricks apps logs databricks-cli-mcp-server --tail 50
```

### Issue: App shows error page

```bash
# Check logs for errors
databricks apps logs databricks-cli-mcp-server --tail 200

# Common issues:
# - Missing dependencies (check requirements.txt)
# - Import errors (check PYTHONPATH in databricks.yml)
# - Port conflicts (default is 8080)
```

### Issue: Slow performance

```bash
# Increase compute size in databricks.yml
compute:
  size: LARGE

# Redeploy
./deploy.sh
```

## Cost Optimization

### Estimate Costs

- **SMALL**: ~$0.20/hour
- **MEDIUM**: ~$0.40/hour
- **LARGE**: ~$0.80/hour

Auto-shutdown reduces costs during idle periods.

### Monitoring Usage

1. Go to Databricks workspace
2. Navigate to **Admin Console** → **Usage**
3. Filter by **Apps**
4. View `databricks-cli-mcp-server` usage

## Security Recommendations

1. **Regular Updates**: Keep dependencies updated
2. **Access Control**: Limit app permissions to required users
3. **Audit Logs**: Enable and review Databricks audit logs
4. **Token Rotation**: Users should rotate PATs every 90 days
5. **Network Security**: Use workspace network policies if available

## Support

For deployment issues:

1. Check this guide
2. Review app logs
3. Test locally to isolate issues
4. Contact Databricks support if workspace issues
5. Contact development team for code issues

## Additional Resources

- [Databricks Apps Documentation](https://docs.databricks.com/en/dev-tools/databricks-apps/index.html)
- [Databricks CLI Reference](https://docs.databricks.com/en/dev-tools/cli/index.html)
- [Main README](README.md)

---

Last updated: October 2025

