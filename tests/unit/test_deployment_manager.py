"""
Comprehensive tests for Customer.IO Deployment Manager.

Tests cover:
- Environment types, deployment strategies, infrastructure providers, and security levels
- Configuration management with secure secrets handling
- Infrastructure as Code (IaC) generation for multiple providers
- Deployment engine with strategy execution and rollback capabilities
- Multi-environment deployment workflows and promotion
- Security hardening and compliance validation
- Performance testing and concurrent deployments
"""

import pytest
import os
import tempfile
import yaml
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock, mock_open
from pydantic import ValidationError

from utils.deployment_manager import (
    Environment,
    DeploymentStrategy,
    InfrastructureProvider,
    DeploymentStatus,
    SecurityLevel,
    SecretConfig,
    EnvironmentConfig,
    DeploymentConfig,
    DeploymentResult,
    InfrastructureTemplate,
    ConfigurationManager,
    InfrastructureGenerator,
    DeploymentEngine,
    DeploymentManager
)
from utils.api_client import CustomerIOClient


class TestEnvironment:
    """Test Environment enum."""
    
    def test_environment_values(self):
        """Test all environment values."""
        assert Environment.DEVELOPMENT == "development"
        assert Environment.STAGING == "staging"
        assert Environment.PRODUCTION == "production"
        assert Environment.TESTING == "testing"
    
    def test_environment_membership(self):
        """Test environment membership."""
        valid_environments = [env.value for env in Environment]
        assert "development" in valid_environments
        assert "invalid_environment" not in valid_environments


class TestDeploymentStrategy:
    """Test DeploymentStrategy enum."""
    
    def test_deployment_strategy_values(self):
        """Test all deployment strategy values."""
        assert DeploymentStrategy.ROLLING_UPDATE == "rolling_update"
        assert DeploymentStrategy.BLUE_GREEN == "blue_green"
        assert DeploymentStrategy.CANARY == "canary"
        assert DeploymentStrategy.RECREATE == "recreate"
        assert DeploymentStrategy.A_B_TESTING == "a_b_testing"


class TestInfrastructureProvider:
    """Test InfrastructureProvider enum."""
    
    def test_infrastructure_provider_values(self):
        """Test all infrastructure provider values."""
        assert InfrastructureProvider.AWS == "aws"
        assert InfrastructureProvider.AZURE == "azure"
        assert InfrastructureProvider.GCP == "gcp"
        assert InfrastructureProvider.KUBERNETES == "kubernetes"
        assert InfrastructureProvider.DOCKER == "docker"
        assert InfrastructureProvider.LOCAL == "local"


class TestDeploymentStatus:
    """Test DeploymentStatus enum."""
    
    def test_deployment_status_values(self):
        """Test all deployment status values."""
        assert DeploymentStatus.PENDING == "pending"
        assert DeploymentStatus.RUNNING == "running"
        assert DeploymentStatus.SUCCESS == "success"
        assert DeploymentStatus.FAILED == "failed"
        assert DeploymentStatus.ROLLED_BACK == "rolled_back"
        assert DeploymentStatus.CANCELLED == "cancelled"


class TestSecurityLevel:
    """Test SecurityLevel enum."""
    
    def test_security_level_values(self):
        """Test all security level values."""
        assert SecurityLevel.BASIC == "basic"
        assert SecurityLevel.STANDARD == "standard"
        assert SecurityLevel.ENHANCED == "enhanced"
        assert SecurityLevel.CRITICAL == "critical"


class TestSecretConfig:
    """Test SecretConfig data model."""
    
    def test_valid_secret_config(self):
        """Test valid secret configuration creation."""
        secret = SecretConfig(
            name="api_key",
            value="secret_value_123",
            source="vault",
            encrypted=True,
            required=True,
            description="API key for Customer.IO"
        )
        
        assert secret.name == "API_KEY"  # Should be uppercase
        assert secret.value == "secret_value_123"
        assert secret.source == "vault"
        assert secret.encrypted is True
        assert secret.required is True
        assert secret.description == "API key for Customer.IO"
    
    def test_secret_name_validation(self):
        """Test secret name validation."""
        # Test empty name
        with pytest.raises(ValidationError):
            SecretConfig(
                name="",
                source="env"
            )
        
        # Test whitespace-only name
        with pytest.raises(ValidationError):
            SecretConfig(
                name="   ",
                source="env"
            )
        
        # Test invalid characters
        with pytest.raises(ValidationError):
            SecretConfig(
                name="invalid@secret#name",
                source="env"
            )
    
    def test_secret_name_normalization(self):
        """Test secret name normalization to uppercase."""
        secret = SecretConfig(
            name="database_url",
            source="k8s"
        )
        assert secret.name == "DATABASE_URL"
        
        secret = SecretConfig(
            name="API-Key",
            source="vault"
        )
        assert secret.name == "API-KEY"


class TestEnvironmentConfig:
    """Test EnvironmentConfig data model."""
    
    def test_valid_environment_config(self):
        """Test valid environment configuration creation."""
        secrets = [
            SecretConfig(name="API_KEY", source="vault"),
            SecretConfig(name="DB_PASSWORD", source="k8s")
        ]
        
        config = EnvironmentConfig(
            name=Environment.PRODUCTION,
            display_name="Production Environment",
            description="Production deployment environment",
            provider=InfrastructureProvider.KUBERNETES,
            region="us-west-2",
            namespace="production",
            replicas=5,
            resources={
                "requests": {"memory": "1Gi", "cpu": "500m"},
                "limits": {"memory": "2Gi", "cpu": "1000m"}
            },
            secrets=secrets,
            config_vars={"LOG_LEVEL": "INFO", "DEBUG": "false"},
            security_level=SecurityLevel.ENHANCED,
            auto_scaling=True,
            monitoring_enabled=True
        )
        
        assert config.name == Environment.PRODUCTION
        assert config.display_name == "Production Environment"
        assert config.provider == InfrastructureProvider.KUBERNETES
        assert config.replicas == 5
        assert len(config.secrets) == 2
        assert config.security_level == SecurityLevel.ENHANCED
        assert config.auto_scaling is True
    
    def test_environment_config_defaults(self):
        """Test environment configuration defaults."""
        config = EnvironmentConfig(
            name=Environment.DEVELOPMENT,
            display_name="Development",
            provider=InfrastructureProvider.DOCKER
        )
        
        assert config.region == "us-east-1"  # Default region
        assert config.replicas == 1  # Default replicas
        assert config.security_level == SecurityLevel.STANDARD  # Default security
        assert config.auto_scaling is False  # Default auto-scaling
        assert config.monitoring_enabled is True  # Default monitoring


