using System;
using System.ComponentModel.DataAnnotations;
using System.Text.Json.Serialization;
using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;


namespace submissions.Models;

public class Submission
{
    [BsonId]
    [BsonRepresentation(BsonType.ObjectId)]
    public string Id { get; set; }

    [Required]
    [BsonRepresentation(BsonType.ObjectId)]
    public string TaskId { get; set; }

    [Required]
    public string UserEmail { get; set; }

    [Required]
    public string TaskName { get; set; }

    // Name is combination of task name and submission date
    public string Name {
        get => _name ?? $"{TaskName} on {SubmittedOn}";
        set => _name = value;
    }

    public System.DateTime SubmittedOn { get; set; } = DateTime.UtcNow;

    [BsonIgnore]
    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public string Content { get; set; }

    private string _name = null;
}
