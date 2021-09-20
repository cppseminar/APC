using System;
using System.Linq;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using Azure.Storage.Blobs;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace submissions.Services
{
    public class StorageService
    {
        private const string _containerName = "submissions";
        private BlobServiceClient _client = null;
        private ILogger<StorageService> _logger;

        public StorageService(IConfiguration config, ILogger<StorageService> logger)
        {
            _client = new BlobServiceClient(config["StorageConnectionString"]);
            _logger = logger;
            // We can afford calling create here, because this service has big lifetime
            // TODO: Check CloudBlobContainer - it has createifnotexists
            try
            {
                _client.CreateBlobContainer(_containerName);
            }
            catch (Azure.RequestFailedException)
            {
                // Ignore that container already exists
            }

        }

        // Accepts only name normalized by NormalizeFileName
        public async Task UploadBlobAsync(List<string> path, BinaryData data)
        {
            if (!CheckPathParam(path))
            {
                _logger.LogError("Invalid path to upload blob {path}", path);
                throw new ArgumentException($"Invalid path for blob");
            }
            
            string blobName = string.Join('/', path);
            var blobClient = _client.GetBlobContainerClient(_containerName);
            await blobClient.UploadBlobAsync(blobName, data);
        }

        // Path must be normalized by NormalizeFileName
        public async Task<BinaryData> DownloadBlobAsync(List<string> path)
        {
            if (!CheckPathParam(path))
            {
                _logger.LogError("Invalid path to download blob {path}", path);
                throw new ArgumentException($"Invalid path for blob");
            }

            try
            {
                string blobName = string.Join("/", path);
                _logger.LogTrace("Downloading blob {path}", blobName);
                var blobClient = _client.GetBlobContainerClient(_containerName);
                var response = await blobClient.GetBlobClient(blobName).DownloadContentAsync();
                int responseStatus = response.GetRawResponse().Status;
                if (responseStatus > 299)
                {
                    _logger.LogError("Azure blob download returned response {code} ", responseStatus);
                    throw new Exception("Bad response code, check logs");
                }
                _logger.LogTrace("Downloaded successfuly");
                return response.Value.Content;
            }
            catch(Exception e)
            {
                _logger.LogError("Error during blob donwload {e}", e);
                throw new ApplicationException("Operation failed");
            }
        }

        private bool CheckPathParam(List<string> path)
        {
            var invalidNames = path.FindAll(path => path != NormalizeFileName(path));
            if (invalidNames.Count > 0)
            {
                return false;
            }
            if (path.Count == 0)
            {
                return false;
            }
            if (path.FindAll(path => string.IsNullOrEmpty(path)).Count > 0)
            {
                return false;
            }
            return true;
        }

        public static string NormalizeFileName(string name)
        {
            string newName = Regex.Replace(name, @"[^a-zA-Z0-9@\-\.]", "");
            // We don't want files to start/end with . or even -
            return newName.Trim(new[] { '.', '-' });
        }

    }
}
