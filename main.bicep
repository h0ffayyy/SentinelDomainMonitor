@description('Storage Account type')
@allowed([
  'Premium_LRS'
  'Premium_ZRS'
  'Standard_GRS'
  'Standard_GZRS'
  'Standard_LRS'
  'Standard_RAGRS'
  'Standard_RAGZRS'
  'Standard_ZRS'
])
param storageAccountType string = 'Standard_LRS'

@description('The storage account location.')
param location string = resourceGroup().location

@description('The name of the storage account')
param storageAccountName string = 'store${uniqueString(resourceGroup().id)}'

@description('The name of the container instance')
param containerName string = 'domain-monitor'

param imageName string = 'h0ffayyy/sentinel-domain-monitor'
param imageTag string = 'v1'
param LogAnalyticsWorkspaceId string
param LogAnalyticsSharedKey string

@description('The behavior of Azure runtime if container has stopped.')
@allowed([
  'Always'
  'Never'
  'OnFailure'
])
param restartPolicy string = 'Never'

resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: storageAccountType
  }
  kind: 'StorageV2'
  properties: {}
}

resource blobServices 'Microsoft.Storage/storageAccounts/blobServices@2021-06-01' = {
  parent: storageAccount
  name: 'default'
  properties: {
    deleteRetentionPolicy: {
      enabled: true
      days: 7
    }
  }
}

resource blobContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2021-06-01' = {
  parent: blobServices
  name: 'domainmonitor'
}

resource containerGroup 'Microsoft.ContainerInstance/containerGroups@2021-07-01' = {
  name: containerName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    containers: [
      {
        name: containerName
        properties: {
          image: '${imageName}:${imageTag}'
          resources: {
            requests: {
              cpu: 1
              memoryInGB: json('1.5')
            }
          }
          environmentVariables: [
            {
              name: 'WORKSPACE_ID'
              value: LogAnalyticsWorkspaceId
            }
            {
              name: 'SHARED_KEY'
              value: LogAnalyticsSharedKey
            }
            {
              name: 'azure_storage_account'
              value: storageAccountName
            }
            {
              name: 'azure_storage_blob_name'
              value: 'domains.txt'
            }
            {
              name: 'azure_storage_container'
              value: 'domainmonitor'
            }
          ]
          ports: [
            {
              port: 80
              protocol: 'TCP'
            }
          ]
        }
      }
    ]
    restartPolicy: restartPolicy
    osType: 'Linux'
    ipAddress: {
      type: 'Public'
      ports: [
        {
          port: 80
          protocol: 'TCP'
        }
      ]
    }
  }
}

resource roleAssignment 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(subscription().subscriptionId, containerGroup.name, 'RoleAssignment')
  scope: storageAccount
  properties: {
    principalId: containerGroup.identity.principalId
    roleDefinitionId: '/subscriptions/${subscription().subscriptionId}/providers/Microsoft.Authorization/roleDefinitions/2a2b9908-6ea1-4ae2-8e65-a410df84e7d1'
  }
}

output storageAccountName string = storageAccountName
output storageAccountId string = storageAccount.id
output containerName string = containerName
