using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata;
using Microsoft.EntityFrameworkCore.Cosmos;
using submissions.Models;
using System;

namespace submissions.Data
{
    public sealed class CosmosContext : DbContext
    {

        public CosmosContext(DbContextOptions<CosmosContext> options)
        : base(options)
        {

        }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<Submission>().ToContainer("submissions");
            modelBuilder.Entity<Submission>().HasPartitionKey(s => s.UserEmail);
            modelBuilder.Entity<Submission>().HasNoDiscriminator();
            modelBuilder.Entity<WorkTask>()
                        .ToContainer("tasks")
                        .HasNoDiscriminator()
                        .HasPartitionKey(s => s.Name)
                        .Property(x => x.Id).ToJsonProperty("id");
        }

        public DbSet<Submission> Submissions { get; set; }
        public DbSet<WorkTask> Tasks { get; set; }
    }
}
