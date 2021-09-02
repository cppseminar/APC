using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using Azure.Storage.Blobs;
using Microsoft.Extensions.Configuration;

namespace submissions.Services
{
    public class StorageService
    {
        private const string _containerName = "submissions";
        private BlobServiceClient _client = null;
        public StorageService(IConfiguration config)
        {
            _client = new BlobServiceClient(config["StorageConnectionString"]);
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
            var invalidNames = path.FindAll(path => path != StorageService.NormalizeFileName(path));
            if (invalidNames.Count > 0)
            {
                throw new ArgumentException($"Invalid file nam {invalidNames[0]}");
            }
            if (path.Count == 0)
            {
                throw new ArgumentException("Blob path cannot be empty");
            }
            if (path.FindAll(path => string.IsNullOrEmpty(path)).Count > 0)
            {
                throw new ArgumentException("Path cannot contain empty strings.");
            }
            string blobName = string.Join('/', path);
            var blobClient = _client.GetBlobContainerClient(_containerName);
            await blobClient.UploadBlobAsync(blobName, data);
        }

        public static string NormalizeFileName(string name)
        {
            string newName = Regex.Replace(name, @"[^a-zA-Z0-9@\-\.]", "");
            // We don't want files to start/end with . or even -
            return newName.Trim(new[] { '.', '-' });
        }

    }
}
