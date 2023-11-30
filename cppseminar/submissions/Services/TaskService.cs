using System.Threading.Tasks;
using System.Collections.Generic;
using Microsoft.Extensions.Options;
using MongoDB.Driver;

using submissions.Models;
using MongoDB.Bson;

namespace submissions.Services;

public class TasksService
{
    private readonly IMongoCollection<WorkTask> _tasks;

    public TasksService(IOptions<DatabaseSettings> databaseSettings)
    {
        var mongoClient = new MongoClient(
            databaseSettings.Value.ConnectionString);

        var mongoDatabase = mongoClient.GetDatabase(
            databaseSettings.Value.DatabaseName);

        _tasks = mongoDatabase.GetCollection<WorkTask>("tasks");
    }

    public async Task<List<WorkTask>> GetAsync(int count) =>
        await _tasks.Find(_ => true).SortByDescending(x => x.CreatedOn).Limit(count).ToListAsync();

    public async Task<WorkTask> GetAsync(string id) =>
        await _tasks.Find(x => x.Id == id).SingleAsync();

    public async Task CreateAsync(WorkTask newTask) =>
        await _tasks.InsertOneAsync(newTask);

    // Returns updated WorkTask on success, null on not found.
    public async Task<WorkTask> PatchOneAsync(string taskId, BsonDocument update) =>
       await _tasks.FindOneAndUpdateAsync(
           x => x.Id == taskId,
           new BsonDocument { { "$set", update } },
           new() { IsUpsert = false, ReturnDocument = ReturnDocument.After });
}
