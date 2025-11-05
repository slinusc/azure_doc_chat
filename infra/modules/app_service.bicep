// App Service module for Flask backend
// Deploys Azure App Service with Docker container support

param location string
param resourceNamePrefix string
param containerRegistryLoginServer string
param containerImage string

var appServicePlanName = '${resourceNamePrefix}-asp'
var appServiceName = '${resourceNamePrefix}-app'

// App Service Plan (B1 - Basic tier for development)
resource appServicePlan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: 'B1'
    tier: 'Basic'
    capacity: 1
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

// App Service
resource appService 'Microsoft.Web/sites@2022-09-01' = {
  name: appServiceName
  location: location
  kind: 'app,linux,container'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'DOCKER|${containerImage}'
      appSettings: [
        {
          name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'
          value: 'false'
        }
      ]
      healthCheckPath: '/api/health'
    }
    httpsOnly: true
  }
}

// Output the app service properties
output appServiceName string = appService.name
output appServiceId string = appService.id
output appServiceUri string = 'https://${appService.properties.defaultHostName}'
output principalId string = appService.identity.principalId
