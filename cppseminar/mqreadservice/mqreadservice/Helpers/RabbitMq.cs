using RabbitMQ.Client;
using System.Text;

namespace mqreadservice
{
    public static class RabbitMq
    {
        public static string? Receive(string mqHostName, string queueName)
        {
            _ = !string.IsNullOrWhiteSpace(mqHostName) ? mqHostName : throw new ArgumentException(nameof(mqHostName));
            _ = !string.IsNullOrWhiteSpace(queueName) ? queueName : throw new ArgumentException(nameof(queueName));

            string? message = null;

            var factory = new ConnectionFactory() { HostName = mqHostName };

            using (var connection = factory.CreateConnection())
            using (var channel = connection.CreateModel())
            {
                channel.QueueDeclare(queue: queueName,
                                     durable: true,
                                     exclusive: false,
                                     autoDelete: false,
                                     new Dictionary<string, object> { { "x-queue-type", "quorum" } });

                bool autoAck = false;
                BasicGetResult result = channel.BasicGet(queueName, autoAck);

                if (result != null)
                {
                    IBasicProperties props = result.BasicProperties;
                    var body = result.Body.Span;
                    message = Encoding.UTF8.GetString(body);

                    // acknowledge receipt of the message, so it is removed from queue
                    channel.BasicAck(result.DeliveryTag, false);
                }
            }

            return message;
        }
    }
}
