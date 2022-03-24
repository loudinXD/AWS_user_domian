import boto3

access_key = "accesskey"
secret_key = "secretkey"
region = "ap-south-1"
ses = boto3.client(
    "ses",
    region_name=region,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
)
iam = boto3.client(
    "iam",
    region_name=region,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
)
s3 = boto3.client(
    "s3",
    region_name=region,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
)
route53 = boto3.client(
    "route53",
    region_name=region,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
)
sesv2 = boto3.client(
    "sesv2",
    region_name=region,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
)
