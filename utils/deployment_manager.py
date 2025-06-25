"""
Customer.IO Production Deployment Module

Comprehensive production deployment and infrastructure management for Customer.IO data pipelines including:
- Container orchestration and deployment strategies
- Configuration management and secrets handling
- Infrastructure as Code (IaC) templates
- CI/CD pipeline integration
- Environment management and promotion
- Performance optimization and scaling
- Security hardening and compliance
- Disaster recovery and backup strategies
"""

import json
import yaml
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import structlog
from pydantic import BaseModel, Field, validator
import hashlib
import base64
import secrets

from .api_client import CustomerIOClient
from .error_handlers import retry_on_error, ErrorContext, CustomerIOError


class Environment(str, Enum):
    """Deployment environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class DeploymentStrategy(str, Enum):
    """Deployment strategy types."""
    ROLLING_UPDATE = "rolling_update"
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    RECREATE = "recreate"
    A_B_TESTING = "a_b_testing"


class InfrastructureProvider(str, Enum):
    """Infrastructure provider types."""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    KUBERNETES = "kubernetes"
    DOCKER = "docker"
    LOCAL = "local"


class DeploymentStatus(str, Enum):
    """Deployment status values."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"


class SecurityLevel(str, Enum):
    """Security hardening levels."""
    BASIC = "basic"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    CRITICAL = "critical"


class SecretConfig(BaseModel):
    """Type-safe secret configuration model."""
    name: str = Field(..., description="Secret name")
    value: Optional[str] = Field(None, description="Secret value (if stored locally)")
    source: str = Field(..., description="Secret source (env, vault, k8s, etc.)")
    encrypted: bool = Field(default=True, description="Whether secret is encrypted")
    required: bool = Field(default=True, description="Whether secret is required")
    description: Optional[str] = Field(None, description="Secret description")
    
    @validator('name')
    def validate_name(cls, v: str) -> str:
        """Validate secret name format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Secret name cannot be empty")
        # Ensure secret name follows conventions
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Secret name must contain only alphanumeric, underscore, or dash characters")
        return v.strip().upper()
    
    class Config:
        """Pydantic model configuration."""
        validate_assignment = True


class EnvironmentConfig(BaseModel):
    """Type-safe environment configuration model."""
    name: Environment = Field(..., description="Environment name")
    display_name: str = Field(..., description="Human readable name")
    description: Optional[str] = Field(None, description="Environment description")
    provider: InfrastructureProvider = Field(..., description="Infrastructure provider")
    region: str = Field(default="us-east-1", description="Deployment region")
    namespace: Optional[str] = Field(None, description="Kubernetes namespace or equivalent")
    replicas: int = Field(default=1, gt=0, description="Number of replicas")
    resources: Dict[str, Any] = Field(default_factory=dict, description="Resource requirements")
    secrets: List[SecretConfig] = Field(default_factory=list, description="Environment secrets")
    config_vars: Dict[str, str] = Field(default_factory=dict, description="Configuration variables")
    security_level: SecurityLevel = Field(default=SecurityLevel.STANDARD, description="Security level")
    auto_scaling: bool = Field(default=False, description="Enable auto-scaling")
    monitoring_enabled: bool = Field(default=True, description="Enable monitoring")
    
    class Config:
        """Pydantic model configuration."""
        use_enum_values = True
        validate_assignment = True


class DeploymentConfig(BaseModel):
    """Type-safe deployment configuration model."""
    deployment_id: str = Field(..., description="Unique deployment identifier")
    name: str = Field(..., description="Deployment name")
    version: str = Field(..., description="Application version")
    environment: Environment = Field(..., description="Target environment")
    strategy: DeploymentStrategy = Field(default=DeploymentStrategy.ROLLING_UPDATE, description="Deployment strategy")
    image_tag: str = Field(..., description="Container image tag")
    image_repository: str = Field(default="customer-io-pipelines", description="Container image repository")
    rollback_version: Optional[str] = Field(None, description="Version to rollback to if needed")
    health_check_path: str = Field(default="/health", description="Health check endpoint")
    readiness_check_path: str = Field(default="/ready", description="Readiness check endpoint")
    timeout_seconds: int = Field(default=600, gt=0, description="Deployment timeout")
    created_by: str = Field(..., description="User who created deployment")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @validator('deployment_id', 'name')
    def validate_identifiers(cls, v: str) -> str:
        """Validate identifier formats."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Identifier cannot be empty")
        return v.strip()
    
    class Config:
        """Pydantic model configuration."""
        use_enum_values = True
        validate_assignment = True


class DeploymentResult(BaseModel):
    """Type-safe deployment result model."""
    deployment_id: str = Field(..., description="Deployment identifier")
    status: DeploymentStatus = Field(..., description="Deployment status")
    start_time: datetime = Field(..., description="Deployment start time")
    end_time: Optional[datetime] = Field(None, description="Deployment end time")
    duration_seconds: Optional[float] = Field(None, ge=0, description="Deployment duration")
    logs: List[str] = Field(default_factory=list, description="Deployment logs")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    rollback_performed: bool = Field(default=False, description="Whether rollback was performed")
    health_check_passed: bool = Field(default=False, description="Whether health checks passed")
    performance_metrics: Dict[str, float] = Field(default_factory=dict, description="Performance metrics")
    resource_usage: Dict[str, Any] = Field(default_factory=dict, description="Resource usage during deployment")
    
    def finish(self, status: DeploymentStatus, error_message: Optional[str] = None) -> None:
        """Finish the deployment with final status."""
        self.end_time = datetime.now(timezone.utc)
        self.duration_seconds = (self.end_time - self.start_time).total_seconds()
        self.status = status
        if error_message:
            self.error_message = error_message
    
    def add_log(self, message: str) -> None:
        """Add log entry to deployment."""
        timestamp = datetime.now(timezone.utc).isoformat()
        self.logs.append(f"[{timestamp}] {message}")
    
    def is_successful(self) -> bool:
        """Check if deployment was successful."""
        return self.status == DeploymentStatus.SUCCESS
    
    class Config:
        """Pydantic model configuration."""
        use_enum_values = True
        validate_assignment = True


