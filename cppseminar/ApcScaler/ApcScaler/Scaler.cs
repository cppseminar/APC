
namespace ApcScaler
{
    public class Scaler : BackgroundService
    {
        private readonly ILogger<Scaler> _logger;
        private readonly IConfiguration _configuration;

        public Scaler(ILogger<Scaler> logger, IConfiguration configuration)
        {
            _logger = logger;
            _configuration = configuration;
        }
        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            var mqHostName = _configuration["MQ_HOST_NAME"];
            var mqQueueName = _configuration["MQ_QUEUE_NAME"];

            var scaleOutThreshold = Convert.ToDecimal(_configuration["SCALE_OUT_THRESHOLD"]);
            var intervalBetweenChecks = Convert.ToInt32(_configuration["INTERVAL_BETWEEN_CHECKS"]);
            var maxNumberOfWorkers = Convert.ToInt32(_configuration["MAX_NUMBER_OF_WORKERS"]);

            var vmManager = new Workers(_logger, _configuration);

            var scaleMetrics = new SlidingBuffer<decimal>(12);

            while (!stoppingToken.IsCancellationRequested)
            {
                int actQueueSize = -1;
                int actNoOfWorkers = -1;
                decimal actScaleMetric = 0.0M;

                try
                {
                    actQueueSize = RabbitMq.GetQueueSize(mqHostName, mqQueueName);
                    _logger.LogDebug("Queue size at {time} is {size}", DateTimeOffset.Now, actQueueSize);
                }
                catch (Exception e)
                {
                    _logger.LogError(Helpers.ExtractErrorMessage(e));
                }

                try
                {
                    actNoOfWorkers = vmManager.CountVm();
                    _logger.LogDebug("Number of worker VMs at {time} is {number}", 
                        DateTimeOffset.Now, actNoOfWorkers);
                }
                catch (Exception e)
                {
                    _logger.LogError(Helpers.ExtractErrorMessage(e));
                }

                if (actNoOfWorkers == maxNumberOfWorkers)
                {
                    _logger.LogDebug("We are running with maximum number of workers. NO ACTION REQUIRED.");
                }
                else
                {
                    if ((actQueueSize >= 0) && (actNoOfWorkers > 0))
                    {
                        actScaleMetric = (decimal)actQueueSize / (decimal)actNoOfWorkers;
                        _logger.LogDebug("Current scale metric at {time} is {metric}",
                            DateTimeOffset.Now, actScaleMetric);

                        scaleMetrics.Add(actScaleMetric);

                        if (scaleMetrics.ActCount() == scaleMetrics.MaxCount())
                        {
                            if (scaleMetrics.IsAlwaysAbove(scaleOutThreshold))
                            {
                                _logger.LogInformation("Scale out condition is met. WE SCALE OUT.");

                                decimal scaleAverage = scaleMetrics.GetLatestAverage();
                                int numberOfNewVm = vmManager.GetNeededNumberOfVm(scaleOutThreshold,
                                    actNoOfWorkers, scaleAverage);

                                if (actNoOfWorkers + numberOfNewVm > maxNumberOfWorkers)
                                {
                                    numberOfNewVm = maxNumberOfWorkers - actNoOfWorkers;
                                }

                                try
                                {
                                    vmManager.ScaleOutVm(numberOfNewVm);
                                }
                                catch (Exception e)
                                {
                                    _logger.LogError(Helpers.ExtractErrorMessage(e));
                                }                                
                            }
                            else
                            {
                                _logger.LogDebug("Scale out condition is not met. NO ACTION REQUIRED.");
                            }
                        }
                        else
                        {
                            _logger.LogDebug("Skipping evaluating scale average - there are not enough values");
                        }
                    }
                    else if ((actQueueSize >= 0) && (actNoOfWorkers == 0))
                    {
                        try
                        {
                            _logger.LogInformation("Queue is not empty and no worker is running. WE START ONE.");
                            vmManager.ScaleOutVm(1);
                        }
                        catch (Exception e)
                        {
                            _logger.LogError(Helpers.ExtractErrorMessage(e));
                        }
                    }
                    else if ((actQueueSize == 0) && (actNoOfWorkers == 0))
                    {
                        _logger.LogDebug("Queue is empty and no worker is running. QUIET TIMES.");
                    }
                    else
                    {
                        _logger.LogWarning("Skipping collecting scale metrics - strange error with getting scale metrics");
                    }
                }

                if (intervalBetweenChecks > 0)
                {
                    await Task.Delay(intervalBetweenChecks * 1000, stoppingToken);
                }
            }
        }
    }
}