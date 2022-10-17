using Microsoft.Extensions.Options;
using MongoDB.Driver;
using System.Collections.Generic;
using System.Threading.Tasks;
using testservice.Models;

namespace testservice.Services;

public class TestCasesService
{
    private readonly IMongoCollection<TestCase> _testCases;

    public TestCasesService(IOptions<DatabaseSettings> databaseSettings)
    {
        var mongoClient = new MongoClient(
            databaseSettings.Value.ConnectionString);

        var mongoDatabase = mongoClient.GetDatabase(
            databaseSettings.Value.DatabaseName);

        _testCases = mongoDatabase.GetCollection<TestCase>("testCases");
    }

    public async Task<List<TestCase>> GetAsync(int count) =>
        await _testCases.Find(_ => true).SortByDescending(x => x.CreatedAt).Limit(count).ToListAsync();

    public async Task<List<TestCase>> GetForTaskAsync(string taskId, int count) =>
        await _testCases.Find(x => x.TaskId == taskId).SortByDescending(x => x.CreatedAt).Limit(count).ToListAsync();

    public async Task<TestCase> GetAsync(string id) =>
        await _testCases.Find(x => x.Id == id).SingleAsync();

    public async Task CreateAsync(TestCase newTestCase) =>
        await _testCases.InsertOneAsync(newTestCase);
}