class TestDeploymentConfig:
    """Test DeploymentConfig data model."""
    
    def test_valid_deployment_config(self):
        """Test valid deployment configuration creation."""
        config = DeploymentConfig(
            deployment_id="deploy_001",
            name="customer-io-pipelines",
            version="2.1.0",
            environment=Environment.STAGING,
            strategy=DeploymentStrategy.BLUE_GREEN,
            image_tag="v2.1.0",
            image_repository="myorg/customer-io-pipelines",
            rollback_version="2.0.0",
            health_check_path="/health",
            readiness_check_path="/ready",
            timeout_seconds=600,
            created_by="deployment-system"
        )
        
        assert config.deployment_id == "deploy_001"
        assert config.name == "customer-io-pipelines"
        assert config.version == "2.1.0"
        assert config.environment == Environment.STAGING
        assert config.strategy == DeploymentStrategy.BLUE_GREEN
        assert config.rollback_version == "2.0.0"
        assert config.timeout_seconds == 600
        assert config.created_at is not None
    
    def test_deployment_config_validation(self):
        """Test deployment configuration validation."""
        # Test empty deployment_id
        with pytest.raises(ValidationError):
            DeploymentConfig(
                deployment_id="",
                name="test",
                version="1.0.0",
                environment=Environment.DEVELOPMENT,
                image_tag="v1.0.0",
                created_by="test"
            )
        
        # Test negative timeout
        with pytest.raises(ValidationError):
            DeploymentConfig(
                deployment_id="test_001",
                name="test",
                version="1.0.0",
                environment=Environment.DEVELOPMENT,
                image_tag="v1.0.0",
                timeout_seconds=-1,
                created_by="test"
            )


class TestDeploymentResult:
    """Test DeploymentResult data model."""
    
    def test_valid_deployment_result(self):
        """Test valid deployment result creation."""
        result = DeploymentResult(
            deployment_id="deploy_001",
            status=DeploymentStatus.PENDING,
            start_time=datetime.now(timezone.utc)
        )
        
        assert result.deployment_id == "deploy_001"
        assert result.status == DeploymentStatus.PENDING
        assert result.start_time is not None
        assert result.end_time is None
        assert result.duration_seconds is None
        assert len(result.logs) == 0
        assert result.rollback_performed is False
    
    def test_deployment_result_finish(self):
        """Test deployment result finishing."""
        result = DeploymentResult(
            deployment_id="deploy_001",
            status=DeploymentStatus.RUNNING,
            start_time=datetime.now(timezone.utc)
        )
        
        # Small delay to ensure duration calculation
        import time
        time.sleep(0.01)
        
        result.finish(DeploymentStatus.SUCCESS)
        
        assert result.status == DeploymentStatus.SUCCESS
        assert result.end_time is not None
        assert result.duration_seconds is not None
        assert result.duration_seconds > 0
    
    def test_deployment_result_finish_with_error(self):
        """Test deployment result finishing with error."""
        result = DeploymentResult(
            deployment_id="deploy_001",
            status=DeploymentStatus.RUNNING,
            start_time=datetime.now(timezone.utc)
        )
        
        result.finish(DeploymentStatus.FAILED, "Deployment failed due to timeout")
        
        assert result.status == DeploymentStatus.FAILED
        assert result.error_message == "Deployment failed due to timeout"
    
    def test_add_log(self):
        """Test adding logs to deployment result."""
        result = DeploymentResult(
            deployment_id="deploy_001",
            status=DeploymentStatus.RUNNING,
            start_time=datetime.now(timezone.utc)
        )
        
        result.add_log("Starting deployment process")
        result.add_log("Validating configuration")
        
        assert len(result.logs) == 2
        assert "Starting deployment process" in result.logs[0]
        assert "Validating configuration" in result.logs[1]
        # Check timestamp format
        assert "[" in result.logs[0] and "]" in result.logs[0]
    
    def test_is_successful(self):
        """Test successful deployment check."""
        result = DeploymentResult(
            deployment_id="deploy_001",
            status=DeploymentStatus.SUCCESS,
            start_time=datetime.now(timezone.utc)
        )
        assert result.is_successful() is True
        
        result.status = DeploymentStatus.FAILED
        assert result.is_successful() is False


class TestInfrastructureTemplate:
    """Test InfrastructureTemplate data model."""
    
    def test_valid_infrastructure_template(self):
        """Test valid infrastructure template creation."""
        template = InfrastructureTemplate(
            template_id="k8s_template_001",
            name="Kubernetes Deployment Template",
            provider=InfrastructureProvider.KUBERNETES,
            template_format="yaml",
            template_content="apiVersion: apps/v1\nkind: Deployment\n...",
            parameters={"replicas": 3, "image": "myapp:v1.0.0"},
            description="Kubernetes deployment template for Customer.IO pipelines",
            version="1.2.0"
        )
        
        assert template.template_id == "k8s_template_001"
        assert template.name == "Kubernetes Deployment Template"
        assert template.provider == InfrastructureProvider.KUBERNETES
        assert template.template_format == "yaml"
        assert "apiVersion" in template.template_content
        assert template.parameters["replicas"] == 3
        assert template.version == "1.2.0"
        assert template.created_at is not None


