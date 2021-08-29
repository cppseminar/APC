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
            // TODO: HasNoDiscriminator
        }

        public DbSet<Submission> Submissions { get; set; }
    }
}
