using Microsoft.EntityFrameworkCore;
using submissions.Models;

namespace submissions.Data
{
    public sealed class SubmissionContext : DbContext
    {

        public SubmissionContext(DbContextOptions<SubmissionContext> options)
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
