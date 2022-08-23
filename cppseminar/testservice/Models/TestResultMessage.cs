using System;
using System.Text.Json.Serialization;

namespace testservice.Models;

public class TestResultMessage
{
    [JsonConstructor]
    public TestResultMessage(string MetaData, string Students, string Teachers, string Data)
    {
        this.MetaData = MetaData ?? throw new ArgumentNullException(nameof(MetaData));
        this.Students = Students ?? throw new ArgumentNullException(nameof(Students));
        this.Teachers = Teachers ?? throw new ArgumentNullException(nameof(Teachers));
        this.Data = Data ?? throw new ArgumentNullException(nameof(Data));
    }
    public string MetaData { get; set; }
    // Link to json with stripped down content for students
    public string Students { get; set; }
    // Link to json with full content for teachers
    public string Teachers { get; set; }
    // Link to zip with dumped debug data
    public string Data { get; set; }
}
