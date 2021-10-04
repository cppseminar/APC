using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.Web;
using Azure.Storage.Blobs;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace testservice.Services
{
    public class StorageService
    {
        private BlobServiceClient _client;
        private ILogger<StorageService> _logger;
        private BlobContainerClient _containerClient;
        private const string _containerName = "testresults";

        public StorageService(IConfiguration config, ILogger<StorageService> logger)
        {
            _client = new BlobServiceClient(config["BLOB_STORAGE_CONNECTION"]);
            _logger = logger;
            // We can afford calling create here, because this service has big lifetime
            try
            {
                _client.CreateBlobContainer(_containerName);
            }
            catch (Azure.RequestFailedException e)
            {
                // Ignore that container already exists
            }
            _containerClient = _client.GetBlobContainerClient(_containerName);
        }

        public async Task UploadResult(string blobName, byte[] data)
        {
            var blobClient = _containerClient.GetBlobClient(blobName);
            await blobClient.UploadAsync(BinaryData.FromBytes(data), overwrite: true);
        }
    }
}
