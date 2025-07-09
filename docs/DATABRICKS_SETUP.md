# Databricks Setup Guide for Customer.IO Notebooks

This guide explains how to deploy and run the Customer.IO API client library and notebooks on Databricks clusters.

## Overview

The Customer.IO notebooks have been updated to work seamlessly on Databricks clusters. The notebooks now support:
- Automatic library installation
- Databricks secrets for credential management
- Compatible import paths for both local and cluster environments
- DBFS path support

## Prerequisites

1. **Databricks Workspace** with appropriate permissions
2. **Customer.IO API Credentials**:
   - Data Pipelines API Key (for pipelines_api notebooks)
   - App API Token (for app_api notebooks)
   - Region setting (us or eu)
3. **Cluster Access** with ability to install libraries

## Setup Options

### Option 1: Using the Packaged Library (Recommended)

This approach packages all the Customer.IO modules into a wheel file for easy installation.

#### Step 1: Build the Wheel File

On your local machine:

```bash
# Clone the repository
git clone https://github.com/your-org/customer_io_notebooks.git
cd customer_io_notebooks

# Build the wheel file
pip install build
python -m build

# This creates a wheel file in the dist/ directory
# Example: dist/customerio_api_client-1.0.0-py3-none-any.whl
```

#### Step 2: Upload to DBFS

Upload the wheel file to DBFS using the Databricks UI or CLI:

```bash
# Using Databricks CLI
databricks fs cp dist/customerio_api_client-1.0.0-py3-none-any.whl dbfs:/libraries/customerio_api_client-1.0.0-py3-none-any.whl
```

#### Step 3: Install on Cluster

In your notebooks, the library installation cell will handle this:

```python
%pip install /dbfs/libraries/customerio_api_client-1.0.0-py3-none-any.whl
```

### Option 2: Direct Installation from Requirements

For development or if you prefer not to package:

```python
# In the notebook setup cell
%pip install httpx>=0.25.0 pydantic>=2.0.0 pandas>=2.0.0 python-dotenv>=1.0.0 structlog>=24.0.0
```

Then upload the `src/` directory to your workspace and adjust imports accordingly.

### Option 3: Git-based Installation

If your repository is accessible:

```python
%pip install git+https://github.com/your-org/customer_io_notebooks.git
```

## Credential Management

### Setting up Databricks Secrets

1. **Create a Secret Scope**:
   ```bash
   databricks secrets create-scope --scope customer-io
   ```

2. **Add Your Credentials**:
   ```bash
   # For Data Pipelines API
   databricks secrets put --scope customer-io --key api_key
   # Enter your API key when prompted

   # For region setting
   databricks secrets put --scope customer-io --key region
   # Enter 'us' or 'eu'

   # For App API (if using)
   databricks secrets put --scope customer-io --key app_token
   # Enter your App API token
   ```

3. **Verify Setup**:
   ```bash
   databricks secrets list --scope customer-io
   ```

### Using Secrets in Notebooks

The notebooks automatically detect and use Databricks secrets:

```python
try:
    # Automatically uses Databricks secrets if available
    API_KEY = dbutils.secrets.get(scope="customer-io", key="api_key")
    REGION = dbutils.secrets.get(scope="customer-io", key="region")
except:
    # Falls back to environment variables
    API_KEY = os.getenv('CUSTOMERIO_API_KEY')
```

## Running the Notebooks

### Step 1: Upload Notebooks to Workspace

1. In Databricks workspace, create a folder for the notebooks
2. Upload all notebooks from the `notebooks/` directory
3. Maintain the directory structure:
   ```
   /customer-io-notebooks/
   ├── 00_multi_api_overview.ipynb
   ├── pipelines_api/
   │   ├── 00_setup_and_configuration.ipynb
   │   ├── 01_people_management.ipynb
   │   └── ...
   ├── app_api/
   │   └── 01_communications.ipynb
   └── webhooks/
       └── 01_webhook_processing.ipynb
   ```

### Step 2: Start with Setup Notebook

