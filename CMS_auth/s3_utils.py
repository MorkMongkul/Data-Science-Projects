import os
import boto3
from botocore.exceptions import ClientError
from werkzeug.utils import secure_filename
from flask import current_app

class S3Handler:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'eu-north-1')
        )
        self.bucket_name = os.getenv('AWS_BUCKET_NAME')

    def upload_file(self, file, folder=''):
        """
        Upload a file to S3 bucket
        """
        try:
            # Secure the filename
            filename = secure_filename(file.filename)
            
            # Create a unique filename with folder structure
            if folder:
                s3_path = f"{folder}/{filename}"
            else:
                s3_path = filename

            # Upload the file
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                s3_path,
                ExtraArgs={
                    'ContentType': file.content_type
                }
            )

            # Generate the URL
            url = f"https://{self.bucket_name}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{s3_path}"
            return url

        except ClientError as e:
            current_app.logger.error(f"Error uploading file to S3: {str(e)}")
            return None

    def delete_file(self, file_url):
        """
        Delete a file from S3 bucket
        """
        try:
            # Extract the key from the URL
            key = file_url.split(f"https://{self.bucket_name}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/")[1]
            
            # Delete the file
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True
        except ClientError as e:
            current_app.logger.error(f"Error deleting file from S3: {str(e)}")
            return False 