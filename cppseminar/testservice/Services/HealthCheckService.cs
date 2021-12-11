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
        private Container _container;
        private ILogger<CosmosHealthCheck> _logger;

        public CosmosHealthCheck(IConfiguration config, ILogger<CosmosHealthCheck> logger)
        {
            _container = new CosmosClient(config["COSMOS_CONNECTION_STRING"])
                .GetDatabase(config["COSMOS_DB_NAME"])
                .GetContainer(DbConstants.TestCaseCollection);
            _logger = logger;
        }

        public async Task<HealthCheckResult> CheckHealthAsync(
              HealthCheckContext context,
              CancellationToken cancellationToken = default(CancellationToken))
        {
            try
            {
                var result = await _container.ReadContainerAsync();
                if ((int)result.StatusCode > 299)
                {
                    _logger.LogWarning("Healthcheck on cosmosDb failed with {code}", result.StatusCode);
                    return HealthCheckResult.Unhealthy($"Cannot read cosmos db, code {result.StatusCode}");
                }
                return HealthCheckResult.Healthy("ok");
            }
            catch (Exception e)
            {
                return HealthCheckResult.Unhealthy($"Healthcheck failed with {e}");
            }
        }
    }
}
