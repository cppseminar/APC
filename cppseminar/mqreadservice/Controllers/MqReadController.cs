using Microsoft.AspNetCore.Mvc;
using mqreadservice.Models;
using Serilog;
using System.Text.Json;

namespace mqreadservice.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class MqReadController : ControllerBase
    {
        private readonly IConfiguration _configuration;
        private readonly ILogger<MqReadController> _logger;
        public MqReadController(IConfiguration configuration, ILogger<MqReadController> logger)
        {
            _configuration = configuration;
            _logger = logger;
        }

        [HttpGet()]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public IActionResult Get()
        {
            var mqHostName = _configuration["MQ_URI"];
            var mqQueueName = _configuration["TEST_INPUT_QUEUE"];
            var returnUrl = _configuration["VM_TEST_RETURN_ADDR"];

            TestRun tr;

            try
            {
                var msg = RabbitMq.Receive(mqHostName, mqQueueName);

                if (string.IsNullOrWhiteSpace(msg))
                {
                    _logger.LogInformation("No message found. Input RabbitMq message queue is empty.");
                    return NotFound();
                }

                MqTestRun? mqtr = JsonSerializer.Deserialize<MqTestRun>(msg);

                if (mqtr != null)
                {
                    var sourceFile = BlobStorage.DownloadBlob(mqtr.contentUrl);

                    if (sourceFile != null)
                    {
                        tr = new TestRun();
                        tr.returnUrl = returnUrl;
                        tr.metaData = mqtr.metaData;
                        tr.dockerImage = mqtr.dockerImage;

                        tr.files = new Files();
                        tr.files.maincpp = sourceFile;

                        _logger.LogDebug("Successfully got TestRun data");
                    }
                    else
                    {
                        _logger.LogError("Unable to get source file for a TestRun (blobName: [{blobName}])",
                                mqtr.metaData);

                        return StatusCode(StatusCodes.Status500InternalServerError);
                    }
                }
                else
                {
                    _logger.LogError("Unable to deserialize TestRun JSON data received from RabbitMq");
                    return StatusCode(StatusCodes.Status500InternalServerError);
                }
            }
            catch (Exception e)
            {
                var errmsg = Helpers.ExtractErrorMessage(e);
                _logger.LogError(errmsg);
                return StatusCode(StatusCodes.Status500InternalServerError);
            }

            var jsonPayload = JsonSerializer.Serialize<TestRun>(tr);

            _logger.LogInformation("Message {jsonPayload} sent in response.", jsonPayload);

            return Ok(tr);
        }
    }
}






