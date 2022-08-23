using System.Text.Json;

namespace testservice.Models;

public class TestRequestMessage
{
    public string ToJson()
    {
        return JsonSerializer.Serialize(this, new JsonSerializerOptions { PropertyNamingPolicy = JsonNamingPolicy.CamelCase });
    }

    public string DockerImage { get; set; }
    public string ContentUrl { get; set; }
    public string MetaData { get; set; }
}
