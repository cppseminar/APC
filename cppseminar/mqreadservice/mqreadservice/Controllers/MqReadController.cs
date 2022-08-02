using Microsoft.AspNetCore.Mvc;
using mqreadservice.Models;
using System.Text.Json;

namespace mqreadservice.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class MqReadController : ControllerBase
    {
        private readonly ILogger<MqReadController> _logger;
        private readonly IConfiguration _configuration;

        public MqReadController(ILogger<MqReadController> logger, IConfiguration configuration)
        {
            _logger = logger;
            _configuration = configuration;
        }

        [HttpGet()]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        public IActionResult Get()
        {
            var mqConfig = _configuration.GetSection("RabbitMq").Get<RabbitMqConfig>();
            var returnUrl = _configuration["VM_TEST_RETURN_ADDR"];

            TestRun tr;

            try
            {
                var msg = RabbitMq.Receive(mqConfig.MqHostName, mqConfig.QueueName);

                if (msg == "[<empty>]")
                {
                    _logger.LogInformation("No message found. Input RabbitMq message queue is empty.");
                    return NotFound();
                }

                if (msg != null)
                {
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
                            _logger.LogError(String.Format("Unable to get source file for a TestRun (blobName: [{0}])",
                                    mqtr.metaData));
                            return StatusCode(StatusCodes.Status500InternalServerError);
                        }
                    }
                    else
                    {
                        _logger.LogError("Unable to deserialize TestRun JSON data from RabbitMq");
                        return StatusCode(StatusCodes.Status500InternalServerError);
                    }
                }
                else
                {
                    _logger.LogError("Unable to get TestRun data from RabbitMq");
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
            _logger.LogInformation("Message {message} sent in response.", jsonPayload);

            return Ok(tr);
        }
    }
}






