// Main Bicep template for Azure RAG Application
// Orchestrates the deployment of all Azure resources

param location string = resourceGroup().location
param environmentName string = 'dev'
param projectName string = 'azure-rag'

// Construct resource naming
var resourceNamePrefix = '${projectName}-${environmentName}'

// Outputs for deployed resources
output resourceGroupName string = resourceGroup().name
output location string = location
output projectName string = projectName
output environmentName string = environmentName

// TODO: Add module references for:
// - App Service (backend)
// - Azure Storage (documents)
// - Cognitive Search (vector index)
// - OpenAI Service (embeddings and chat)
// - Key Vault (secrets management)
// - Container Registry (Docker images)
// - Application Insights (monitoring)

// Example module structure (uncomment and customize as needed):
/*
module appService 'modules/app_service.bicep' = {
  name: 'app-service-deployment'
  params: {
    location: location
    resourceNamePrefix: resourceNamePrefix
    containerRegistryLoginServer: containerRegistry.properties.loginServer
    containerImage: '${containerRegistry.properties.loginServer}/rag-backend:latest'
  }
}

module storage 'modules/storage.bicep' = {
  name: 'storage-deployment'
  params: {
    location: location
    resourceNamePrefix: resourceNamePrefix
    containerName: 'documents'
  }
}

module search 'modules/search.bicep' = {
  name: 'search-deployment'
  params: {
    location: location
    resourceNamePrefix: resourceNamePrefix
  }
}

module openai 'modules/openai.bicep' = {
  name: 'openai-deployment'
  params: {
    location: location
    resourceNamePrefix: resourceNamePrefix
  }
}

module keyVault 'modules/keyvault.bicep' = {
  name: 'keyvault-deployment'
  params: {
    location: location
    resourceNamePrefix: resourceNamePrefix
  }
}

module appInsights 'modules/appinsights.bicep' = {
  name: 'appinsights-deployment'
  params: {
    location: location
    resourceNamePrefix: resourceNamePrefix
  }
}
*/
