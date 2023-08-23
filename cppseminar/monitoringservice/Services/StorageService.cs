using StackExchange.Redis;
using System.Text.Json;
using System.Threading.Tasks;
using monitoringservice.Model;

namespace monitoringservice.Services;
public class StorageService
{
    private IDatabase _db;
    private IServer _server;

    public StorageService()
    {
        ConnectionMultiplexer redis = ConnectionMultiplexer.Connect("redis.local");
        _db = redis.GetDatabase();
        _server = redis.GetServer("redis.local", 6379);
    }

    public async Task setConnectionlogAsync(ConnectionLog connectionLog)
    {
        System.Console.WriteLine("Setting connection log "+connectionLog.UserEmail);
        await _db.StringSetAsync(connectionLog.UserEmail, connectionLog.Timestamp);
    }

    public async Task<string?> getValueAsync(string Key)
    {
        string value = await _db.StringGetAsync(Key);
        return value;
    }

/* This works only when key-value pairs of string-string are in redis */
    public async Task<string> getConnectionLogsJsonAsync()
    {
        List<ConnectionLog> connectionLogsList = new List<ConnectionLog>();
            
        var emails = _server.Keys();
        foreach (var email in emails)
        {
            var timestamp = await _db.StringGetAsync(email);
            connectionLogsList.Add(new ConnectionLog(email, timestamp));
        }
        System.Console.WriteLine("Get connections returns " + JsonSerializer.Serialize(connectionLogsList));

        return JsonSerializer.Serialize(connectionLogsList);
    }
}