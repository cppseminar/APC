using StackExchange.Redis;
using System.Text.Json;
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

    public void setPair(string Key, string Value)
    {
        _db.StringSet(Key, Value);
    }

    public string getValue(string Key)
    {
        string value = _db.StringGet(Key);
        return value == null ? "" : value;
    }

    public string getEveryKeyValueJson()
    {
        List<Pair> pairs = new List<Pair>();
        
        var keys = _server.Keys();
        foreach (var key in keys)
        {
            var value = _db.StringGet(key);
            pairs.Add(new Pair(key, value));
        }

        return JsonSerializer.Serialize(pairs);        
    }

}