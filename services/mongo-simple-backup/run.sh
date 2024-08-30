#!/bin/sh

/tools/backup.sh --url ${MONGO_CONN_STR} --output /var/dumps

if [ $? -ne 0 ]; then
    echo "Failed to backup MongoDB."
    exit 1
fi

for FILE in /var/dumps/*; do
    FILENAME=$(basename "$FILE")
    # Get SAS URL for the Azure Blob Storage
    # This is required, because rclone for some reason does not support Azure Blob Storage connection strings
    # ideally this would be in some another vm with managed identity to access the blob storage, so no 
    # connection string is needed and it will work flawalessly even if keys are rotated, for now it is here
    # as python script that generates SAS URL
    SAS_URL=$(python3 /tools/get-sas-url.py mongo-db-dumps "$FILENAME")
    if [ $? -ne 0 ]; then
        echo "Failed to generate SAS URL for $FILE."
    fi
    
    curl --fail-with-body -X PUT -T "$FILE" -H "x-ms-blob-type: BlockBlob" "$SAS_URL"
    if [ $? -ne 0 ]; then
        echo "Failed to upload $FILE to Azure Blob Storage."
    else
        echo "Uploaded $FILE to Azure Blob Storage."
        rm $FILE
    fi
done

# if some files are left, exit with error
if [ "$(ls -A /var/dumps)" ]; then
    echo "Some files were not uploaded to Azure Blob Storage."
    exit 1
fi