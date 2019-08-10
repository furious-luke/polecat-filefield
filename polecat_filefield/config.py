from datetime import timedelta

from polecat.core.config import Config, auto_mount_config

__all__ = ('FileFieldConfig',)


@auto_mount_config('filefield')
class FileFieldConfig(Config):
    aws_access_key_id = str
    aws_secret_access_key = str
    aws_default_region = str
    aws_bucket = str
    query_expiry = timedelta
    upload_expiry = timedelta