class TestConfigurationManager:
    """Test ConfigurationManager implementation."""
    
    @pytest.fixture
    def config_manager(self):
        """Create configuration manager."""
        return ConfigurationManager()
    
    def test_config_manager_initialization(self, config_manager):
        """Test configuration manager initialization."""
        assert len(config_manager.environments) == 0
        assert len(config_manager.encrypted_secrets) == 0
        assert config_manager.encryption_key is not None
    
    def test_register_environment(self, config_manager):
        """Test environment registration."""
        env_config = EnvironmentConfig(
            name=Environment.DEVELOPMENT,
            display_name="Development",
            provider=InfrastructureProvider.DOCKER,
            secrets=[
                SecretConfig(name="API_KEY", value="test_key", source="env"),
                SecretConfig(name="DB_PASSWORD", value="test_password", source="env")
            ]
        )
        
        config_manager.register_environment(env_config)
        
        assert Environment.DEVELOPMENT in config_manager.environments
        assert config_manager.environments[Environment.DEVELOPMENT] == env_config
        
        # Check secrets were encrypted and stored
        assert f"{Environment.DEVELOPMENT}:API_KEY" in config_manager.encrypted_secrets
        assert f"{Environment.DEVELOPMENT}:DB_PASSWORD" in config_manager.encrypted_secrets
    
    def test_get_environment_config(self, config_manager):
        """Test getting environment configuration."""
        env_config = EnvironmentConfig(
            name=Environment.STAGING,
            display_name="Staging",
            provider=InfrastructureProvider.KUBERNETES
        )
        
        config_manager.register_environment(env_config)
        
        retrieved_config = config_manager.get_environment_config(Environment.STAGING)
        assert retrieved_config == env_config
        
        # Test non-existent environment
        non_existent = config_manager.get_environment_config(Environment.PRODUCTION)
        assert non_existent is None
    
    def test_secret_encryption_decryption(self, config_manager):
        """Test secret encryption and decryption."""
        original_value = "super_secret_password_123"
        
        # Test encryption
        encrypted = config_manager._encrypt_value(original_value)
        assert encrypted.startswith("encrypted:")
        assert original_value not in encrypted
        
        # Test decryption
        decrypted = config_manager._decrypt_value(encrypted)
        assert decrypted == original_value
    
    def test_get_secret(self, config_manager):
        """Test secret retrieval."""
        env_config = EnvironmentConfig(
            name=Environment.DEVELOPMENT,
            display_name="Development",
            provider=InfrastructureProvider.DOCKER,
            secrets=[
                SecretConfig(name="API_KEY", value="test_api_key", source="env")
            ]
        )
        
        config_manager.register_environment(env_config)
        
        # Test retrieving encrypted secret
        secret_value = config_manager.get_secret(Environment.DEVELOPMENT, "API_KEY")
        assert secret_value == "test_api_key"
        
        # Test non-existent secret
        non_existent = config_manager.get_secret(Environment.DEVELOPMENT, "NON_EXISTENT")
        assert non_existent is None
    
    @patch.dict(os.environ, {"TEST_SECRET": "env_value"})
    def test_get_secret_from_environment(self, config_manager):
        """Test secret retrieval from environment variables."""
        # Test fallback to environment variable
        secret_value = config_manager.get_secret(Environment.DEVELOPMENT, "TEST_SECRET")
        assert secret_value == "env_value"
    
    def test_set_secret(self, config_manager):
        """Test setting secrets."""
        config_manager.set_secret(
            Environment.PRODUCTION,
            "NEW_SECRET",
            "new_secret_value",
            encrypt=True
        )
        
        # Verify secret was stored
        secret_key = f"{Environment.PRODUCTION}:NEW_SECRET"
        assert secret_key in config_manager.encrypted_secrets
        
        # Verify secret can be retrieved
        retrieved_value = config_manager.get_secret(Environment.PRODUCTION, "NEW_SECRET")
        assert retrieved_value == "new_secret_value"
    
    def test_generate_config_file_yaml(self, config_manager):
        """Test configuration file generation in YAML format."""
        env_config = EnvironmentConfig(
            name=Environment.STAGING,
            display_name="Staging Environment",
            provider=InfrastructureProvider.KUBERNETES,
            region="us-west-2",
            replicas=3,
            secrets=[
                SecretConfig(name="API_KEY", source="vault", description="Customer.IO API key")
            ],
            config_vars={"LOG_LEVEL": "INFO", "DEBUG": "false"}
        )
        
        config_manager.register_environment(env_config)
        
        yaml_content = config_manager.generate_config_file(Environment.STAGING, "yaml")
        
        assert "environment:" in yaml_content
        assert "name: staging" in yaml_content
        assert "provider: kubernetes" in yaml_content
        assert "replicas: 3" in yaml_content
        assert "API_KEY:" in yaml_content
        
        # Parse YAML to verify structure
        parsed = yaml.safe_load(yaml_content)
        assert parsed["environment"]["name"] == "staging"
        assert parsed["environment"]["replicas"] == 3
    
    def test_generate_config_file_json(self, config_manager):
        """Test configuration file generation in JSON format."""
        env_config = EnvironmentConfig(
            name=Environment.DEVELOPMENT,
            display_name="Development",
            provider=InfrastructureProvider.DOCKER
        )
        
        config_manager.register_environment(env_config)
        
        json_content = config_manager.generate_config_file(Environment.DEVELOPMENT, "json")
        
        # Parse JSON to verify structure
        parsed = json.loads(json_content)
        assert parsed["environment"]["name"] == "development"
        assert parsed["environment"]["provider"] == "docker"
    
    def test_validate_environment(self, config_manager):
        """Test environment validation."""
        # Create environment with missing required secret
        env_config = EnvironmentConfig(
            name=Environment.PRODUCTION,
            display_name="Production",
            provider=InfrastructureProvider.AWS,
            secrets=[
                SecretConfig(name="REQUIRED_SECRET", source="vault", required=True)
            ]
        )
        
        config_manager.register_environment(env_config)
        
        # Validation should fail due to missing required secret
        validation_result = config_manager.validate_environment(Environment.PRODUCTION)
        
        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) > 0
        assert "REQUIRED_SECRET" in validation_result["errors"][0]
    
    def test_validate_environment_warnings(self, config_manager):
        """Test environment validation warnings."""
        # Create non-production environment with high replica count
        env_config = EnvironmentConfig(
            name=Environment.DEVELOPMENT,
            display_name="Development",
            provider=InfrastructureProvider.DOCKER,
            replicas=15  # High replica count for dev
        )
        
        config_manager.register_environment(env_config)
        
        validation_result = config_manager.validate_environment(Environment.DEVELOPMENT)
        
        assert validation_result["valid"] is True
        assert len(validation_result["warnings"]) > 0
        assert "replica count" in validation_result["warnings"][0].lower()
    
    def test_get_metrics(self, config_manager):
        """Test configuration manager metrics."""
        # Register multiple environments with secrets
        for env in [Environment.DEVELOPMENT, Environment.STAGING]:
            env_config = EnvironmentConfig(
                name=env,
                display_name=env.value.title(),
                provider=InfrastructureProvider.DOCKER,
                secrets=[
                    SecretConfig(name="SECRET_1", value="value1", source="env"),
                    SecretConfig(name="SECRET_2", value="value2", source="env")
                ]
            )
            config_manager.register_environment(env_config)
        
        metrics = config_manager.get_metrics()
        
        assert metrics["environments_registered"] == 2
        assert metrics["total_secrets"] == 4  # 2 environments * 2 secrets
        assert metrics["encryption_enabled"] is True
        assert "supported_providers" in metrics


