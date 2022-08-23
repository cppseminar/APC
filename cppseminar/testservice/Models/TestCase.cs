using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;
using System;
using System.ComponentModel.DataAnnotations;

namespace testservice.Models;

public class TestCase
{
    [BsonId]
    [BsonRepresentation(BsonType.ObjectId)]
    public string Id { get; set; }

    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [Required]
    public string Name { get; set; }

    [Required]
    [BsonRepresentation(BsonType.ObjectId)]
    public string TaskId { get; set; }

    [Required]
    public string DockerImage { get; set; }

    [Required]
    public int MaxRuns { get; set; }

    [Required]
    public string ClaimName { get; set; }

    [Required]
    public string ClaimValue { get; set; }

    [Required]
    public string CreatedBy { get; set; }
}
