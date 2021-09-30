using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace testservice.Models
{

    public class TestRequestMessage
    {
        public string ToJson()
        {
            return JsonSerializer.Serialize(
                this, new() { PropertyNamingPolicy = JsonNamingPolicy.CamelCase });
        }
        public string DockerImage { get; set; }
        public string ContentUrl { get; set; }
        public string Metadata { get; set; }
    }
}