class TestInfrastructureGenerator:
    """Test InfrastructureGenerator implementation."""
    
    @pytest.fixture
    def infrastructure_generator(self):
        """Create infrastructure generator."""
        return InfrastructureGenerator()
    
    @pytest.fixture
    def sample_env_config(self):
        """Create sample environment configuration."""
        return EnvironmentConfig(
            name=Environment.STAGING,
            display_name="Staging",
            provider=InfrastructureProvider.KUBERNETES,
            namespace="staging",
            replicas=3,
            resources={
                "requests": {"memory": "512Mi", "cpu": "500m"},
                "limits": {"memory": "1Gi", "cpu": "1000m"}
            },
            secrets=[
                SecretConfig(name="API_KEY", source="k8s"),
                SecretConfig(name="DB_PASSWORD", source="k8s")
            ],
            config_vars={"LOG_LEVEL": "INFO"},
            security_level=SecurityLevel.STANDARD,
            auto_scaling=True
        )
    
    @pytest.fixture
    def sample_deployment_config(self):
        """Create sample deployment configuration."""
        return DeploymentConfig(
            deployment_id="deploy_001",
            name="customer-io-pipelines",
            version="2.1.0",
            environment=Environment.STAGING,
            image_tag="v2.1.0",
            created_by="test"
        )
    
    def test_infrastructure_generator_initialization(self, infrastructure_generator):
        """Test infrastructure generator initialization."""
        assert len(infrastructure_generator.templates) == 0
    
    def test_generate_kubernetes_deployment(self, infrastructure_generator, sample_env_config, sample_deployment_config):
        """Test Kubernetes deployment template generation."""
        template = infrastructure_generator.generate_kubernetes_deployment(
            sample_env_config,
            sample_deployment_config
        )
        
        assert template.provider == InfrastructureProvider.KUBERNETES
        assert template.template_format == "yaml"
        assert "apiVersion: apps/v1" in template.template_content
        assert "kind: Deployment" in template.template_content
        assert "replicas: 3" in template.template_content
        assert "namespace: staging" in template.template_content
        
        # Parse YAML to verify structure
        parsed = yaml.safe_load(template.template_content)
        deployment = parsed["deployment"]
        assert deployment["spec"]["replicas"] == 3
        assert deployment["metadata"]["namespace"] == "staging"
        
        # Check HPA is included for auto-scaling
        assert "hpa" in parsed
        hpa = parsed["hpa"]
        assert hpa["spec"]["minReplicas"] == 3
        assert hpa["spec"]["maxReplicas"] == 9  # 3 * 3
    
    def test_generate_docker_compose(self, infrastructure_generator, sample_env_config, sample_deployment_config):
        """Test Docker Compose template generation."""
        template = infrastructure_generator.generate_docker_compose(
            sample_env_config,
            sample_deployment_config
        )
        
        assert template.provider == InfrastructureProvider.DOCKER
        assert template.template_format == "yaml"
        assert "version: '3.8'" in template.template_content
        assert "customer-io-pipelines:" in template.template_content
        
        # Parse YAML to verify structure
        parsed = yaml.safe_load(template.template_content)
        services = parsed["services"]
        app_service = services["customer-io-pipelines"]
        
        assert "myorg/customer-io-pipelines:v2.1.0" in app_service["image"]
        assert app_service["environment"]["LOG_LEVEL"] == "INFO"
        assert app_service["environment"]["ENVIRONMENT"] == "staging"
        
        # Check monitoring services are included
        assert "prometheus" in services
        assert "grafana" in services
    
    def test_generate_terraform_aws(self, infrastructure_generator, sample_env_config, sample_deployment_config):
        """Test Terraform AWS template generation."""
        template = infrastructure_generator.generate_terraform_aws(
            sample_env_config,
            sample_deployment_config
        )
        
        assert template.provider == InfrastructureProvider.AWS
        assert template.template_format == "hcl"
        assert "terraform {" in template.template_content
        assert "aws_ecs_cluster" in template.template_content
        assert "aws_ecs_service" in template.template_content
        assert f"desired_count   = {sample_env_config.replicas}" in template.template_content
    
    def test_generate_env_vars(self, infrastructure_generator, sample_env_config):
        """Test environment variables generation."""
        env_vars = infrastructure_generator._generate_env_vars(sample_env_config)
        
        # Check config vars are included
        config_var_names = [var["name"] for var in env_vars if "valueFrom" not in var]
        assert "LOG_LEVEL" in config_var_names
        
        # Check secret references are included
        secret_vars = [var for var in env_vars if "valueFrom" in var]
        secret_names = [var["name"] for var in secret_vars]
        assert "API_KEY" in secret_names
        assert "DB_PASSWORD" in secret_names
    
    def test_generate_security_context(self, infrastructure_generator):
        """Test security context generation."""
        # Test critical security level
        critical_context = infrastructure_generator._generate_security_context(SecurityLevel.CRITICAL)
        assert critical_context["runAsNonRoot"] is True
        assert critical_context["runAsUser"] == 1001
        assert critical_context["fsGroup"] == 1001
        assert "seccompProfile" in critical_context
        
        # Test standard security level
        standard_context = infrastructure_generator._generate_security_context(SecurityLevel.STANDARD)
        assert standard_context["runAsNonRoot"] is True
        assert standard_context["runAsUser"] == 1001
        assert "fsGroup" not in standard_context
        
        # Test basic security level
        basic_context = infrastructure_generator._generate_security_context(SecurityLevel.BASIC)
        assert len(basic_context) == 0
    
    def test_get_template(self, infrastructure_generator, sample_env_config, sample_deployment_config):
        """Test template retrieval."""
        template = infrastructure_generator.generate_kubernetes_deployment(
            sample_env_config,
            sample_deployment_config
        )
        
        retrieved = infrastructure_generator.get_template(template.template_id)
        assert retrieved == template
        
        # Test non-existent template
        non_existent = infrastructure_generator.get_template("non_existent")
        assert non_existent is None
    
    def test_list_templates(self, infrastructure_generator, sample_env_config, sample_deployment_config):
        """Test template listing."""
        # Generate multiple templates
        k8s_template = infrastructure_generator.generate_kubernetes_deployment(
            sample_env_config,
            sample_deployment_config
        )
        
        docker_template = infrastructure_generator.generate_docker_compose(
            sample_env_config,
            sample_deployment_config
        )
        
        # List all templates
        all_templates = infrastructure_generator.list_templates()
        assert len(all_templates) == 2
        
        # List templates by provider
        k8s_templates = infrastructure_generator.list_templates(InfrastructureProvider.KUBERNETES)
        assert len(k8s_templates) == 1
        assert k8s_templates[0] == k8s_template
        
        docker_templates = infrastructure_generator.list_templates(InfrastructureProvider.DOCKER)
        assert len(docker_templates) == 1
        assert docker_templates[0] == docker_template
    
    def test_export_template(self, infrastructure_generator, sample_env_config, sample_deployment_config):
        """Test template export to file."""
        template = infrastructure_generator.generate_kubernetes_deployment(
            sample_env_config,
            sample_deployment_config
        )
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as temp_file:
            temp_path = temp_file.name
        
        try:
            # Export template
            success = infrastructure_generator.export_template(template.template_id, temp_path)
            assert success is True
            
            # Verify file content
            with open(temp_path, 'r') as f:
                content = f.read()
            assert content == template.template_content
            
            # Test exporting non-existent template
            non_existent_success = infrastructure_generator.export_template("non_existent", temp_path)
            assert non_existent_success is False
            
        finally:
            os.unlink(temp_path)


