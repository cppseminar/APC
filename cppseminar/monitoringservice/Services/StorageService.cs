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

    public async Task setPairAsync(Pair pair)
    {
        await _db.StringSetAsync(pair.Key, pair.Value);
    }

    public async Task<string?> getValueAsync(string Key)
    {
        string value = await _db.StringGetAsync(Key);
        return value;
    }

/* This works only when key-value pairs are in redis */
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

    public async Task appendListPairAsync(Pair pair)
    {
        // Appending items to the list
        await _db.ListRightPushAsync(pair.Key, pair.Value);

        // var last = await _db.ListGetByIndexAsync(pair.Key, -1);
        // Console.WriteLine($"Last item: {last}");
    }

    public async Task<string> getEveryListJsonAsync()
    {
        var output = new List<List<string?>>();
        var keys = _server.Keys();
        foreach (var key in keys)
        {
            var list = new List<string?>();
            list.Add(key); // 1st item is always the key

            // Retrieving all items from the list
            var items = await _db.ListRangeAsync(key);
            foreach (var item in items)
            {
                list.Add(item);
            }

            output.Add(list);
        }

        return JsonSerializer.Serialize(output);
    }
}