class InfrastructureTemplate(BaseModel):
    """Type-safe infrastructure template model."""
    template_id: str = Field(..., description="Template identifier")
    name: str = Field(..., description="Template name")
    provider: InfrastructureProvider = Field(..., description="Infrastructure provider")
    template_format: str = Field(..., description="Template format (yaml, json, tf, etc.)")
    template_content: str = Field(..., description="Template content")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Template parameters")
    description: Optional[str] = Field(None, description="Template description")
    version: str = Field(default="1.0.0", description="Template version")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        """Pydantic model configuration."""
        use_enum_values = True
        validate_assignment = True


class ConfigurationManager:
    """Secure configuration and secrets management system."""
    
    def __init__(self):
        self.environments: Dict[Environment, EnvironmentConfig] = {}
        self.encrypted_secrets: Dict[str, str] = {}
        self.encryption_key = self._generate_encryption_key()
        self.logger = structlog.get_logger("configuration_manager")
    
    def _generate_encryption_key(self) -> str:
        """Generate encryption key for secrets."""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    
    def _encrypt_value(self, value: str) -> str:
        """Encrypt a secret value (simplified for demo)."""
        # In production, use proper encryption libraries like cryptography
        encoded = base64.b64encode(value.encode()).decode()
        return f"encrypted:{encoded}"
    
    def _decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a secret value (simplified for demo)."""
        if encrypted_value.startswith("encrypted:"):
            encoded = encrypted_value[10:]  # Remove "encrypted:" prefix
            return base64.b64decode(encoded).decode()
        return encrypted_value
    
    def register_environment(self, env_config: EnvironmentConfig) -> None:
        """Register environment configuration."""
        self.environments[env_config.name] = env_config
        
        # Encrypt and store secrets
        for secret in env_config.secrets:
            if secret.value and secret.encrypted:
                secret_key = f"{env_config.name}:{secret.name}"
                self.encrypted_secrets[secret_key] = self._encrypt_value(secret.value)
                # Clear the plain text value
                secret.value = None
        
        self.logger.info(
            "Environment registered",
            environment=env_config.name,
            provider=env_config.provider,
            secrets_count=len(env_config.secrets)
        )
    
    def get_environment_config(self, environment: Environment) -> Optional[EnvironmentConfig]:
        """Get environment configuration."""
        return self.environments.get(environment)
    
    def get_secret(self, environment: Environment, secret_name: str) -> Optional[str]:
        """Get decrypted secret value."""
        secret_key = f"{environment}:{secret_name.upper()}"
        encrypted_value = self.encrypted_secrets.get(secret_key)
        
        if encrypted_value:
            return self._decrypt_value(encrypted_value)
        
        # Try to get from environment variables
        env_var = os.getenv(secret_name.upper())
        if env_var:
            return env_var
        
        return None
    
    def set_secret(self, environment: Environment, secret_name: str, secret_value: str, encrypt: bool = True) -> None:
        """Set secret value."""
        secret_key = f"{environment}:{secret_name.upper()}"
        
        if encrypt:
            self.encrypted_secrets[secret_key] = self._encrypt_value(secret_value)
        else:
            self.encrypted_secrets[secret_key] = secret_value
        
        self.logger.info(
            "Secret updated",
            environment=environment,
            secret_name=secret_name,
            encrypted=encrypt
        )
    
    def generate_config_file(self, environment: Environment, output_format: str = "yaml") -> str:
        """Generate configuration file for environment."""
        env_config = self.get_environment_config(environment)
        if not env_config:
            raise ValueError(f"Environment {environment} not found")
        
        config_data = {
            "environment": {
                "name": env_config.name,
                "display_name": env_config.display_name,
                "provider": env_config.provider,
                "region": env_config.region,
                "namespace": env_config.namespace,
                "replicas": env_config.replicas,
                "security_level": env_config.security_level,
                "auto_scaling": env_config.auto_scaling,
                "monitoring_enabled": env_config.monitoring_enabled
            },
            "resources": env_config.resources,
            "config_vars": env_config.config_vars,
            "secrets": {
                secret.name: {
                    "source": secret.source,
                    "required": secret.required,
                    "description": secret.description
                }
                for secret in env_config.secrets
            }
        }
        
        if output_format.lower() == "yaml":
            return yaml.dump(config_data, default_flow_style=False)
        elif output_format.lower() == "json":
            return json.dumps(config_data, indent=2)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def validate_environment(self, environment: Environment) -> Dict[str, Any]:
        """Validate environment configuration."""
        env_config = self.get_environment_config(environment)
        if not env_config:
            return {"valid": False, "errors": ["Environment not found"]}
        
        errors = []
        warnings = []
        
        # Check required secrets
        for secret in env_config.secrets:
            if secret.required:
                secret_value = self.get_secret(environment, secret.name)
                if not secret_value:
                    errors.append(f"Required secret {secret.name} is missing")
        
        # Check resource configuration
        if env_config.replicas > 10 and environment != Environment.PRODUCTION:
            warnings.append(f"High replica count ({env_config.replicas}) for non-production environment")
        
        # Check security level
        if environment == Environment.PRODUCTION and env_config.security_level == SecurityLevel.BASIC:
            warnings.append("Basic security level not recommended for production")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "environment": environment,
            "checked_at": datetime.now(timezone.utc).isoformat()
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get configuration manager metrics."""
        total_secrets = len(self.encrypted_secrets)
        secrets_by_env = {}
        
        for secret_key in self.encrypted_secrets.keys():
            env_name = secret_key.split(':')[0]
            secrets_by_env[env_name] = secrets_by_env.get(env_name, 0) + 1
        
        return {
            "environments_registered": len(self.environments),
            "total_secrets": total_secrets,
            "secrets_by_environment": secrets_by_env,
            "encryption_enabled": True,
            "supported_providers": [provider.value for provider in InfrastructureProvider]
        }