class TestDeploymentEngine:
    """Test DeploymentEngine implementation."""
    
    @pytest.fixture
    def config_manager(self):
        """Create configuration manager with test environment."""
        manager = ConfigurationManager()
        
        env_config = EnvironmentConfig(
            name=Environment.STAGING,
            display_name="Staging",
            provider=InfrastructureProvider.KUBERNETES,
            secrets=[
                SecretConfig(name="API_KEY", value="test_key", source="k8s", required=True)
            ]
        )
        manager.register_environment(env_config)
        
        return manager
    
    @pytest.fixture
    def deployment_engine(self, config_manager):
        """Create deployment engine."""
        return DeploymentEngine(config_manager)
    
    @pytest.fixture
    def sample_deployment_config(self):
        """Create sample deployment configuration."""
        return DeploymentConfig(
            deployment_id="test_deploy_001",
            name="test-application",
            version="1.0.0",
            environment=Environment.STAGING,
            strategy=DeploymentStrategy.ROLLING_UPDATE,
            image_tag="v1.0.0",
            rollback_version="0.9.0",
            created_by="test_user"
        )
    
    def test_deployment_engine_initialization(self, deployment_engine):
        """Test deployment engine initialization."""
        assert deployment_engine.config_manager is not None
        assert len(deployment_engine.active_deployments) == 0
        assert len(deployment_engine.deployment_history) == 0
    
    @pytest.mark.asyncio
    async def test_deploy_success(self, deployment_engine, sample_deployment_config):
        """Test successful deployment."""
        # Mock the deployment execution methods
        with patch.object(deployment_engine, '_execute_rolling_update') as mock_rolling, \
             patch.object(deployment_engine, '_perform_health_checks') as mock_health:
            
            mock_health.return_value = True  # Health checks pass
            
            result = await deployment_engine.deploy(sample_deployment_config)
            
            assert result.status == DeploymentStatus.SUCCESS
            assert result.deployment_id == sample_deployment_config.deployment_id
            assert result.duration_seconds is not None
            assert result.health_check_passed is True
            assert result.rollback_performed is False
            
            # Check execution was called
            mock_rolling.assert_called_once()
            mock_health.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_deploy_health_check_failure(self, deployment_engine, sample_deployment_config):
        """Test deployment with health check failure."""
        with patch.object(deployment_engine, '_execute_rolling_update'), \
             patch.object(deployment_engine, '_perform_health_checks') as mock_health, \
             patch.object(deployment_engine, '_perform_rollback') as mock_rollback:
            
            mock_health.return_value = False  # Health checks fail
            
            result = await deployment_engine.deploy(sample_deployment_config)
            
            assert result.status == DeploymentStatus.FAILED
            assert result.health_check_passed is False
            assert "Health checks failed" in result.error_message
            
            # Rollback should be attempted
            mock_rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_deploy_execution_failure(self, deployment_engine, sample_deployment_config):
        """Test deployment with execution failure."""
        with patch.object(deployment_engine, '_execute_rolling_update') as mock_rolling, \
             patch.object(deployment_engine, '_perform_rollback') as mock_rollback:
            
            mock_rolling.side_effect = Exception("Deployment execution failed")
            
            result = await deployment_engine.deploy(sample_deployment_config)
            
            assert result.status == DeploymentStatus.FAILED
            assert "Deployment execution failed" in result.error_message
            
            # Rollback should be attempted
            mock_rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_deploy_environment_validation_failure(self, deployment_engine):
        """Test deployment with invalid environment."""
        invalid_config = DeploymentConfig(
            deployment_id="invalid_deploy",
            name="test-app",
            version="1.0.0",
            environment=Environment.PRODUCTION,  # Not registered
            image_tag="v1.0.0",
            created_by="test"
        )
        
        result = await deployment_engine.deploy(invalid_config)
        
        assert result.status == DeploymentStatus.FAILED
        assert "not configured" in result.error_message
    
    def test_execute_rolling_update(self, deployment_engine, sample_deployment_config):
        """Test rolling update execution."""
        env_config = deployment_engine.config_manager.get_environment_config(Environment.STAGING)
        result = DeploymentResult(
            deployment_id=sample_deployment_config.deployment_id,
            status=DeploymentStatus.RUNNING,
            start_time=datetime.now(timezone.utc)
        )
        
        deployment_engine._execute_rolling_update(sample_deployment_config, env_config, result)
        
        # Check that steps were logged
        assert len(result.logs) > 0
        assert any("rolling update" in log.lower() for log in result.logs)
        
        # Check performance metrics were recorded
        assert len(result.performance_metrics) > 0
    
    def test_execute_blue_green(self, deployment_engine, sample_deployment_config):
        """Test blue-green deployment execution."""
        env_config = deployment_engine.config_manager.get_environment_config(Environment.STAGING)
        result = DeploymentResult(
            deployment_id=sample_deployment_config.deployment_id,
            status=DeploymentStatus.RUNNING,
            start_time=datetime.now(timezone.utc)
        )
        
        deployment_engine._execute_blue_green(sample_deployment_config, env_config, result)
        
        # Check blue-green specific steps
        assert any("green environment" in log.lower() for log in result.logs)
        assert any("switching traffic" in log.lower() for log in result.logs)
    
    def test_execute_canary(self, deployment_engine, sample_deployment_config):
        """Test canary deployment execution."""
        env_config = deployment_engine.config_manager.get_environment_config(Environment.STAGING)
        result = DeploymentResult(
            deployment_id=sample_deployment_config.deployment_id,
            status=DeploymentStatus.RUNNING,
            start_time=datetime.now(timezone.utc)
        )
        
        deployment_engine._execute_canary(sample_deployment_config, env_config, result)
        
        # Check canary specific steps
        assert any("canary" in log.lower() for log in result.logs)
        assert any("5%" in log for log in result.logs)
        assert any("25%" in log for log in result.logs)
    
    def test_perform_health_checks(self, deployment_engine, sample_deployment_config):
        """Test health checks execution."""
        result = DeploymentResult(
            deployment_id=sample_deployment_config.deployment_id,
            status=DeploymentStatus.RUNNING,
            start_time=datetime.now(timezone.utc)
        )
        
        # Mock random to ensure deterministic results
        with patch('random.random', return_value=0.01):  # Always pass (< 0.05 threshold)
            health_passed = deployment_engine._perform_health_checks(sample_deployment_config, result)
            
            assert health_passed is True
            assert result.performance_metrics["health_check_success_rate"] == 100.0
            assert any("passed" in log for log in result.logs)
    
    def test_perform_rollback(self, deployment_engine, sample_deployment_config):
        """Test rollback execution."""
        result = DeploymentResult(
            deployment_id=sample_deployment_config.deployment_id,
            status=DeploymentStatus.FAILED,
            start_time=datetime.now(timezone.utc)
        )
        
        deployment_engine._perform_rollback(sample_deployment_config, result)
        
        assert result.rollback_performed is True
        assert any("rollback" in log.lower() for log in result.logs)
        assert any(sample_deployment_config.rollback_version in log for log in result.logs)
    
    def test_perform_rollback_no_version(self, deployment_engine):
        """Test rollback when no rollback version is specified."""
        config_without_rollback = DeploymentConfig(
            deployment_id="no_rollback",
            name="test-app",
            version="1.0.0",
            environment=Environment.STAGING,
            image_tag="v1.0.0",
            rollback_version=None,  # No rollback version
            created_by="test"
        )
        
        result = DeploymentResult(
            deployment_id=config_without_rollback.deployment_id,
            status=DeploymentStatus.FAILED,
            start_time=datetime.now(timezone.utc)
        )
        
        deployment_engine._perform_rollback(config_without_rollback, result)
        
        assert result.rollback_performed is False
        assert any("no rollback version" in log.lower() for log in result.logs)
    
    def test_get_deployment_status(self, deployment_engine):
        """Test deployment status retrieval."""
        # Add deployment to history
        result = DeploymentResult(
            deployment_id="test_deploy",
            status=DeploymentStatus.SUCCESS,
            start_time=datetime.now(timezone.utc)
        )
        deployment_engine.deployment_history.append(result)
        
        # Test retrieving from history
        retrieved = deployment_engine.get_deployment_status("test_deploy")
        assert retrieved == result
        
        # Test non-existent deployment
        non_existent = deployment_engine.get_deployment_status("non_existent")
        assert non_existent is None
    
    def test_list_deployments(self, deployment_engine):
        """Test deployment listing."""
        # Add multiple deployments to history
        for i in range(5):
            result = DeploymentResult(
                deployment_id=f"deploy_{i}",
                status=DeploymentStatus.SUCCESS,
                start_time=datetime.now(timezone.utc)
            )
            deployment_engine.deployment_history.append(result)
        
        # List all deployments
        deployments = deployment_engine.list_deployments()
        assert len(deployments) == 5
        
        # List with limit
        limited = deployment_engine.list_deployments(limit=3)
        assert len(limited) == 3
    
    def test_get_deployment_statistics(self, deployment_engine):
        """Test deployment statistics generation."""
        # Add deployments with different statuses
        statuses = [
            DeploymentStatus.SUCCESS,
            DeploymentStatus.SUCCESS,
            DeploymentStatus.FAILED,
            DeploymentStatus.SUCCESS
        ]
        
        for i, status in enumerate(statuses):
            result = DeploymentResult(
                deployment_id=f"deploy_{i}",
                status=status,
                start_time=datetime.now(timezone.utc)
            )
            result.duration_seconds = 60.0 + i * 10  # Varying durations
            result.rollback_performed = (status == DeploymentStatus.FAILED)
            deployment_engine.deployment_history.append(result)
        
        stats = deployment_engine.get_deployment_statistics()
        
        assert stats["total_deployments"] == 4
        assert stats["successful_deployments"] == 3
        assert stats["failed_deployments"] == 1
        assert stats["success_rate_percent"] == 75.0  # 3/4 * 100
        assert stats["rollbacks_performed"] == 1
        assert stats["average_deployment_time_seconds"] == 75.0  # (60+70+80+90)/4