1. Open `pipelines_api/00_setup_and_configuration.ipynb`
2. Run the Databricks setup cells (they're clearly marked)
3. Verify the library installation and credential access
4. Test basic connectivity

### Step 3: Run Other Notebooks

Each notebook includes:
- Databricks setup section at the beginning
- Automatic import path resolution
- Credential management using secrets

## Cluster Configuration

### Recommended Cluster Settings

- **Databricks Runtime**: 12.2 LTS or later
- **Python Version**: 3.9 or later
- **Node Type**: Standard_DS3_v2 or larger
- **Workers**: 1-2 for development, scale as needed

### Library Installation Methods

1. **Cluster Libraries** (Persistent):
   - Go to Cluster > Libraries
   - Install the wheel file or PyPI packages
   - Libraries persist across cluster restarts

2. **Notebook-scoped** (Temporary):
   - Use `%pip install` in notebooks
   - Installations are session-specific
   - Good for development and testing

## Troubleshooting

### Import Errors

If you see import errors:

1. **Check library installation**:
   ```python
   %pip show customerio-api-client
   ```

2. **Verify the src path** (if using direct files):
   ```python
   import sys
   print(sys.path)
   ```

3. **Restart Python kernel** after installation:
   ```python
   dbutils.library.restartPython()
   ```

### Credential Issues

1. **Verify secret scope exists**:
   ```python
   dbutils.secrets.listScopes()
   ```

2. **Check secret keys**:
   ```python
   dbutils.secrets.list("customer-io")
   ```

3. **Test credential access**:
   ```python
   try:
       api_key = dbutils.secrets.get(scope="customer-io", key="api_key")
       print("Successfully retrieved API key")
   except Exception as e:
       print(f"Error: {e}")
   ```

### Path Issues

For DBFS paths:
- Use `/dbfs/` prefix when accessing from Python
- Use `dbfs:/` prefix for Databricks utilities

Example:
```python
# Python file access
with open('/dbfs/path/to/file.txt', 'r') as f:
    content = f.read()

# Databricks utilities
dbutils.fs.ls('dbfs:/path/to/directory')
```

## Best Practices

1. **Use Databricks Secrets** for all credentials
2. **Install libraries at cluster level** for production
3. **Test in development cluster** before production deployment
4. **Use version-pinned dependencies** for reproducibility
5. **Monitor API rate limits** when running parallel notebooks

## Production Deployment

### Step 1: Create Production Cluster

1. Create a dedicated cluster for Customer.IO workloads
2. Install the library at cluster level
3. Configure autoscaling based on workload

### Step 2: Schedule Notebooks

Use Databricks Jobs to schedule regular runs:

```python
# Example job configuration
{
  "name": "Customer.IO Daily Sync",
  "tasks": [{
    "task_key": "sync_customers",
    "notebook_task": {
      "notebook_path": "/customer-io-notebooks/pipelines_api/01_people_management",
      "base_parameters": {
        "mode": "production"
      }
    }
  }]
}
```

### Step 3: Monitor and Alert

1. Set up email notifications for job failures
2. Monitor API usage and rate limits
3. Track data quality metrics

## Advanced Topics

### Using with Delta Tables

Store Customer.IO data in Delta tables:

```python
# After fetching data from Customer.IO
df = spark.createDataFrame(customer_data)
df.write.mode("overwrite").saveAsTable("customer_io.customers")
```

### Parallel Processing

For large-scale operations:

```python
# Use Spark for parallel processing
from pyspark.sql.functions import col

# Process customer batches in parallel
customer_df = spark.table("customers")
customer_df.foreachPartition(process_customer_batch)
```

### Integration with Other Systems

Connect Customer.IO data with other data sources:

```python
# Join with internal data
customer_io_df = spark.table("customer_io.customers")
internal_df = spark.table("internal.users")

enriched_df = customer_io_df.join(
    internal_df,
    customer_io_df.email == internal_df.email,
    "left"
)
```

## Support and Resources

- **Documentation**: See other docs in the `docs/` directory
- **API Specifications**: Review `specs/` directory for API details
- **Issues**: Report issues in the project repository
- **Customer.IO Support**: Contact Customer.IO for API-specific questions

## Migration Checklist

When migrating existing notebooks:

- [ ] Update import statements to support both environments
- [ ] Add Databricks setup cells
- [ ] Convert credentials to use secrets
- [ ] Test in development cluster
- [ ] Update any file paths to use DBFS
- [ ] Verify all dependencies are available
- [ ] Test error handling and retries
- [ ] Document any cluster-specific configurations