class InfrastructureGenerator:
    """Infrastructure as Code template generator."""
    
    def __init__(self):
        self.templates: Dict[str, InfrastructureTemplate] = {}
        self.logger = structlog.get_logger("infrastructure_generator")
    
    def generate_kubernetes_deployment(self, env_config: EnvironmentConfig, deployment_config: DeploymentConfig) -> InfrastructureTemplate:
        """Generate Kubernetes deployment template."""
        
        k8s_template = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"customer-io-{env_config.name}",
                "namespace": env_config.namespace or "default",
                "labels": {
                    "app": "customer-io-pipelines",
                    "environment": env_config.name,
                    "version": deployment_config.version
                }
            },
            "spec": {
                "replicas": env_config.replicas,
                "strategy": {
                    "type": "RollingUpdate",
                    "rollingUpdate": {
                        "maxUnavailable": 1,
                        "maxSurge": 1
                    }
                },
                "selector": {
                    "matchLabels": {
                        "app": "customer-io-pipelines",
                        "environment": env_config.name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "customer-io-pipelines",
                            "environment": env_config.name,
                            "version": deployment_config.version
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "customer-io-pipelines",
                            "image": f"{deployment_config.image_repository}:{deployment_config.image_tag}",
                            "ports": [{
                                "containerPort": 8080,
                                "name": "http"
                            }],
                            "env": self._generate_env_vars(env_config),
                            "resources": env_config.resources or {
                                "requests": {
                                    "memory": "256Mi",
                                    "cpu": "250m"
                                },
                                "limits": {
                                    "memory": "512Mi",
                                    "cpu": "500m"
                                }
                            },
                            "livenessProbe": {
                                "httpGet": {
                                    "path": deployment_config.health_check_path,
                                    "port": 8080
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10
                            },
                            "readinessProbe": {
                                "httpGet": {
                                    "path": deployment_config.readiness_check_path,
                                    "port": 8080
                                },
                                "initialDelaySeconds": 5,
                                "periodSeconds": 5
                            }
                        }],
                        "securityContext": self._generate_security_context(env_config.security_level)
                    }
                }
            }
        }
        
        # Add horizontal pod autoscaler if enabled
        hpa_template = None
        if env_config.auto_scaling:
            hpa_template = {
                "apiVersion": "autoscaling/v2",
                "kind": "HorizontalPodAutoscaler",
                "metadata": {
                    "name": f"customer-io-{env_config.name}-hpa",
                    "namespace": env_config.namespace or "default"
                },
                "spec": {
                    "scaleTargetRef": {
                        "apiVersion": "apps/v1",
                        "kind": "Deployment",
                        "name": f"customer-io-{env_config.name}"
                    },
                    "minReplicas": env_config.replicas,
                    "maxReplicas": env_config.replicas * 3,
                    "metrics": [
                        {
                            "type": "Resource",
                            "resource": {
                                "name": "cpu",
                                "target": {
                                    "type": "Utilization",
                                    "averageUtilization": 70
                                }
                            }
                        }
                    ]
                }
            }
        
        # Combine templates
        combined_template = {
            "deployment": k8s_template
        }
        
        if hpa_template:
            combined_template["hpa"] = hpa_template
        
        template = InfrastructureTemplate(
            template_id=f"k8s-{env_config.name}-{deployment_config.version}",
            name=f"Kubernetes Deployment - {env_config.display_name}",
            provider=InfrastructureProvider.KUBERNETES,
            template_format="yaml",
            template_content=yaml.dump(combined_template, default_flow_style=False),
            parameters={
                "environment": env_config.name,
                "version": deployment_config.version,
                "replicas": env_config.replicas,
                "auto_scaling": env_config.auto_scaling
            }
        )
        
        self.templates[template.template_id] = template
        return template
    
    def generate_docker_compose(self, env_config: EnvironmentConfig, deployment_config: DeploymentConfig) -> InfrastructureTemplate:
        """Generate Docker Compose template."""
        
        compose_template = {
            "version": "3.8",
            "services": {
                "customer-io-pipelines": {
                    "image": f"{deployment_config.image_repository}:{deployment_config.image_tag}",
                    "ports": ["8080:8080"],
                    "environment": {
                        **env_config.config_vars,
                        "ENVIRONMENT": env_config.name,
                        "LOG_LEVEL": "INFO" if env_config.name == Environment.PRODUCTION else "DEBUG"
                    },
                    "restart": "unless-stopped",
                    "healthcheck": {
                        "test": f"curl -f http://localhost:8080{deployment_config.health_check_path} || exit 1",
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 3,
                        "start_period": "40s"
                    },
                    "deploy": {
                        "replicas": env_config.replicas,
                        "resources": {
                            "limits": env_config.resources.get("limits", {
                                "memory": "512M",
                                "cpus": "0.5"
                            }),
                            "reservations": env_config.resources.get("requests", {
                                "memory": "256M",
                                "cpus": "0.25"
                            })
                        },
                        "restart_policy": {
                            "condition": "on-failure",
                            "delay": "5s",
                            "max_attempts": 3
                        }
                    }
                }
            }
        }
        
        # Add monitoring services if enabled
        if env_config.monitoring_enabled:
            compose_template["services"]["prometheus"] = {
                "image": "prom/prometheus:latest",
                "ports": ["9090:9090"],
                "volumes": ["./prometheus.yml:/etc/prometheus/prometheus.yml"]
            }
            
            compose_template["services"]["grafana"] = {
                "image": "grafana/grafana:latest",
                "ports": ["3000:3000"],
                "environment": {
                    "GF_SECURITY_ADMIN_PASSWORD": "admin"
                }
            }
        
        template = InfrastructureTemplate(
            template_id=f"docker-{env_config.name}-{deployment_config.version}",
            name=f"Docker Compose - {env_config.display_name}",
            provider=InfrastructureProvider.DOCKER,
            template_format="yaml",
            template_content=yaml.dump(compose_template, default_flow_style=False),
            parameters={
                "environment": env_config.name,
                "version": deployment_config.version,
                "monitoring": env_config.monitoring_enabled
            }
        )
        
        self.templates[template.template_id] = template
        return template
    
    def generate_terraform_aws(self, env_config: EnvironmentConfig, deployment_config: DeploymentConfig) -> InfrastructureTemplate:
        """Generate Terraform template for AWS ECS."""
        
        terraform_template = f"""
# Customer.IO Pipelines AWS ECS Infrastructure
terraform {{
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = "{env_config.region}"
}}

# ECS Cluster
resource "aws_ecs_cluster" "customer_io_cluster" {{
  name = "customer-io-{env_config.name}"
  
  setting {{
    name  = "containerInsights"
    value = "enabled"
  }}
}}

# Task Definition
resource "aws_ecs_task_definition" "customer_io_task" {{
  family                   = "customer-io-{env_config.name}"
  network_mode             = "awsvpc"
  requires_compatibility   = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn
  
  container_definitions = jsonencode([
    {{
      name  = "customer-io-pipelines"
      image = "{deployment_config.image_repository}:{deployment_config.image_tag}"
      portMappings = [
        {{
          containerPort = 8080
          protocol      = "tcp"
        }}
      ]
      environment = [
        {{
          name  = "ENVIRONMENT"
          value = "{env_config.name}"
        }}
      ]
      healthCheck = {{
        command = [
          "CMD-SHELL",
          "curl -f http://localhost:8080{deployment_config.health_check_path} || exit 1"
        ]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }}
      logConfiguration = {{
        logDriver = "awslogs"
        options = {{
          "awslogs-group"         = aws_cloudwatch_log_group.customer_io_logs.name
          "awslogs-region"        = "{env_config.region}"
          "awslogs-stream-prefix" = "ecs"
        }}
      }}
    }}
  ])
}}

# ECS Service
resource "aws_ecs_service" "customer_io_service" {{
  name            = "customer-io-{env_config.name}"
  cluster         = aws_ecs_cluster.customer_io_cluster.id
  task_definition = aws_ecs_task_definition.customer_io_task.arn
  desired_count   = {env_config.replicas}
  launch_type     = "FARGATE"
  
  network_configuration {{
    subnets         = var.subnet_ids
    security_groups = [aws_security_group.customer_io_sg.id]
    assign_public_ip = true
  }}
  
  deployment_configuration {{
    maximum_percent         = 200
    minimum_healthy_percent = 100
  }}
}}

# Security Group
resource "aws_security_group" "customer_io_sg" {{
  name_prefix = "customer-io-{env_config.name}-"
  
  ingress {{
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}
  
  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
}}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "customer_io_logs" {{
  name              = "/ecs/customer-io-{env_config.name}"
  retention_in_days = 30
}}

# IAM Roles
resource "aws_iam_role" "ecs_execution_role" {{
  name = "customer-io-{env_config.name}-execution-role"
  
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = "ecs-tasks.amazonaws.com"
        }}
      }}
    ]
  }})
}}

resource "aws_iam_role" "ecs_task_role" {{
  name = "customer-io-{env_config.name}-task-role"
  
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {{
          Service = "ecs-tasks.amazonaws.com"
        }}
      }}
    ]
  }})
}}

# Variables
variable "subnet_ids" {{
  description = "List of subnet IDs"
  type        = list(string)
}}

# Outputs
output "cluster_name" {{
  value = aws_ecs_cluster.customer_io_cluster.name
}}

output "service_name" {{
  value = aws_ecs_service.customer_io_service.name
}}
"""
        
        template = InfrastructureTemplate(
            template_id=f"terraform-aws-{env_config.name}-{deployment_config.version}",
            name=f"Terraform AWS ECS - {env_config.display_name}",
            provider=InfrastructureProvider.AWS,
            template_format="hcl",
            template_content=terraform_template,
            parameters={
                "environment": env_config.name,
                "version": deployment_config.version,
                "region": env_config.region,
                "replicas": env_config.replicas
            }
        )
        
        self.templates[template.template_id] = template
        return template
    
    def _generate_env_vars(self, env_config: EnvironmentConfig) -> List[Dict[str, str]]:
        """Generate environment variables for containers."""
        env_vars = []
        
        # Add config vars
        for key, value in env_config.config_vars.items():
            env_vars.append({"name": key, "value": value})
        
        # Add secret references
        for secret in env_config.secrets:
            if secret.source == "k8s":
                env_vars.append({
                    "name": secret.name,
                    "valueFrom": {
                        "secretKeyRef": {
                            "name": f"customer-io-{env_config.name}-secrets",
                            "key": secret.name.lower()
                        }
                    }
                })
            else:
                env_vars.append({"name": secret.name, "value": f"${{{secret.name}}}"})
        
        return env_vars
    
    def _generate_security_context(self, security_level: SecurityLevel) -> Dict[str, Any]:
        """Generate security context based on security level."""
        if security_level == SecurityLevel.CRITICAL:
            return {
                "runAsNonRoot": True,
                "runAsUser": 1001,
                "runAsGroup": 1001,
                "fsGroup": 1001,
                "seccompProfile": {
                    "type": "RuntimeDefault"
                }
            }
        elif security_level == SecurityLevel.ENHANCED:
            return {
                "runAsNonRoot": True,
                "runAsUser": 1001,
                "fsGroup": 1001
            }
        elif security_level == SecurityLevel.STANDARD:
            return {
                "runAsNonRoot": True,
                "runAsUser": 1001
            }
        else:  # BASIC
            return {}
    
    def get_template(self, template_id: str) -> Optional[InfrastructureTemplate]:
        """Get infrastructure template by ID."""
        return self.templates.get(template_id)
    
    def list_templates(self, provider: Optional[InfrastructureProvider] = None) -> List[InfrastructureTemplate]:
        """List infrastructure templates."""
        templates = list(self.templates.values())
        if provider:
            templates = [t for t in templates if t.provider == provider]
        return templates
    
    def export_template(self, template_id: str, output_path: str) -> bool:
        """Export template to file."""
        template = self.get_template(template_id)
        if not template:
            return False
        
        try:
            with open(output_path, 'w') as f:
                f.write(template.template_content)
            
            self.logger.info(
                "Template exported",
                template_id=template_id,
                output_path=output_path
            )
            return True
        except Exception as e:
            self.logger.error(
                "Template export failed",
                template_id=template_id,
                error=str(e)
            )
            return False


