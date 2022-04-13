using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Azure.Cosmos;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Diagnostics.HealthChecks;
using Microsoft.Extensions.Logging;

namespace testservice.Services
{
    public class RabbitMQHealthCheck : IHealthCheck
    {
        private ILogger<RabbitMQHealthCheck> _logger;
        private RabbitMQService _rabbitMQService;

        public RabbitMQHealthCheck(RabbitMQService rabbitMQService, ILogger<RabbitMQHealthCheck> logger)
        {
            _logger = logger;
            _rabbitMQService = rabbitMQService;
        }

        public Task<HealthCheckResult> CheckHealthAsync(
              HealthCheckContext context,
              CancellationToken cancellationToken = default(CancellationToken))
        {
            if (!_rabbitMQService.HealthCheck())
            {
                _logger.LogWarning("Healthcheck on rabbitmq failed");
                return Task.FromResult(HealthCheckResult.Unhealthy("Rabbit mq not ready"));
            }
            return Task.FromResult(HealthCheckResult.Healthy("ok"));
        }
    }

    public class CosmosHealthCheck : IHealthCheck
    {
        private ILogger<CosmosHealthCheck> _logger;
        private IConfiguration _config;

        public CosmosHealthCheck(IConfiguration config, ILogger<CosmosHealthCheck> logger)
        {
            _logger = logger;
            _config = config;
        }

        public async Task<HealthCheckResult> CheckHealthAsync(
              HealthCheckContext context,
              CancellationToken cancellationToken = default(CancellationToken))
        {
            try
            {
                var container = new CosmosClient(_config["COSMOS_CONNECTION_STRING"])
                    .GetDatabase(_config["COSMOS_DB_NAME"])
                    .GetContainer(DbConstants.TestCaseCollection);

                // https://github.com/Azure/azure-cosmos-dotnet-v3/issues/1610#issuecomment-886720013
                // we cannot do ReadContainerAsync on healtcheck, it will not work in long run
                //var result = await container.ReadContainerAsync();
                //if ((int)result.StatusCode > 299)
                //{
                //    _logger.LogWarning("Healthcheck on cosmosDb failed with {code}", result.StatusCode);
                //    return HealthCheckResult.Unhealthy($"Cannot read cosmos db, code {result.StatusCode}");
                //}
                return HealthCheckResult.Healthy("ok");
            }
            catch (Exception e)
            {
                _logger.LogWarning("Healthcheck on cosmosDb failed with {code}", e);
                return HealthCheckResult.Unhealthy($"Healthcheck failed with {e}");
            }
        }
    }
}
