using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.Azure.Cosmos.Table;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using userservice.Models;

namespace userservice.Services
{
    public class UserDbService
    {
        private ILogger<UserDbService> _logger;
        private CloudTable _table;
        private const string _isAdminConst = "isAdmin";

        public UserDbService(ILogger<UserDbService> logger, IConfiguration config)
        {
            _logger = logger;
            string connectionString = config["TABLE_STORAGE"];
            CloudTableClient cloudTableClient = CloudStorageAccount.Parse(connectionString)
                                                                   .CreateCloudTableClient(new TableClientConfiguration());
            _table = cloudTableClient.GetTableReference("usersTable");
            _logger.LogInformation("Creating users table");
            _table.CreateIfNotExists();
            _logger.LogInformation("Created users table");
        }

        // There is no API to get all distinct partition keys, which is what we would
        // need, so we query for isAdmin claim instead. In other words, if there is
        // ever user which doesn't have isAdmin claim set (either true or false),
        // then we won't list him.  This app will never create such user, so we
        // are safe, as long as all requests to Tables are done ONLY through this
        // service.
        public async Task<IEnumerable<string>> GetAllUsersAsync()
        {
            string filterExpr = TableQuery.GenerateFilterCondition(nameof(UserRow.RowKey), QueryComparisons.Equal, "isAdmin");
            var query = new TableQuery<UserRow>().Where(filterExpr);
            // This will return only first batch, but it should be enough
            var results = await _table.ExecuteQuerySegmentedAsync(query, null);
            return from x in results.Results select x.UserEmail;
        }

        public async Task<UserModel> GetUserAync(string userEmail)
        {
            string filterExpr = TableQuery.GenerateFilterCondition(nameof(UserRow.PartitionKey), QueryComparisons.Equal, userEmail);
            var query = new TableQuery<UserRow>().Where(filterExpr);
            Dictionary<string, string> claims = new Dictionary<string, string>();
            foreach (UserRow row in await _table.ExecuteQuerySegmentedAsync(query, null))
            {
                if (row.ClaimValue == null)
                {
                    // This shouldn't happen, unless someone edited it by hand
                    _logger.LogWarning("Users table contains row without claim value for {userEmail}", userEmail);
                    continue;
                }
                claims.Add(row.ClaimType, row.ClaimValue);
            }
            return new UserModel()
            {
                UserEmail = userEmail,
                Claims = claims
            };
        }

        public async Task UpdateListOfStudents(List<UserModel> listOfStudents)
        {
            try
            {
                for (int i = 0; i < listOfStudents.Count; i++)
                {
                    var student = new UserRow();

                    student.PartitionKey = listOfStudents[i].UserEmail;
                    student.RowKey = (listOfStudents[i].Claims.ToArray())[0].Key;
                    student.ClaimValue = (listOfStudents[i].Claims.ToArray())[0].Value;

                    await _table.ExecuteAsync(TableOperation.InsertOrReplace(student));
                }

                _logger.LogInformation("List of students was successfully updated.");
            }
            catch (Exception e)
            {
                _logger.LogError("List of students update failed. {e}", e);
            }
        }
    }
}