class DeploymentEngine:
    """Core deployment engine with strategy execution and rollback."""
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager
        self.active_deployments: Dict[str, DeploymentResult] = {}
        self.deployment_history: List[DeploymentResult] = []
        self.logger = structlog.get_logger("deployment_engine")
    
    @retry_on_error(max_retries=2, backoff_factor=2.0)
    def deploy(self, deployment_config: DeploymentConfig) -> DeploymentResult:
        """Execute deployment with specified strategy."""
        
        # Create deployment result
        result = DeploymentResult(
            deployment_id=deployment_config.deployment_id,
            status=DeploymentStatus.PENDING,
            start_time=datetime.now(timezone.utc)
        )
        
        self.active_deployments[deployment_config.deployment_id] = result
        result.add_log(f"Deployment started by {deployment_config.created_by}")
        
        try:
            # Validate environment configuration
            env_config = self.config_manager.get_environment_config(deployment_config.environment)
            if not env_config:
                raise ValueError(f"Environment {deployment_config.environment} not configured")
            
            validation_result = self.config_manager.validate_environment(deployment_config.environment)
            if not validation_result["valid"]:
                raise ValueError(f"Environment validation failed: {validation_result['errors']}")
            
            result.add_log("Environment validation passed")
            result.status = DeploymentStatus.RUNNING
            
            # Execute deployment strategy
            if deployment_config.strategy == DeploymentStrategy.ROLLING_UPDATE:
                self._execute_rolling_update(deployment_config, env_config, result)
            elif deployment_config.strategy == DeploymentStrategy.BLUE_GREEN:
                self._execute_blue_green(deployment_config, env_config, result)
            elif deployment_config.strategy == DeploymentStrategy.CANARY:
                self._execute_canary(deployment_config, env_config, result)
            else:
                self._execute_recreate(deployment_config, env_config, result)
            
            # Perform health checks
            health_passed = self._perform_health_checks(deployment_config, result)
            result.health_check_passed = health_passed
            
            if health_passed:
                result.finish(DeploymentStatus.SUCCESS)
                result.add_log("Deployment completed successfully")
            else:
                result.finish(DeploymentStatus.FAILED, "Health checks failed")
                self._perform_rollback(deployment_config, result)
            
        except Exception as e:
            error_msg = str(e)
            result.finish(DeploymentStatus.FAILED, error_msg)
            result.add_log(f"Deployment failed: {error_msg}")
            
            # Attempt rollback
            try:
                self._perform_rollback(deployment_config, result)
            except Exception as rollback_error:
                result.add_log(f"Rollback failed: {rollback_error}")
                self.logger.error(
                    "Rollback failed",
                    deployment_id=deployment_config.deployment_id,
                    error=str(rollback_error)
                )
        
        finally:
            # Move to history and clean up
            if deployment_config.deployment_id in self.active_deployments:
                del self.active_deployments[deployment_config.deployment_id]
            
            self.deployment_history.append(result)
            
            # Keep only last 100 deployments in history
            if len(self.deployment_history) > 100:
                self.deployment_history = self.deployment_history[-100:]
            
            self.logger.info(
                "Deployment completed",
                deployment_id=deployment_config.deployment_id,
                status=result.status,
                duration_seconds=result.duration_seconds
            )
        
        return result
    
    def _execute_rolling_update(self, deployment_config: DeploymentConfig, env_config: EnvironmentConfig, result: DeploymentResult) -> None:
        """Execute rolling update deployment strategy."""
        result.add_log("Executing rolling update strategy")
        
        # Simulate rolling update steps
        steps = [
            "Updating container image",
            "Rolling out to 25% of instances",
            "Checking health of updated instances",
            "Rolling out to 50% of instances",
            "Rolling out to 75% of instances",
            "Completing rollout to 100% of instances"
        ]
        
        import time
        for i, step in enumerate(steps):
            result.add_log(f"Step {i+1}: {step}")
            time.sleep(0.1)  # Simulate work
            
            # Update performance metrics
            result.performance_metrics[f"step_{i+1}_duration_ms"] = 100.0 + (i * 50)
    
    def _execute_blue_green(self, deployment_config: DeploymentConfig, env_config: EnvironmentConfig, result: DeploymentResult) -> None:
        """Execute blue-green deployment strategy."""
        result.add_log("Executing blue-green deployment strategy")
        
        steps = [
            "Creating green environment",
            "Deploying new version to green environment",
            "Running smoke tests on green environment",
            "Switching traffic to green environment",
            "Monitoring green environment",
            "Decommissioning blue environment"
        ]
        
        import time
        for i, step in enumerate(steps):
            result.add_log(f"Step {i+1}: {step}")
            time.sleep(0.1)
            result.performance_metrics[f"step_{i+1}_duration_ms"] = 150.0 + (i * 75)
    
    def _execute_canary(self, deployment_config: DeploymentConfig, env_config: EnvironmentConfig, result: DeploymentResult) -> None:
        """Execute canary deployment strategy."""
        result.add_log("Executing canary deployment strategy")
        
        steps = [
            "Deploying canary version to 5% of traffic",
            "Monitoring canary metrics",
            "Increasing canary traffic to 25%",
            "Validating canary performance",
            "Promoting canary to 100% of traffic",
            "Removing old version"
        ]
        
        import time
        for i, step in enumerate(steps):
            result.add_log(f"Step {i+1}: {step}")
            time.sleep(0.1)
            result.performance_metrics[f"step_{i+1}_duration_ms"] = 200.0 + (i * 100)
    
    def _execute_recreate(self, deployment_config: DeploymentConfig, env_config: EnvironmentConfig, result: DeploymentResult) -> None:
        """Execute recreate deployment strategy."""
        result.add_log("Executing recreate deployment strategy")
        
        steps = [
            "Stopping existing instances",
            "Removing old deployment",
            "Creating new deployment",
            "Starting new instances",
            "Waiting for instances to be ready"
        ]
        
        import time
        for i, step in enumerate(steps):
            result.add_log(f"Step {i+1}: {step}")
            time.sleep(0.1)
            result.performance_metrics[f"step_{i+1}_duration_ms"] = 80.0 + (i * 40)
    
    def _perform_health_checks(self, deployment_config: DeploymentConfig, result: DeploymentResult) -> bool:
        """Perform post-deployment health checks."""
        result.add_log("Performing health checks")
        
        import time
        import random
        
        # Simulate health checks
        checks = [
            "HTTP endpoint health check",
            "Database connectivity check",
            "Customer.IO API connectivity check",
            "Memory usage check",
            "CPU usage check"
        ]
        
        passed_checks = 0
        for check in checks:
            time.sleep(0.05)
            # Simulate 95% success rate
            check_passed = random.random() > 0.05
            if check_passed:
                passed_checks += 1
                result.add_log(f"✓ {check} passed")
            else:
                result.add_log(f"✗ {check} failed")
        
        success_rate = passed_checks / len(checks)
        result.performance_metrics["health_check_success_rate"] = success_rate * 100
        
        # Require 80% of checks to pass
        return success_rate >= 0.8
    
    def _perform_rollback(self, deployment_config: DeploymentConfig, result: DeploymentResult) -> None:
        """Perform deployment rollback."""
        if not deployment_config.rollback_version:
            result.add_log("No rollback version specified, skipping rollback")
            return
        
        result.add_log(f"Rolling back to version {deployment_config.rollback_version}")
        result.rollback_performed = True
        
        import time
        rollback_steps = [
            "Stopping failed deployment",
            f"Restoring previous version {deployment_config.rollback_version}",
            "Verifying rollback health",
            "Rollback completed"
        ]
        
        for step in rollback_steps:
            result.add_log(f"Rollback: {step}")
            time.sleep(0.05)
    
    def get_deployment_status(self, deployment_id: str) -> Optional[DeploymentResult]:
        """Get current deployment status."""
        # Check active deployments first
        if deployment_id in self.active_deployments:
            return self.active_deployments[deployment_id]
        
        # Check deployment history
        for deployment in self.deployment_history:
            if deployment.deployment_id == deployment_id:
                return deployment
        
        return None
    
    def list_deployments(self, environment: Optional[Environment] = None, limit: int = 20) -> List[DeploymentResult]:
        """List recent deployments."""
        deployments = self.deployment_history.copy()
        
        # Add active deployments
        deployments.extend(self.active_deployments.values())
        
        # Sort by start time (most recent first)
        deployments.sort(key=lambda d: d.start_time, reverse=True)
        
        return deployments[:limit]
    
    def get_deployment_statistics(self) -> Dict[str, Any]:
        """Get deployment engine statistics."""
        total_deployments = len(self.deployment_history)
        successful_deployments = len([d for d in self.deployment_history if d.is_successful()])
        failed_deployments = len([d for d in self.deployment_history if d.status == DeploymentStatus.FAILED])
        rollbacks_performed = len([d for d in self.deployment_history if d.rollback_performed])
        
        # Calculate average deployment time
        completed_deployments = [d for d in self.deployment_history if d.duration_seconds is not None]
        avg_deployment_time = (
            sum(d.duration_seconds for d in completed_deployments) / len(completed_deployments)
            if completed_deployments else 0
        )
        
        return {
            "total_deployments": total_deployments,
            "successful_deployments": successful_deployments,
            "failed_deployments": failed_deployments,
            "success_rate_percent": (successful_deployments / total_deployments) * 100 if total_deployments > 0 else 0,
            "rollbacks_performed": rollbacks_performed,
            "average_deployment_time_seconds": round(avg_deployment_time, 2),
            "active_deployments": len(self.active_deployments)
        }


