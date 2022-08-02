using System.Text.Json.Serialization;

namespace mqreadservice.Models
{
    public class TestRun
    {
        public string? returnUrl { get; set; }
        public string? metaData { get; set; }
        public string? dockerImage { get; set; }
        public Files files { get; set; }

        public TestRun()
        {
            returnUrl = null;
            metaData = null;
            dockerImage = null;

            files = new Files();
            files.maincpp = null;
        }
    }

    public class Files
    {
        [JsonPropertyName("main.cpp")]
        public string? maincpp { get; set; }
    }
}
