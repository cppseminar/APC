using Azure.Storage.Blobs;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using System;
using System.Threading.Tasks;
using System.Web;

namespace testservice.Services;

public class StorageService
{
    private readonly BlobServiceClient _client;
    private readonly ILogger<StorageService> _logger;
    private readonly BlobContainerClient _containerClient;
    private const string _containerName = "testresults";

    public StorageService(IConfiguration config, ILogger<StorageService> logger)
    {
        _client = new BlobServiceClient(config["BLOB_STORAGE_CONNECTION"]);
        _logger = logger;
        // We can afford calling create here, because this service has big lifetime
        try
        {
            _logger.LogTrace("Creating azure storage container {cont}", _containerName);

            _client.CreateBlobContainer(_containerName);
        }
        catch (Azure.RequestFailedException)
        {
            // Ignore that container already exists
            _logger.LogInformation("Azure storage container {cont} already exists", _containerName);
        }
        _containerClient = _client.GetBlobContainerClient(_containerName);
    }

    public async Task<byte[]> DownloadResultAsync(string blobName)
    {
        var blobClient = _containerClient.GetBlobClient(blobName);
        return (await blobClient.DownloadContentAsync()).Value.Content.ToMemory().ToArray();
    }

    public string CreateName(string testId, string userEmail, string fileName)
    {
        return HttpUtility.UrlEncode(userEmail) + "/"
            + HttpUtility.UrlEncode(testId) + "/"
            + HttpUtility.UrlEncode(fileName);
    }

    public async Task UploadResultAsync(string blobName, byte[] data)
    {
        var blobClient = _containerClient.GetBlobClient(blobName);
        await blobClient.UploadAsync(BinaryData.FromBytes(data), overwrite: true);
    }
}
