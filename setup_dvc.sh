
#!/bin/bash

# Initialize DVC in the project
dvc init

# Set up a remote on Minio
dvc remote add -d minio_remote s3://ml-dvc-storage
dvc remote modify minio_remote endpointurl http://localhost:9000
dvc remote modify minio_remote access_key_id minioadmin
dvc remote modify minio_remote secret_access_key minioadmin

echo "DVC has been configured with Minio remote."
