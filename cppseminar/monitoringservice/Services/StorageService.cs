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

    public async Task setPairAsync(string Key, string Value)
    {
        await _db.StringSetAsync(Key, Value);
    }

    public async Task<string?> getValueAsync(string Key)
    {
        string value = await _db.StringGetAsync(Key);
        return value;
    }

    public async Task<string> getEveryKeyValueJsonAsync()
    {
        List<Pair> pairs = new List<Pair>();
            
        var keys = _server.Keys();
        foreach (var key in keys)
        {
            var value = await _db.StringGetAsync(key);
            pairs.Add(new Pair(key, value));
        }

        return JsonSerializer.Serialize(pairs);        
    }

}