using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;
using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using System.Web;
using testservice.Models;

namespace testservice.Services;

public sealed class RabbitMQService : IDisposable
{
    private readonly ILogger<RabbitMQService> _logger;
    private readonly TestRunsService _testRuns;
    private readonly StorageService _storageService;
    private readonly string _publishQueue;
    private readonly string _subscribeQueue;
    private readonly ConnectionFactory _factory;
    private IConnection _mqConnection;
    private IModel _channel;
    private string _consumerTag = null;

    public RabbitMQService(ILogger<RabbitMQService> logger, IConfiguration config, StorageService storageService, TestRunsService testRuns)
    {
        _logger = logger;
        _testRuns = testRuns;
        _storageService = storageService;
        _publishQueue = config["TEST_REQUESTS_QUEUE"] ?? throw new ArgumentException("Request queue is null");
        _subscribeQueue = config["TEST_RESULTS_QUEUE"] ?? throw new ArgumentException("Result queue is null");
        _factory = new ConnectionFactory() { DispatchConsumersAsync = true };
        _factory.RequestedHeartbeat = TimeSpan.FromSeconds(6); // 5 should be minimum according to docs
        _factory.Uri = new Uri(config["MQ_URI"]);
        _factory.ClientProvidedName = "testservice";
    }

    public void StartProcessing()
    {
        _logger.LogTrace("Subscribing to queue");
        VerifyChannel();
    }

    public bool HealthCheck()
    {
        try
        {
            if (_mqConnection == null || !_mqConnection.IsOpen)
            {
                throw new Exception("Connection error");
            }
            if (_channel == null || !_channel.IsOpen)
            {
                throw new Exception("Channel error");
            }
            return true;
        }
        catch (Exception e)
        {
            _logger.LogWarning("RabbitMQ healthcheck failed with {e}", e);
            return false;
        }
    }

    private async Task HandleEvent(object sender, BasicDeliverEventArgs args)
    {
        _logger.LogTrace("Received event on queue");
        try
        {
            string message = Encoding.UTF8.GetString(args.Body.ToArray());
            _logger.LogTrace("Got result {msg}", message);

            TestResultMessage testMessage = JsonSerializer.Deserialize<TestResultMessage>(
                message, new JsonSerializerOptions() { PropertyNameCaseInsensitive = true });

            await ProcessResultMessageInsecure(testMessage);
        }
        catch (Exception e)
        {
            _logger.LogError("Error during handling received message {message} {e}", args.Body.ToArray(), e);
            _logger.LogTrace("Decoded {message}", Encoding.UTF8.GetString(args.Body.ToArray()));
        }
        finally
        {
            _channel.BasicAck(args.DeliveryTag, false);
        }
    }

    private async Task ProcessResultMessageInsecure(TestResultMessage message)
    {
        var testRun = await _testRuns.GetAsync(message.MetaData);

        try
        {
            using (var client = new HttpClient())
            {
                var studentData = await client.GetByteArrayAsync(message.Students);
                await _storageService.UploadResultAsync(
                    CreateBlobName(testRun.CreatedBy, testRun.Id, TestRunConstants.FileStudents), studentData);

                _logger.LogTrace("Processing teachers");
                var teacherData = await client.GetByteArrayAsync(message.Teachers);
                await _storageService.UploadResultAsync(
                    CreateBlobName(testRun.CreatedBy, testRun.Id, TestRunConstants.FileTeachers), teacherData);

                _logger.LogTrace("Processing dump");
                var zipData = await client.GetByteArrayAsync(message.Data);
                await _storageService.UploadResultAsync(
                    CreateBlobName(testRun.CreatedBy, testRun.Id, TestRunConstants.FileZip), zipData);
            }
            testRun.Status = TestStatus.Finished;
            testRun.FinishedAt = DateTime.UtcNow;
            testRun.Message = TestRunConstants.TestMessageFinished;
            await _testRuns.UpdateAsync(testRun);
        }
        catch (Exception e)
        {
            _logger.LogError("Error during processing result message contents (updating db) {e}", e);
            testRun.Status = TestStatus.Failed;
            testRun.Message = TestRunConstants.TestMessageFailed;
            testRun.FinishedAt = DateTime.UtcNow;
            await _testRuns.UpdateAsync(testRun);
            _logger.LogTrace("Failed test updated in database.");

            throw;
        }
    }

    private static string CreateBlobName(string userName, string testId, string fileName)
    {
        userName = HttpUtility.UrlEncode(userName);
        testId = HttpUtility.UrlEncode(testId);
        fileName = HttpUtility.UrlEncode(fileName);
        return $"{userName}/{testId}/{fileName}";
    }

    private void VerifyChannel()
    {
        if (_mqConnection == null || !_mqConnection.IsOpen)
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
        catch (Exception)
        {
            // Do nothing
        }
        _logger.LogTrace("Disposing of rabbit mq resources");
        _channel.Close();
        _mqConnection.Close();
    }
}
