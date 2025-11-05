// Azure Key Vault module
// Stores secrets and manages access policies

param location string
param resourceNamePrefix string

var keyVaultName = 'kv-${resourceNamePrefix}'

// Azure Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2022-11-01' = {
  name: keyVaultName
  location: location
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    accessPolicies: []
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    enablePurgeProtection: false
  }
}

// Output key vault properties
output keyVaultName string = keyVault.name
output keyVaultId string = keyVault.id
output keyVaultUri string = keyVault.properties.vaultUri
