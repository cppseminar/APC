
using Microsoft.Azure.Management.Compute.Fluent;
using Microsoft.Azure.Management.Fluent;
using Microsoft.Azure.Management.ResourceManager.Fluent.Authentication;
using Microsoft.Azure.Management.ResourceManager.Fluent;

namespace ApcScaler
{
    public class Workers
    {
        private readonly ILogger<Scaler> _logger;
        private readonly IConfiguration _configuration;

        private readonly string _apcWorkerResourceGroup;
        private readonly string _apcWorkerVmNamePrefix;

        private readonly IAzure? _azureClient;
        public Workers(ILogger<Scaler> logger, IConfiguration configuration)
        {
            _logger = logger;
            _configuration = configuration;

            _apcWorkerResourceGroup = _configuration["APC_WORKER_RESOURCE_GROUP"];
            _apcWorkerVmNamePrefix = _configuration["APC_WORKER_VM_NAME_PREFIX"];

            _ = !string.IsNullOrWhiteSpace(_apcWorkerResourceGroup) ? _apcWorkerResourceGroup : 
                throw new Exception("Missing configuration value of [APC_WORKER_RESOURCE_GROUP]");
            _ = !string.IsNullOrWhiteSpace(_apcWorkerVmNamePrefix) ? _apcWorkerVmNamePrefix : 
                throw new Exception("Missing configuration value of [APC_WORKER_VM_NAME_PREFIX]");

            var subscriptionId = _configuration["AZURE_SUBSCRIPTION_ID"];
            var tenantId = _configuration["AZURE_TENANT_ID"];
            var clientId = _configuration["AZURE_CLIENT_ID"];
            var clientSecret = _configuration["AZURE_CLIENT_SECRET"];

            _ = !string.IsNullOrWhiteSpace(subscriptionId) ? subscriptionId :
                throw new Exception("Missing configuration value of [AZURE_SUBSCRIPTION_ID]");
            _ = !string.IsNullOrWhiteSpace(tenantId) ? tenantId :
                throw new Exception("Missing configuration value of [AZURE_TENANT_ID]");
            _ = !string.IsNullOrWhiteSpace(clientId) ? clientId :
                throw new Exception("Missing configuration value of [AZURE_CLIENT_ID]");
            _ = !string.IsNullOrWhiteSpace(clientSecret) ? clientSecret :
                throw new Exception("Missing configuration value of [AZURE_CLIENT_SECRET]");

            try
            {
                var creds = new AzureCredentialsFactory().FromServicePrincipal(clientId,
                    clientSecret, tenantId, AzureEnvironment.AzureGlobalCloud);

                _azureClient = Azure.Authenticate(creds).WithSubscription(subscriptionId);

                _logger.LogDebug("Azure client successfully created");
            }
            catch (Exception e)
            {
                _logger.LogError(Helpers.ExtractErrorMessage(e));
            }
        }
        public int CountVm()
        {
            int allVmCounter = 0;
            int runningVmCounter = 0;

            _ = _azureClient ?? throw new Exception("_azureClient is null");
            var vmInRg = _azureClient.VirtualMachines.ListByResourceGroup(_apcWorkerResourceGroup);
            _logger.LogDebug("List of worker VMs successfully retrieved");

            foreach (var virtualMachine in vmInRg)
            {
                if (virtualMachine.ComputerName.StartsWith(_apcWorkerVmNamePrefix))
                {
                    if (virtualMachine.PowerState == PowerState.Running)
                    {
                        runningVmCounter++;
                    }

                    if (virtualMachine.PowerState == PowerState.Stopped)
                    {
                        virtualMachine.Deallocate();
                        _logger.LogInformation("Stopped worker VM (Name: {vmName}, Id:{vmId} was successfully deallocated",
                            virtualMachine.ComputerName, virtualMachine.Id);
                    }
                }

                allVmCounter++;
            }

            _logger.LogDebug("{allVmCounter} worker VM found ({runningVmCounter} running)", allVmCounter, runningVmCounter);

            return runningVmCounter;
        }
        public void ScaleOutVm(int numberOfNewVm)
        {
            _logger.LogInformation("ScaleOut action started. We plan to start {numberOfNewVm} worker VMs.",
                numberOfNewVm);

            _ = _azureClient ?? throw new Exception("_azureClient is null");
            var vmInRg = _azureClient.VirtualMachines.ListByResourceGroup(_apcWorkerResourceGroup);
            _logger.LogDebug("List of worker VMs successfully retrieved");

            foreach (var virtualMachine in vmInRg)
            {
                if (virtualMachine.ComputerName.StartsWith(_apcWorkerVmNamePrefix))
                {
                    if (virtualMachine.PowerState == PowerState.Deallocated)
                    {
                        virtualMachine.Start();
                        _logger.LogInformation("Deallocated worker VM (Name: {vmName}, Id:{vmId} was successfully started",
                            virtualMachine.ComputerName, virtualMachine.Id);

                        numberOfNewVm--;
                    }
                   
                    if (numberOfNewVm < 1)
                    {
                        break;
                    }
                }
            }
        }
        public int GetNeededNumberOfVm(decimal threshold, int actNoOfWorkers, decimal scaleAverage)
        {
            int rv = 0;

            while (scaleAverage / (decimal)actNoOfWorkers >= threshold)
            {
                rv++;
            }

            return rv;
        }
    }
}
