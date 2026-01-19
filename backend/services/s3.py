import boto3
import os
from botocore.exceptions import NoCredentialsError

class S3Service:
    def __init__(self):
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "wardrobe-ingestion-bucket")
        self.region = os.getenv("AWS_REGION", "us-east-1")
        # If no creds, boto3 looks for env vars or config file automatically
        self.s3 = boto3.client('s3', region_name=self.region)

    def upload_file(self, file_obj, object_name):
        """Upload a file-like object to S3."""
        try:
            self.s3.upload_fileobj(file_obj, self.bucket_name, object_name)
            url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{object_name}"
            return url
        except NoCredentialsError:
            print("Credentials not available")
            return None
        except Exception as e:
            print(f"Error uploading to S3: {e}")
            return None

s3_service = S3Service()