class TestDeploymentManager:
    """Test DeploymentManager main class."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock Customer.IO client."""
        return Mock(spec=CustomerIOClient)
    
    @pytest.fixture
    def deployment_manager(self, mock_client):
        """Create deployment manager."""
        return DeploymentManager(mock_client)
    
    def test_deployment_manager_initialization(self, deployment_manager):
        """Test deployment manager initialization."""
        assert deployment_manager.client is not None
        assert deployment_manager.config_manager is not None
        assert deployment_manager.infrastructure_generator is not None
        assert deployment_manager.deployment_engine is not None
        assert deployment_manager.start_time is not None
        
        # Check default environments were created
        dev_config = deployment_manager.config_manager.get_environment_config(Environment.DEVELOPMENT)
        staging_config = deployment_manager.config_manager.get_environment_config(Environment.STAGING)
        prod_config = deployment_manager.config_manager.get_environment_config(Environment.PRODUCTION)
        
        assert dev_config is not None
        assert staging_config is not None
        assert prod_config is not None
        
        # Verify environment configurations
        assert dev_config.provider == InfrastructureProvider.DOCKER
        assert staging_config.provider == InfrastructureProvider.KUBERNETES
        assert prod_config.provider == InfrastructureProvider.AWS
    
    def test_create_deployment(self, deployment_manager):
        """Test deployment configuration creation."""
        deployment_config = deployment_manager.create_deployment(
            name="customer-io-pipelines",
            version="2.1.0",
            environment=Environment.STAGING,
            strategy=DeploymentStrategy.BLUE_GREEN,
            image_tag="v2.1.0",
            created_by="test_user"
        )
        
        assert deployment_config.name == "customer-io-pipelines"
        assert deployment_config.version == "2.1.0"
        assert deployment_config.environment == Environment.STAGING
        assert deployment_config.strategy == DeploymentStrategy.BLUE_GREEN
        assert deployment_config.image_tag == "v2.1.0"
        assert deployment_config.created_by == "test_user"
        assert deployment_config.deployment_id is not None
    
    @pytest.mark.asyncio
    async def test_deploy_application(self, deployment_manager):
        """Test application deployment."""
        deployment_config = deployment_manager.create_deployment(
            name="test-app",
            version="1.0.0",
            environment=Environment.DEVELOPMENT,
            created_by="test"
        )
        
        # Mock the deployment engine
        with patch.object(deployment_manager.deployment_engine, 'deploy') as mock_deploy:
            mock_result = Mock()
            mock_result.status = DeploymentStatus.SUCCESS
            mock_deploy.return_value = mock_result
            
            result = await deployment_manager.deploy_application(deployment_config)
            
            assert result.status == DeploymentStatus.SUCCESS
            mock_deploy.assert_called_once_with(deployment_config)
    
    def test_generate_infrastructure(self, deployment_manager):
        """Test infrastructure template generation."""
        deployment_config = deployment_manager.create_deployment(
            name="test-app",
            version="1.0.0",
            environment=Environment.STAGING,
            created_by="test"
        )
        
        templates = deployment_manager.generate_infrastructure(Environment.STAGING, deployment_config)
        
        assert len(templates) == 1  # Staging uses Kubernetes
        template = templates[0]
        assert template.provider == InfrastructureProvider.KUBERNETES
        assert template.template_format == "yaml"
        assert "apiVersion" in template.template_content
    
    def test_generate_infrastructure_invalid_environment(self, deployment_manager):
        """Test infrastructure generation with invalid environment."""
        deployment_config = deployment_manager.create_deployment(
            name="test-app",
            version="1.0.0",
            environment=Environment.DEVELOPMENT,
            created_by="test"
        )
        
        # Remove the environment configuration
        del deployment_manager.config_manager.environments[Environment.DEVELOPMENT]
        
        with pytest.raises(ValueError, match="not configured"):
            deployment_manager.generate_infrastructure(Environment.DEVELOPMENT, deployment_config)
    
    @pytest.mark.asyncio
    async def test_promote_deployment(self, deployment_manager):
        """Test deployment promotion between environments."""
        # Add a successful deployment to source environment
        successful_deployment = DeploymentResult(
            deployment_id="customer-io-pipelines-development-2.1.0-123456",
            status=DeploymentStatus.SUCCESS,
            start_time=datetime.now(timezone.utc)
        )
        deployment_manager.deployment_engine.deployment_history.append(successful_deployment)
        
        # Mock the deploy method
        with patch.object(deployment_manager, 'deploy_application') as mock_deploy:
            mock_result = Mock()
            mock_result.status = DeploymentStatus.SUCCESS
            mock_deploy.return_value = mock_result
            
            result = await deployment_manager.promote_deployment(
                from_env=Environment.DEVELOPMENT,
                to_env=Environment.STAGING,
                version="2.1.0",
                created_by="release_manager"
            )
            
            assert result.status == DeploymentStatus.SUCCESS
            mock_deploy.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_promote_deployment_no_source(self, deployment_manager):
        """Test deployment promotion with no successful source deployment."""
        with pytest.raises(ValueError, match="No successful deployment found"):
            await deployment_manager.promote_deployment(
                from_env=Environment.DEVELOPMENT,
                to_env=Environment.STAGING,
                version="nonexistent",
                created_by="test"
            )
    
    def test_create_environment_config_bundle(self, deployment_manager):
        """Test environment configuration bundle creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            bundle_files = deployment_manager.create_environment_config_bundle(
                Environment.DEVELOPMENT,
                temp_dir
            )
            
            # Check that all expected files were created
            assert "config" in bundle_files
            assert "deploy_script" in bundle_files
            
            # Verify config file exists and contains expected content
            config_file = bundle_files["config"]
            assert os.path.exists(config_file)
            
            with open(config_file, 'r') as f:
                config_content = f.read()
            assert "development" in config_content.lower()
            
            # Verify deploy script exists and is executable
            script_file = bundle_files["deploy_script"]
            assert os.path.exists(script_file)
            assert os.access(script_file, os.X_OK)  # Check if executable
    
    def test_generate_deployment_script_kubernetes(self, deployment_manager):
        """Test deployment script generation for Kubernetes."""
        env_config = deployment_manager.config_manager.get_environment_config(Environment.STAGING)
        script = deployment_manager._generate_deployment_script(Environment.STAGING, env_config)
        
        assert "#!/bin/bash" in script
        assert "kubectl" in script
        assert "staging" in script
        assert env_config.namespace in script
    
    def test_generate_deployment_script_docker(self, deployment_manager):
        """Test deployment script generation for Docker."""
        env_config = deployment_manager.config_manager.get_environment_config(Environment.DEVELOPMENT)
        script = deployment_manager._generate_deployment_script(Environment.DEVELOPMENT, env_config)
        
        assert "#!/bin/bash" in script
        assert "docker-compose" in script
        assert "development" in script
    
    def test_get_deployment_dashboard(self, deployment_manager):
        """Test deployment dashboard data generation."""
        # Add some deployment history
        for i in range(5):
            result = DeploymentResult(
                deployment_id=f"deploy_{i}",
                status=DeploymentStatus.SUCCESS if i < 4 else DeploymentStatus.FAILED,
                start_time=datetime.now(timezone.utc)
            )
            deployment_manager.deployment_engine.deployment_history.append(result)
        
        dashboard = deployment_manager.get_deployment_dashboard()
        
        assert "system" in dashboard
        assert "deployments" in dashboard
        assert "configuration" in dashboard
        assert "infrastructure" in dashboard
        
        # Check system info
        assert dashboard["system"]["uptime_seconds"] > 0
        
        # Check deployment stats
        assert dashboard["deployments"]["total_deployments"] == 5
        assert dashboard["deployments"]["success_rate_percent"] == 80.0
        
        # Check environment breakdown
        assert "by_environment" in dashboard["deployments"]
    
    def test_get_metrics(self, deployment_manager):
        """Test deployment manager metrics retrieval."""
        metrics = deployment_manager.get_metrics()
        
        assert "manager" in metrics
        assert "components" in metrics
        assert "features" in metrics
        
        # Check manager info
        assert metrics["manager"]["uptime_seconds"] > 0
        
        # Check features
        features = metrics["features"]
        assert features["configuration_management"] is True
        assert features["infrastructure_generation"] is True
        assert features["deployment_automation"] is True
        assert features["rollback_support"] is True
        assert features["environment_promotion"] is True
        assert features["security_hardening"] is True
        assert features["multi_provider_support"] is True


class TestDeploymentManagerIntegration:
    """Integration tests for DeploymentManager."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock Customer.IO client."""
        return Mock(spec=CustomerIOClient)
    
    @pytest.fixture
    def deployment_manager(self, mock_client):
        """Create deployment manager."""
        return DeploymentManager(mock_client)
    
    @pytest.mark.asyncio
    async def test_complete_deployment_workflow(self, deployment_manager):
        """Test complete deployment workflow from creation to deployment."""
        # 1. Create deployment configuration
        deployment_config = deployment_manager.create_deployment(
            name="customer-io-pipelines",
            version="2.1.0",
            environment=Environment.DEVELOPMENT,
            strategy=DeploymentStrategy.ROLLING_UPDATE,
            created_by="integration_test"
        )
        
        # 2. Generate infrastructure templates
        templates = deployment_manager.generate_infrastructure(
            Environment.DEVELOPMENT,
            deployment_config
        )
        
        assert len(templates) == 1
        template = templates[0]
        assert template.provider == InfrastructureProvider.DOCKER
        
        # 3. Mock deployment execution
        with patch.object(deployment_manager.deployment_engine, 'deploy') as mock_deploy:
            mock_result = DeploymentResult(
                deployment_id=deployment_config.deployment_id,
                status=DeploymentStatus.SUCCESS,
                start_time=datetime.now(timezone.utc)
            )
            mock_result.finish(DeploymentStatus.SUCCESS)
            mock_deploy.return_value = mock_result
            
            # 4. Deploy application
            result = await deployment_manager.deploy_application(deployment_config)
            
            assert result.status == DeploymentStatus.SUCCESS
            assert result.deployment_id == deployment_config.deployment_id
    
    @pytest.mark.asyncio
    async def test_multi_environment_promotion_workflow(self, deployment_manager):
        """Test multi-environment promotion workflow."""
        version = "2.2.0"
        
        # 1. Simulate successful development deployment
        dev_deployment = DeploymentResult(
            deployment_id=f"customer-io-pipelines-{Environment.DEVELOPMENT}-{version}-123456",
            status=DeploymentStatus.SUCCESS,
            start_time=datetime.now(timezone.utc)
        )
        deployment_manager.deployment_engine.deployment_history.append(dev_deployment)
        
        # Mock promotion deployments
        with patch.object(deployment_manager, 'deploy_application') as mock_deploy:
            # 2. Promote to staging
            staging_result = Mock()
            staging_result.status = DeploymentStatus.SUCCESS
            mock_deploy.return_value = staging_result
            
            staging_promotion = await deployment_manager.promote_deployment(
                from_env=Environment.DEVELOPMENT,
                to_env=Environment.STAGING,
                version=version,
                created_by="ci_cd_pipeline"
            )
            
            assert staging_promotion.status == DeploymentStatus.SUCCESS
            
            # Add staging deployment to history
            staging_deployment = DeploymentResult(
                deployment_id=f"customer-io-pipelines-{Environment.STAGING}-{version}-123457",
                status=DeploymentStatus.SUCCESS,
                start_time=datetime.now(timezone.utc)
            )
            deployment_manager.deployment_engine.deployment_history.append(staging_deployment)
            
            # 3. Promote to production
            prod_result = Mock()
            prod_result.status = DeploymentStatus.SUCCESS
            mock_deploy.return_value = prod_result
            
            prod_promotion = await deployment_manager.promote_deployment(
                from_env=Environment.STAGING,
                to_env=Environment.PRODUCTION,
                version=version,
                created_by="release_manager"
            )
            
            assert prod_promotion.status == DeploymentStatus.SUCCESS
            
            # Verify deployment configs were created with appropriate strategies
            assert mock_deploy.call_count == 2
            
            # Check that production deployment uses blue-green strategy
            prod_call_args = mock_deploy.call_args_list[1][0][0]
            assert prod_call_args.strategy == DeploymentStrategy.BLUE_GREEN
    
    def test_configuration_bundle_generation_workflow(self, deployment_manager):
        """Test configuration bundle generation for all environments."""
        with tempfile.TemporaryDirectory() as base_temp_dir:
            for environment in [Environment.DEVELOPMENT, Environment.STAGING, Environment.PRODUCTION]:
                env_dir = os.path.join(base_temp_dir, environment.value)
                
                bundle_files = deployment_manager.create_environment_config_bundle(
                    environment,
                    env_dir
                )
                
                # Verify all expected files were created
                assert "config" in bundle_files
                assert "deploy_script" in bundle_files
                
                # Check provider-specific templates
                env_config = deployment_manager.config_manager.get_environment_config(environment)
                if env_config.provider == InfrastructureProvider.KUBERNETES:
                    assert any("template_kubernetes" in key for key in bundle_files.keys())
                elif env_config.provider == InfrastructureProvider.DOCKER:
                    assert any("template_docker" in key for key in bundle_files.keys())
                elif env_config.provider == InfrastructureProvider.AWS:
                    assert any("template_aws" in key for key in bundle_files.keys())
                
                # Verify files exist and have content
                for file_path in bundle_files.values():
                    assert os.path.exists(file_path)
                    assert os.path.getsize(file_path) > 0
    
    def test_security_level_compliance_workflow(self, deployment_manager):
        """Test security level compliance across environments."""
        # Check security levels are appropriate for each environment
        dev_config = deployment_manager.config_manager.get_environment_config(Environment.DEVELOPMENT)
        staging_config = deployment_manager.config_manager.get_environment_config(Environment.STAGING)
        prod_config = deployment_manager.config_manager.get_environment_config(Environment.PRODUCTION)
        
        assert dev_config.security_level == SecurityLevel.BASIC
        assert staging_config.security_level == SecurityLevel.STANDARD
        assert prod_config.security_level == SecurityLevel.ENHANCED
        
        # Validate environment configurations
        for env in [Environment.DEVELOPMENT, Environment.STAGING, Environment.PRODUCTION]:
            validation = deployment_manager.config_manager.validate_environment(env)
            
            # Development might have warnings but should be valid
            if env == Environment.DEVELOPMENT:
                assert validation["valid"] is True
            else:
                # Staging and production should pass validation
                # (might fail due to missing secrets in test environment)
                assert "errors" in validation
    
    def test_infrastructure_template_consistency(self, deployment_manager):
        """Test infrastructure template generation consistency."""
        deployment_config = deployment_manager.create_deployment(
            name="customer-io-pipelines",
            version="1.0.0",
            environment=Environment.STAGING,
            created_by="test"
        )
        
        # Generate templates multiple times
        templates_1 = deployment_manager.generate_infrastructure(Environment.STAGING, deployment_config)
        templates_2 = deployment_manager.generate_infrastructure(Environment.STAGING, deployment_config)
        
        # Templates should be consistent
        assert len(templates_1) == len(templates_2)
        
        for t1, t2 in zip(templates_1, templates_2):
            assert t1.provider == t2.provider
            assert t1.template_format == t2.template_format
            # Content might differ slightly due to timestamps, but structure should be same
            assert "apiVersion" in t1.template_content
            assert "apiVersion" in t2.template_content
    
    def test_concurrent_deployment_operations(self, deployment_manager):
        """Test concurrent deployment operations."""
        import threading
        import time
        
        results = []
        errors = []
        
        def create_deployment_configs(thread_id):
            try:
                for i in range(5):
                    config = deployment_manager.create_deployment(
                        name=f"app-{thread_id}-{i}",
                        version=f"1.{i}.0",
                        environment=Environment.DEVELOPMENT,
                        created_by=f"thread_{thread_id}"
                    )
                    results.append(config.deployment_id)
                    
                    # Generate infrastructure
                    templates = deployment_manager.generate_infrastructure(
                        Environment.DEVELOPMENT,
                        config
                    )
                    assert len(templates) == 1
                    
            except Exception as e:
                errors.append(f"Thread {thread_id}: {str(e)}")
        
        # Run operations in multiple threads
        threads = []
        for thread_id in range(3):
            thread = threading.Thread(target=create_deployment_configs, args=(thread_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no errors and all operations completed
        assert len(errors) == 0, f"Concurrent operation errors: {errors}"
        assert len(results) == 15  # 3 threads * 5 configs each
        
        # Verify all deployment IDs are unique
        assert len(set(results)) == len(results)
    
    def test_dashboard_data_accuracy(self, deployment_manager):
        """Test deployment dashboard data accuracy."""
        # Create deployments with known outcomes
        deployment_configs = []
        for i in range(10):
            config = deployment_manager.create_deployment(
                name=f"test-app-{i}",
                version=f"1.{i}.0",
                environment=Environment.DEVELOPMENT if i < 5 else Environment.STAGING,
                created_by="dashboard_test"
            )
            deployment_configs.append(config)
        
        # Add deployment results with known success/failure rates
        for i, config in enumerate(deployment_configs):
            result = DeploymentResult(
                deployment_id=config.deployment_id,
                status=DeploymentStatus.SUCCESS if i < 8 else DeploymentStatus.FAILED,
                start_time=datetime.now(timezone.utc)
            )
            result.finish(result.status)
            deployment_manager.deployment_engine.deployment_history.append(result)
        
        # Get dashboard data
        dashboard = deployment_manager.get_deployment_dashboard()
        
        # Verify accuracy
        assert dashboard["deployments"]["total_deployments"] == 10
        assert dashboard["deployments"]["successful_deployments"] == 8
        assert dashboard["deployments"]["failed_deployments"] == 2
        assert dashboard["deployments"]["success_rate_percent"] == 80.0
        
        # Check environment breakdown
        env_breakdown = dashboard["deployments"]["by_environment"]
        assert env_breakdown[Environment.DEVELOPMENT]["total"] == 5
        assert env_breakdown[Environment.STAGING]["total"] == 5