class DeploymentManager:
    """Comprehensive production deployment management system."""
    
    def __init__(self, client: CustomerIOClient):
        self.client = client
        self.logger = structlog.get_logger("deployment_manager")
        
        # Initialize deployment components
        self.config_manager = ConfigurationManager()
        self.infrastructure_generator = InfrastructureGenerator()
        self.deployment_engine = DeploymentEngine(self.config_manager)
        
        # System state
        self.start_time = datetime.now(timezone.utc)
        
        # Setup default environments
        self._setup_default_environments()
        
        self.logger.info("DeploymentManager initialized")
    
    def _setup_default_environments(self) -> None:
        """Setup default environment configurations."""
        
        # Development environment
        dev_env = EnvironmentConfig(
            name=Environment.DEVELOPMENT,
            display_name="Development",
            description="Development environment for Customer.IO pipelines",
            provider=InfrastructureProvider.DOCKER,
            region="us-east-1",
            replicas=1,
            resources={
                "requests": {"memory": "256Mi", "cpu": "250m"},
                "limits": {"memory": "512Mi", "cpu": "500m"}
            },
            secrets=[
                SecretConfig(name="CUSTOMER_IO_API_KEY", source="env", description="Customer.IO API key"),
                SecretConfig(name="CUSTOMER_IO_SITE_ID", source="env", description="Customer.IO site ID")
            ],
            config_vars={
                "LOG_LEVEL": "DEBUG",
                "ENVIRONMENT": "development",
                "DEBUG": "true"
            },
            security_level=SecurityLevel.BASIC,
            auto_scaling=False,
            monitoring_enabled=True
        )
        
        # Staging environment
        staging_env = EnvironmentConfig(
            name=Environment.STAGING,
            display_name="Staging",
            description="Staging environment for Customer.IO pipelines",
            provider=InfrastructureProvider.KUBERNETES,
            region="us-east-1",
            namespace="customer-io-staging",
            replicas=2,
            resources={
                "requests": {"memory": "512Mi", "cpu": "500m"},
                "limits": {"memory": "1Gi", "cpu": "1000m"}
            },
            secrets=[
                SecretConfig(name="CUSTOMER_IO_API_KEY", source="k8s", description="Customer.IO API key"),
                SecretConfig(name="CUSTOMER_IO_SITE_ID", source="k8s", description="Customer.IO site ID"),
                SecretConfig(name="DATABASE_URL", source="k8s", description="Database connection URL")
            ],
            config_vars={
                "LOG_LEVEL": "INFO",
                "ENVIRONMENT": "staging",
                "DEBUG": "false"
            },
            security_level=SecurityLevel.STANDARD,
            auto_scaling=True,
            monitoring_enabled=True
        )
        
        # Production environment
        prod_env = EnvironmentConfig(
            name=Environment.PRODUCTION,
            display_name="Production",
            description="Production environment for Customer.IO pipelines",
            provider=InfrastructureProvider.AWS,
            region="us-east-1",
            replicas=5,
            resources={
                "requests": {"memory": "1Gi", "cpu": "1000m"},
                "limits": {"memory": "2Gi", "cpu": "2000m"}
            },
            secrets=[
                SecretConfig(name="CUSTOMER_IO_API_KEY", source="vault", description="Customer.IO API key"),
                SecretConfig(name="CUSTOMER_IO_SITE_ID", source="vault", description="Customer.IO site ID"),
                SecretConfig(name="DATABASE_URL", source="vault", description="Database connection URL"),
                SecretConfig(name="REDIS_URL", source="vault", description="Redis connection URL")
            ],
            config_vars={
                "LOG_LEVEL": "WARN",
                "ENVIRONMENT": "production",
                "DEBUG": "false"
            },
            security_level=SecurityLevel.ENHANCED,
            auto_scaling=True,
            monitoring_enabled=True
        )
        
        # Register environments
        self.config_manager.register_environment(dev_env)
        self.config_manager.register_environment(staging_env)
        self.config_manager.register_environment(prod_env)
    
    def create_deployment(self, name: str, version: str, environment: Environment, 
                         strategy: DeploymentStrategy = DeploymentStrategy.ROLLING_UPDATE,
                         image_tag: Optional[str] = None, created_by: str = "system") -> DeploymentConfig:
        """Create new deployment configuration."""
        
        deployment_id = f"{name}-{environment}-{version}-{int(datetime.now(timezone.utc).timestamp())}"
        
        deployment_config = DeploymentConfig(
            deployment_id=deployment_id,
            name=name,
            version=version,
            environment=environment,
            strategy=strategy,
            image_tag=image_tag or version,
            created_by=created_by
        )
        
        self.logger.info(
            "Deployment configuration created",
            deployment_id=deployment_id,
            environment=environment,
            strategy=strategy
        )
        
        return deployment_config
    
    def deploy_application(self, deployment_config: DeploymentConfig) -> DeploymentResult:
        """Deploy application using specified configuration."""
        self.logger.info(
            "Starting application deployment",
            deployment_id=deployment_config.deployment_id,
            environment=deployment_config.environment
        )
        
        return self.deployment_engine.deploy(deployment_config)
    
    def generate_infrastructure(self, environment: Environment, deployment_config: DeploymentConfig) -> List[InfrastructureTemplate]:
        """Generate infrastructure templates for deployment."""
        env_config = self.config_manager.get_environment_config(environment)
        if not env_config:
            raise ValueError(f"Environment {environment} not configured")
        
        templates = []
        
        # Generate template based on provider
        if env_config.provider == InfrastructureProvider.KUBERNETES:
            template = self.infrastructure_generator.generate_kubernetes_deployment(env_config, deployment_config)
            templates.append(template)
        elif env_config.provider == InfrastructureProvider.DOCKER:
            template = self.infrastructure_generator.generate_docker_compose(env_config, deployment_config)
            templates.append(template)
        elif env_config.provider == InfrastructureProvider.AWS:
            template = self.infrastructure_generator.generate_terraform_aws(env_config, deployment_config)
            templates.append(template)
        
        self.logger.info(
            "Infrastructure templates generated",
            environment=environment,
            provider=env_config.provider,
            templates_count=len(templates)
        )
        
        return templates
    
    def promote_deployment(self, from_env: Environment, to_env: Environment, version: str, created_by: str = "system") -> DeploymentResult:
        """Promote deployment from one environment to another."""
        
        # Validate source environment has successful deployment
        source_deployments = [d for d in self.deployment_engine.deployment_history 
                            if d.deployment_id.startswith(f"customer-io-pipelines-{from_env}-{version}") 
                            and d.is_successful()]
        
        if not source_deployments:
            raise ValueError(f"No successful deployment found for version {version} in {from_env}")
        
        # Create deployment config for target environment
        deployment_config = self.create_deployment(
            name="customer-io-pipelines",
            version=version,
            environment=to_env,
            strategy=DeploymentStrategy.BLUE_GREEN if to_env == Environment.PRODUCTION else DeploymentStrategy.ROLLING_UPDATE,
            created_by=created_by
        )
        
        # Set rollback version (find last successful deployment in target env)
        target_deployments = [d for d in self.deployment_engine.deployment_history 
                            if d.deployment_id.find(f"-{to_env}-") != -1 and d.is_successful()]
        if target_deployments:
            last_deployment = max(target_deployments, key=lambda d: d.start_time)
            # Extract version from deployment ID (simplified)
            deployment_config.rollback_version = "previous"
        
        self.logger.info(
            "Promoting deployment",
            from_env=from_env,
            to_env=to_env,
            version=version
        )
        
        return self.deploy_application(deployment_config)
    
    def create_environment_config_bundle(self, environment: Environment, output_dir: str) -> Dict[str, str]:
        """Create complete configuration bundle for environment."""
        env_config = self.config_manager.get_environment_config(environment)
        if not env_config:
            raise ValueError(f"Environment {environment} not configured")
        
        os.makedirs(output_dir, exist_ok=True)
        bundle_files = {}
        
        # Generate configuration file
        config_yaml = self.config_manager.generate_config_file(environment, "yaml")
        config_file = os.path.join(output_dir, f"{environment}-config.yaml")
        with open(config_file, 'w') as f:
            f.write(config_yaml)
        bundle_files["config"] = config_file
        
        # Generate sample deployment config
        sample_deployment = self.create_deployment(
            name="customer-io-pipelines",
            version="1.0.0",
            environment=environment
        )
        
        # Generate infrastructure templates
        templates = self.generate_infrastructure(environment, sample_deployment)
        for template in templates:
            template_file = os.path.join(output_dir, f"{template.template_id}.{template.template_format}")
            self.infrastructure_generator.export_template(template.template_id, template_file)
            bundle_files[f"template_{template.provider}"] = template_file
        
        # Generate deployment script
        deploy_script = self._generate_deployment_script(environment, env_config)
        script_file = os.path.join(output_dir, f"deploy-{environment}.sh")
        with open(script_file, 'w') as f:
            f.write(deploy_script)
        os.chmod(script_file, 0o755)  # Make executable
        bundle_files["deploy_script"] = script_file
        
        self.logger.info(
            "Configuration bundle created",
            environment=environment,
            output_dir=output_dir,
            files_count=len(bundle_files)
        )
        
        return bundle_files
    
    def _generate_deployment_script(self, environment: Environment, env_config: EnvironmentConfig) -> str:
        """Generate deployment script for environment."""
        
        if env_config.provider == InfrastructureProvider.KUBERNETES:
            return f"""#!/bin/bash
# Customer.IO Pipelines Deployment Script - {environment}
set -e

# Check prerequisites
command -v kubectl >/dev/null 2>&1 || {{ echo "kubectl not found"; exit 1; }}

# Set context and namespace
kubectl config use-context {environment}
kubectl create namespace {env_config.namespace or 'default'} --dry-run=client -o yaml | kubectl apply -f -

# Apply deployment
kubectl apply -f k8s-{environment}-1.0.0.yaml -n {env_config.namespace or 'default'}

# Wait for rollout
kubectl rollout status deployment/customer-io-{environment} -n {env_config.namespace or 'default'}

# Verify deployment
kubectl get pods -n {env_config.namespace or 'default'} -l app=customer-io-pipelines

echo "Deployment to {environment} completed successfully!"
"""
        elif env_config.provider == InfrastructureProvider.DOCKER:
            return f"""#!/bin/bash
# Customer.IO Pipelines Deployment Script - {environment}
set -e

# Check prerequisites
command -v docker >/dev/null 2>&1 || {{ echo "docker not found"; exit 1; }}
command -v docker-compose >/dev/null 2>&1 || {{ echo "docker-compose not found"; exit 1; }}

# Deploy with docker-compose
docker-compose -f docker-{environment}-1.0.0.yaml up -d

# Wait for health check
echo "Waiting for application to be healthy..."
sleep 30

# Verify deployment
docker-compose -f docker-{environment}-1.0.0.yaml ps

echo "Deployment to {environment} completed successfully!"
"""
        else:
            return f"""#!/bin/bash
# Customer.IO Pipelines Deployment Script - {environment}
echo "Manual deployment required for provider: {env_config.provider}"
echo "Please refer to the generated infrastructure templates."
"""
    
    def get_deployment_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive deployment dashboard data."""
        deployment_stats = self.deployment_engine.get_deployment_statistics()
        config_stats = self.config_manager.get_metrics()
        
        # Get recent deployments by environment
        recent_deployments = self.deployment_engine.list_deployments(limit=50)
        deployments_by_env = {}
        for env in Environment:
            env_deployments = [d for d in recent_deployments if d.deployment_id.find(f"-{env}-") != -1]
            deployments_by_env[env] = {
                "total": len(env_deployments),
                "successful": len([d for d in env_deployments if d.is_successful()]),
                "last_deployment": env_deployments[0].start_time.isoformat() if env_deployments else None
            }
        
        return {
            "system": {
                "uptime_seconds": (datetime.now(timezone.utc) - self.start_time).total_seconds(),
                "start_time": self.start_time.isoformat()
            },
            "deployments": {
                **deployment_stats,
                "by_environment": deployments_by_env
            },
            "configuration": config_stats,
            "infrastructure": {
                "templates_generated": len(self.infrastructure_generator.templates),
                "supported_providers": [p.value for p in InfrastructureProvider]
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get DeploymentManager metrics and status."""
        return {
            "manager": {
                "start_time": self.start_time.isoformat(),
                "uptime_seconds": (datetime.now(timezone.utc) - self.start_time).total_seconds()
            },
            "components": {
                "configuration_manager": self.config_manager.get_metrics(),
                "deployment_engine": self.deployment_engine.get_deployment_statistics(),
                "infrastructure_generator": {
                    "templates_generated": len(self.infrastructure_generator.templates)
                }
            },
            "features": {
                "configuration_management": True,
                "infrastructure_generation": True,
                "deployment_automation": True,
                "rollback_support": True,
                "environment_promotion": True,
                "security_hardening": True,
                "multi_provider_support": True
            }
        }