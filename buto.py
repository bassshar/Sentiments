import boto3

# Specify your access key and secret key
access_key = 'access key ID'
secret_key = 'secret key ID'

# Create an S3 client with your credentials
s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)

# Rest of the code remains the same
bucket_name = 'enter bucket name'
object_key = 'audios/abc.wav'
local_file_path = 'enter local path'

s3.upload_file(local_file_path, bucket_name, object_key)

print('Object uploaded successfully!')
