using System;
using System.Text.Json.Serialization;

namespace testservice.Models;

public class TestResultMessage
{
    // allow json deserialization
    public TestResultMessage()
    {
    }

    public void Validate()
    {
        if (!string.IsNullOrEmpty(Error))
        {
            return;
        }

        if (!string.IsNullOrEmpty(Teachers) 
            && !string.IsNullOrEmpty(Students)
            && !string.IsNullOrEmpty(Data))
        {
            return;
        }

        throw new ArgumentException("Either error or (students, teachers, data) must be set.");
    }

    [JsonPropertyName("metaData")]
    [JsonRequired] // we can use required keyword from C#11
    public string MetaData { get; set; }

    [JsonPropertyName("students")]
    public string Students { get; set; }

    [JsonPropertyName("teachers")]
    public string Teachers { get; set; }

    [JsonPropertyName("data")]
    public string Data { get; set; }

    [JsonPropertyName("error")]
    public string Error { get; set; }
}
