# Staging Environment Configuration
# terraform apply -var-file="envs/staging.tfvars"

# Project Configuration
project_id  = "bobs-brain-staging"
region      = "us-central1"
environment = "staging"

# Application Configuration
app_name    = "bobs-brain"
app_version = "0.14.0"

# Agent Engine Configuration
# Bob agent (main orchestrator)
bob_docker_image = "gcr.io/bobs-brain-staging/agent:0.14.0"

# Foreman agent (iam-senior-adk-devops-lead)
foreman_docker_image = "gcr.io/bobs-brain-staging/foreman:0.14.0"

# Agent Engine compute resources (staging = production-like)
agent_machine_type = "n1-standard-4"
agent_max_replicas = 3

# Gateway Configuration
a2a_gateway_image     = "gcr.io/bobs-brain-staging/a2a-gateway:0.14.0"
slack_webhook_image   = "gcr.io/bobs-brain-staging/slack-webhook:0.14.0"
gateway_max_instances = 10

# Slack Configuration (staging credentials)
# IMPORTANT: Use Secret Manager or CI/CD secrets in production
slack_bot_token      = "xoxb-staging-placeholder"
slack_signing_secret = "staging-placeholder"

# SPIFFE ID (R7) - Bob agent
agent_spiffe_id = "spiffe://intent.solutions/agent/bobs-brain/staging/us-central1/0.14.0"

# AI Model Configuration
model_name = "gemini-2.0-flash-exp"

# Vertex AI Search Configuration (Phase 3)
vertex_search_datastore_id = "adk-documentation"

# Networking
allow_public_access = true

# Labels
labels = {
  cost_center = "staging"
  team        = "platform"
}

# ADK Deployment Configuration
# Staging bucket created by storage.tf (output: staging_bucket_url)
# Used by: adk deploy agent_engine --staging_bucket
# Format: gs://<project-id>-adk-staging

# Knowledge Hub Configuration (org-wide knowledge repository)
# TODO: Wire actual service account emails after projects are configured
knowledge_hub_project_id = "datahub-intent"
knowledge_bucket_prefix  = "datahub-intent"

# Service accounts that need knowledge hub access
bobs_brain_runtime_sa = "" # TODO: Get from Agent Engine deployment
bobs_brain_search_sa  = "" # TODO: Get from Vertex AI Search setup

# Additional consumers can be added here
consumer_service_accounts = []

# ==============================================================================
# Org-Wide Knowledge Hub (LIVE1-GCS)
# ==============================================================================
# Central GCS bucket for org-wide SWE/portfolio audit data
# Disabled by default; enable explicitly to test GCS integration
# ==============================================================================

org_storage_enabled     = false # Set to true to enable org storage bucket
org_storage_bucket_name = "intent-org-knowledge-hub-staging"
org_storage_location    = "US"

# Additional service accounts that can write (future repos)
org_storage_writer_service_accounts = [
  # Will add when other repos integrate:
  # "diagnosticpro-agent@diagnosticpro-staging.iam.gserviceaccount.com",
  # "pipelinepilot-agent@pipelinepilot-staging.iam.gserviceaccount.com",
]
