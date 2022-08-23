using System.Threading.Tasks;
using System.Collections.Generic;
using Microsoft.Extensions.Options;
using MongoDB.Driver;

using userservice.Models;

namespace userservice.Services;

public class UsersService
{
    private readonly IMongoCollection<User> _users;

    public UsersService(IOptions<DatabaseSettings> databaseSettings)
    {
        var mongoClient = new MongoClient(
            databaseSettings.Value.ConnectionString);

        var mongoDatabase = mongoClient.GetDatabase(
            databaseSettings.Value.DatabaseName);

        _users = mongoDatabase.GetCollection<User>("users");
    }

    public async Task<List<User>> GetAsync() =>
        await _users.Find(_ => true).ToListAsync();

    public async Task<User> GetAsync(string userEmail) =>
        await _users.Find(x => x.UserEmail == userEmail).SingleAsync();

    public async Task CreateAsync(User user) =>
        await _users.InsertOneAsync(user);

    public async Task UpdateAsync(User user) =>
        await _users.ReplaceOneAsync(x => x.Id == user.Id, user);
}

