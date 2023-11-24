using MongoDB.Bson;
using MongoDB.Bson.Serialization.Attributes;
using System;
using System.ComponentModel.DataAnnotations;
using System.Text.Json.Serialization;

namespace testservice.Models;

public enum TestStatus
{
    Requested,
    Failed,
    Finished,
}

public class TestRun
{
    [BsonId]
    [BsonRepresentation(BsonType.ObjectId)]
    public string Id { get; set; }

    [Required]
    [BsonRepresentation(BsonType.ObjectId)]
    public string TaskId { get; set; }

    [Required]
    [BsonRepresentation(BsonType.ObjectId)]
    public string SubmissionId { get; set; }

    [Required]
    [BsonRepresentation(BsonType.ObjectId)]
    public string TestCaseId { get; set; }

    [Required]
    public string CreatedBy { get; set; }

    [Required]
    public string TaskName { get; set; }

    [Required]
    public string TestCaseName { get; set; }

    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    public DateTime? FinishedAt { get; set; }

    [JsonConverter(typeof(JsonStringEnumConverter))]
    [BsonRepresentation(BsonType.String)]
    public TestStatus Status { get; set; } = TestStatus.Requested;

    [Required]
    public bool Counted { get; set; }

    public string Message { get; set; } = "Test will start shortly."
        + " If you don't see results in few hours, please contact your teacher";

    public string Name
    {
        get => _name ?? $"Test run for {SubmissionId}";
        set => _name = value;
    }

    [Required]
    public string ContentUrl { get; set; }

    [BsonIgnore]
    public string Students { get; set; }

    [BsonIgnore]
    public string Teachers { get; set; }

    private string _name;
}

public class TestRunPatch
{
    [Required]
    public bool Counted { get; set; }
}

public class TestRunConstants
{
    public const string TestMessageFinished = "All tests finished successfully";
    public const string TestMessageFailed = "Something went wrong. Please contact your teacher.";
    public const string FileStudents = "students.json";
    public const string FileTeachers = "teachers.json";
    public const string FileZip = "dump.zip";
}
