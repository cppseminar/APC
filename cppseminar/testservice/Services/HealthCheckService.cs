using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Azure.Cosmos;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Diagnostics.HealthChecks;

namespace testservice.Services
{
    public class RabbitMQHealthCheck : IHealthCheck
    {
        private RabbitMQService _rabbitMQService;

        public RabbitMQHealthCheck(RabbitMQService rabbitMQService)
        {
            _rabbitMQService = rabbitMQService;
        }

        public Task<HealthCheckResult> CheckHealthAsync(
              HealthCheckContext context,
              CancellationToken cancellationToken = default(CancellationToken))
        {
            if (!_rabbitMQService.HealthCheck())
            {
                return Task.FromResult(HealthCheckResult.Unhealthy("Rabbit mq not ready"));
            }
            return Task.FromResult(HealthCheckResult.Healthy("ok"));
        }
    }

    public class CosmosHealthCheck : IHealthCheck
    {
        private Container _container;

        public CosmosHealthCheck(IConfiguration config)
        {
            _container = new CosmosClient(config["COSMOS_CONNECTION_STRING"])
                .GetDatabase(config["COSMOS_DB_NAME"])
                .GetContainer(DbConstants.TestCaseCollection);
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
