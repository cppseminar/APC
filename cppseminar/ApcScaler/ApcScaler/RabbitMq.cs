
using RabbitMQ.Client;

namespace ApcScaler
{
    public static class RabbitMq
    {
        public static int GetQueueSize(string mqHostName, string queueName)
        {
            _ = !string.IsNullOrWhiteSpace(mqHostName) ? mqHostName : throw new ArgumentException(nameof(mqHostName));
            _ = !string.IsNullOrWhiteSpace(queueName) ? queueName : throw new ArgumentException(nameof(queueName));

            int rv = -1;

            var factory = new ConnectionFactory() { HostName = mqHostName };
            using (var connection = factory.CreateConnection())
            using (var channel = connection.CreateModel())
            {
                rv = (int)channel.MessageCount(queueName);
            }

            return rv;
        }
    }
}
