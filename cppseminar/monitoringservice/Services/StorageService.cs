using StackExchange.Redis;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using monitoringservice.Model;

namespace monitoringservice.Services;
public class StorageService
{
    private readonly IDatabase _db;
    private readonly IServer _server;

    public StorageService()
    {
        ConnectionMultiplexer redis = ConnectionMultiplexer.Connect("redis.local");
        _db = redis.GetDatabase();
        _server = redis.GetServer("redis.local", 6379);
    }

    public async Task setConnectionlogAsync(ConnectionLog connectionLog)
    {
        await _db.StringSetAsync(connectionLog.UserEmail, connectionLog.Timestamp.ToString());
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
        try{
            foreach (var email in emails)
            {
                var timestamp = await _db.StringGetAsync(email);
                connectionLogsList.Add(new ConnectionLog(email, DateTime.Parse(timestamp)));
            }
            return JsonSerializer.Serialize(connectionLogsList);
        }
        catch (Exception e){
            return "";
        }
    }
}