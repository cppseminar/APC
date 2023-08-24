using System;
using System.Text.Json.Serialization;
using presentation.Converters;

namespace presentation.Model;

public class ConnectionLogRest
{
    public string UserEmail { get; set; }
    [JsonPropertyName("Timestamp")]
    [JsonConverter(typeof(DateTimeDifferenceConverter))]
    public string Seconds { get; set; }
    
}