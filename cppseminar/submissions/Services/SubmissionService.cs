using System.Threading.Tasks;
using System.Collections.Generic;
using Microsoft.Extensions.Options;
using MongoDB.Driver;
using MongoDB.Bson;

using submissions.Models;
using System.Linq;
using System;

namespace submissions.Services;

public class SubmissionsService
{
    private readonly IMongoCollection<Submission> _submissions;

    public SubmissionsService(IOptions<DatabaseSettings> databaseSettings)
    {
        var mongoClient = new MongoClient(
            databaseSettings.Value.ConnectionString);

        var mongoDatabase = mongoClient.GetDatabase(
            databaseSettings.Value.DatabaseName);

        _submissions = mongoDatabase.GetCollection<Submission>("submissions");
    }

    public async Task<List<Submission>> GetAsync(int count) =>
        await _submissions.Find(_ => true).SortByDescending(x => x.SubmittedOn).Limit(count).ToListAsync();

    public async Task<List<Submission>> GetForUserAsync(string email, string taskId, int count)
    {
        var filter = Builders<Submission>.Filter.Eq(x => x.UserEmail, email);

        if (taskId != null)
            filter &= Builders<Submission>.Filter.Eq("TaskId", ObjectId.Parse(taskId));

        return await _submissions.Find(filter).SortByDescending(x => x.SubmittedOn).Limit(count).ToListAsync();
    }

    public async Task<Submission> GetAsync(string submissionId) =>
        await _submissions.Find(x => x.Id == submissionId).SingleAsync();

    public class GetForTaskItem
    {
        public string UserEmail { get; set; }
        public string SubmissionId { get; set; }
        public DateTime SubmittedOn { get; set; }
    }

    public async Task<List<GetForTaskItem>> GetForTask(string taskId) =>
        await _submissions.Aggregate()
            .Match(x => x.TaskId == taskId)
            .SortByDescending(x => x.SubmittedOn)
            .Group(x => x.UserEmail,
                g => new GetForTaskItem
                {
                    UserEmail = g.Key,
                    SubmissionId = g.First().Id,
                    SubmittedOn = g.First().SubmittedOn
                }
            )
            .ToListAsync();

    public async Task CreateAsync(Submission newSubmission) =>
        await _submissions.InsertOneAsync(newSubmission);

    public async Task RemoveAsync(string id) =>
        await _submissions.DeleteOneAsync(x => x.Id == id);
}
