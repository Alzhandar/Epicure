from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False
    default_acl = 'public-read'
    custom_domain = f'{settings.AWS_STORAGE_BUCKET_NAME}.{settings.AWS_S3_REGION_NAME}.digitaloceanspaces.com'