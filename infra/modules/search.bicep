// Azure Cognitive Search module
// Deploys search service with vector indexing capability

param location string
param resourceNamePrefix string

var searchServiceName = '${resourceNamePrefix}-search'

// Azure Cognitive Search Service
resource searchService 'Microsoft.Search/searchServices@2022-09-01' = {
  name: searchServiceName
  location: location
  sku: {
    name: 'basic' // Use 'standard' or 'standard2' for production
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
  }
}

// Output search service properties
output searchServiceName string = searchService.name
output searchServiceId string = searchService.id
output searchEndpoint string = 'https://${searchService.name}.search.windows.net'
