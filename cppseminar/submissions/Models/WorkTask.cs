using System;
using System.ComponentModel.DataAnnotations;
using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;

namespace submissions.Models;

public class WorkTask
{
    [BsonId]
    [BsonRepresentation(BsonType.ObjectId)]
    public string Id { get; set; }

    [Required]
    public string Name { get; set; }

    public string ClaimName { get; set; }

    public string ClaimValue { get; set; }

    [Required]
    public string Description { get; set; }

    [Required]
    public string CreatedBy { get; set; }

    public DateTime CreatedOn { get; set; } = DateTime.UtcNow;

    public DateTime Ends
    {
        get => ends ?? new DateTime(CreatedOn.Year + 1, CreatedOn.Month, CreatedOn.Day);
        set => ends = value;
    }
    private DateTime? ends = null;
}
