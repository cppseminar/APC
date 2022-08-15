using Azure.Storage.Blobs;
using Azure.Storage.Blobs.Models;

namespace mqreadservice
{
    public static class BlobStorage
    {
        public static string DownloadBlob(string? blobSasUrl)
        {
            _ = blobSasUrl ?? throw new ArgumentNullException(nameof(blobSasUrl));

            BlobClient blobClient = new BlobClient(new Uri(blobSasUrl), null);

            BlobDownloadResult blobDownloadResult = blobClient.DownloadContent();

            var downloadedData = blobDownloadResult.Content.ToString();

            return downloadedData;
        }
    }
}
