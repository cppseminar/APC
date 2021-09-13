using Microsoft.EntityFrameworkCore;
using submissions.Models;

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
            modelBuilder.Entity<Submission>().Property(x => x.Id).ToJsonProperty("id");
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
