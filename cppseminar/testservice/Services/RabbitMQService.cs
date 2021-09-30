using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using RabbitMQ.Client;

namespace testservice.Services
{
    public class RabbitMQService : IDisposable
    {
        private ILogger<RabbitMQService> _logger;
        private string _publishQueue;
        private string _subscribeQueue;
        private ConnectionFactory _factory;
        private IConnection _mqConnection;
        private IModel _channel;

        public RabbitMQService(ILogger<RabbitMQService> logger, IConfiguration config)
        {
            _logger = logger;
            _publishQueue = config["TEST_REQUESTS_QUEUE"] ?? throw new ArgumentException("Request queue is null");
            _subscribeQueue = config["TEST_RESULTS_QUEUE"] ?? throw new ArgumentException("Result queue is null");
            _factory = new ConnectionFactory();
            _factory.Uri = new Uri("amqp://rabbitmq.local/");
            _factory.ClientProvidedName = "testservice";
            _mqConnection = _factory.CreateConnection();
            _channel = _mqConnection.CreateModel();
        }

        public void StartProcessing()
        {
            _logger.LogTrace("Subscribing to queue");
            _mqConnection.CreateModel().QueueDeclare(queue: _publishQueue, durable: true, exclusive: false, autoDelete: false);
        }

        public void StopProcessing()
        {
            _logger.LogTrace("Disconnecting from queue");
        }

        private void HandleEvent()
        {

        }

        private void VerifyChannel()
        {
            if(!_mqConnection.IsOpen)
            {
                _logger.LogWarning("Connection to rabbitmq is closed, reopening");
                _mqConnection = _factory.CreateConnection();
                _logger.LogTrace("Connection reopened successfully");
            }
            if (!_channel.IsOpen)
            {
                _logger.LogWarning("Channel is closed, recreating");
                _channel = _mqConnection.CreateModel();
                _logger.LogTrace("Channel created successfully");
            }
        }

        public void Publish(string jsonMessage)
        {
            VerifyChannel();  // Throws on failure
            var props = _channel.CreateBasicProperties();
            props.Persistent = true;
            _channel.BasicPublish(exchange: "", routingKey: _publishQueue, props, Encoding.UTF8.GetBytes(jsonMessage));
        }

        public void Dispose()
        {
            _logger.LogTrace("Disposing of rabbit mq resources");
            _channel.Close();
            _mqConnection.Close();
        }
    }
}
