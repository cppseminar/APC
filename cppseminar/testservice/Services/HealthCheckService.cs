using Microsoft.Extensions.Diagnostics.HealthChecks;
using Microsoft.Extensions.Logging;
using System.Threading;
using System.Threading.Tasks;

namespace testservice.Services;

public class RabbitMQHealthCheck : IHealthCheck
{
    private readonly ILogger<RabbitMQHealthCheck> _logger;
    private readonly RabbitMQService _rabbitMQService;

    public RabbitMQHealthCheck(RabbitMQService rabbitMQService, ILogger<RabbitMQHealthCheck> logger)
    {
        _logger = logger;
        _rabbitMQService = rabbitMQService;
    }

    public Task<HealthCheckResult> CheckHealthAsync(
          HealthCheckContext context,
          CancellationToken cancellationToken = default)
    {
        if (!_rabbitMQService.HealthCheck())
        {
            _logger.LogWarning("Healthcheck on rabbitmq failed");
            return Task.FromResult(HealthCheckResult.Unhealthy("Rabbit mq not ready"));
        }
        return Task.FromResult(HealthCheckResult.Healthy("ok"));
    }
}
