using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using testservice.Models;
namespace testservice.Services
{
    public sealed class DbService: DbContext
    {
        public DbService(DbContextOptions<DbService> options)
            :base(options)
        {
        }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<TestCase>()
                .ToContainer(DbConstants.TestCaseCollection)
                .HasNoDiscriminator()
                .HasPartitionKey(x => x.TaskId); // This partition key is just to have smth

            modelBuilder.Entity<TestCase>()
                .Property(testCase => testCase.Id).ToJsonProperty("id");

            modelBuilder.Entity<TestRun>()
                .ToContainer(DbConstants.TestRunCollection)
                .HasNoDiscriminator()
                .HasPartitionKey(x => x.CreatedBy);
            modelBuilder.Entity<TestRun>()
                .Property(req => req.Id).ToJsonProperty("id");

        }
        public DbSet<TestCase> Cases { get; set; }
        public DbSet<TestRun> Tests { get; set; }
    }

    public class DbConstants
    {
        public const string TestCaseCollection = "testCases";
        public const string TestRunCollection = "testRuns";
    }
}
