using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Microsoft.EntityFrameworkCore;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;
using testservice.Models;
using System.Web;
using Microsoft.Extensions.DependencyInjection;

namespace testservice.Services
{
    public class RabbitMQService : IDisposable
    {
        private ILogger<RabbitMQService> _logger;
        private IServiceProvider _serviceProvider;
        private StorageService _storageService;
        private string _publishQueue;
        private string _subscribeQueue;
        private ConnectionFactory _factory;
        private IConnection _mqConnection;
        private IModel _channel;
        private string _consumerTag = null;

        public RabbitMQService(ILogger<RabbitMQService> logger, IConfiguration config, StorageService storageService, IServiceProvider services)
        {
            _logger = logger;
            _serviceProvider = services;
            _storageService = storageService;
            _publishQueue = config["TEST_REQUESTS_QUEUE"] ?? throw new ArgumentException("Request queue is null");
            _subscribeQueue = config["TEST_RESULTS_QUEUE"] ?? throw new ArgumentException("Result queue is null");
            _factory = new ConnectionFactory() { DispatchConsumersAsync = true };
            _factory.Uri = new Uri(config["MQ_URI"]);
            _factory.ClientProvidedName = "testservice";
        }

        public void StartProcessing()
        {
            _logger.LogTrace("Subscribing to queue");
            VerifyChannel();
        }

        public void StopProcessing()
        {
            _logger.LogTrace("Disconnecting from queue");

        }

        private async Task HandleEvent(object sender, BasicDeliverEventArgs args)
        {
            _logger.LogTrace("Received event on queue");
            try
            {
                using (var scope = _serviceProvider.CreateScope())
                {
                    var dbService = scope.ServiceProvider.GetRequiredService<DbService>();
                    string message = Encoding.UTF8.GetString(args.Body.ToArray());
                    TestResultMessage testMessage = JsonSerializer.Deserialize<TestResultMessage>(
                        message, new JsonSerializerOptions() { PropertyNameCaseInsensitive = true });
                    await ProcessResultMessageInsecure(testMessage, dbService);
                }

            }
            catch(Exception e)
            {
                _logger.LogError("Error during handling received message {message} {e}", args.Body.ToArray(), e);
                _logger.LogTrace("Decoded {message}", Encoding.UTF8.GetString(args.Body.ToArray()));
            }
            finally
            {
                _channel.BasicAck(args.DeliveryTag, false);
            }
        }

        private async Task ProcessResultMessageInsecure(TestResultMessage message, DbService dbService)
        {
            var testRun = await dbService.Tests.FirstOrDefaultAsync(test => test.Id == message.MetaData);
            if (testRun == null)
            {
                _logger.LogError("Cannot find testRun for results {id} {message}", message.MetaData, message);
                return;
            }
            _logger.LogTrace("Found matching test case");

            try
            {
                using (var client = new WebClient())
                {
                    _logger.LogTrace("Processing students");
                    var studentData = client.DownloadData(message.Students);
                    await _storageService.UploadResultAsync(
                        CreateBlobName(testRun.CreatedBy, testRun.Id, TestRunConstants.FileStudents), studentData);

                    _logger.LogTrace("Processing teachers");
                    var teacherData = client.DownloadData(message.Teachers);
                    await _storageService.UploadResultAsync(
                        CreateBlobName(testRun.CreatedBy, testRun.Id, TestRunConstants.FileTeachers), teacherData);

                    _logger.LogTrace("Processing dump");
                    var zipData = client.DownloadData(message.Data);
                    await _storageService.UploadResultAsync(
                        CreateBlobName(testRun.CreatedBy, testRun.Id, TestRunConstants.FileZip), zipData);
                }
                testRun.Status = TestRunConstants.TestFinished;
                testRun.FinishedAt = DateTime.UtcNow;
                testRun.Message = TestRunConstants.TestMessageFinished;
                await dbService.SaveChangesAsync();
            }
            catch (Exception e)
            {
                _logger.LogError("Error during processing result message contents (updating db) {e}", e);
                testRun.Status = TestRunConstants.TestFailed;
                testRun.Message = TestRunConstants.TestMessageFailed;
                testRun.FinishedAt = DateTime.UtcNow;
                await dbService.SaveChangesAsync();
                throw;
            }
        }

        private string CreateBlobName(string userName, string testId, string fileName)
        {
            userName = HttpUtility.UrlEncode(userName);
            testId = HttpUtility.UrlEncode(testId);
            fileName = HttpUtility.UrlEncode(fileName);
            return $"{userName}/{testId}/{fileName}";
        }

        private void VerifyChannel()
        {
            if(_mqConnection == null || !_mqConnection.IsOpen)
            {
                _logger.LogWarning("Connection to rabbitmq is closed, reopening");
                _mqConnection = _factory.CreateConnection();
                _mqConnection.CreateModel().QueueDeclare(
                    queue: _publishQueue,
                    durable: true,
                    exclusive: false,
                    autoDelete: false,
                    new Dictionary<string, object> { { "x-queue-type", "quorum" } }
                );
                _mqConnection.CreateModel().QueueDeclare(
                    queue: _subscribeQueue,
                    durable: true,
                    exclusive: false,
                    autoDelete: false,
                    new Dictionary<string, object> { { "x-queue-type", "quorum" } }
                );
                _logger.LogTrace("Connection reopened successfully");
            }
            if (_channel == null || !_channel.IsOpen)
            {
                _logger.LogWarning("Channel is closed, recreating");
                RecreateChannelNocheck();
                _logger.LogTrace("Channel created successfully");
            }
        }

        private void RecreateChannelNocheck()
        {
            _channel = _mqConnection.CreateModel();
            var consumer = new AsyncEventingBasicConsumer(_channel);
            consumer.Received += HandleEvent;
            _consumerTag = _channel.BasicConsume(queue: _subscribeQueue, autoAck: false, consumer);
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
            try
            {
                _channel.BasicCancel(_consumerTag);
            }
            catch(Exception)
            {
                // Do nothing
            }
            _logger.LogTrace("Disposing of rabbit mq resources");
            _channel.Close();
            _mqConnection.Close();
        }
    }
}
