from pathlib import Path

import boto3
from polecat.core import active_config
from polecat.model.db import Q
from polecat.utils import retry

from .models import Tmpfile
from .utils import (destination_path_from_filename, remove_leading_slash,
                    temporary_path_from_file_id)


@active_config
def get_s3_client(config=None):
    return boto3.client(
        's3',
        aws_access_key_id=config.filefield.aws_access_key_id,
        aws_secret_access_key=config.filefield.aws_secret_access_key,
        region_name=config.filefield.aws_default_region
    )


class Resolver:
    def __init__(self, expiry=None):
        self.expiry = expiry
        if not self.expiry:
            with active_config() as config:
                self.expiry = config.filefield.query_expiry


class QueryResolver(Resolver):
    @active_config
    def resolve(self, model, field, field_name, config=None):
        filename = getattr(model, field_name, None)
        if not filename:
            return None
        s3 = get_s3_client()
        path = destination_path_from_filename(filename)
        path = remove_leading_slash(path)
        return s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': config.filefield.aws_bucket,
                'Key': path
            },
            ExpiresIn=self.expiry
        )


class MutationResolver(Resolver):
    def __init__(self, prefix=None, expiry=None):
        super().__init__(expiry=expiry)
        self.prefix = prefix

    @active_config
    def resolve(self, model, field, field_name, value, config=None):
        file_id = value
        bucket = config.filefield.aws_bucket,
        tmpfile_query = (
            Q(Tmpfile)
            .filter(uuid=file_id)
        )
        filename = (
            tmpfile_query
            .select('filename')
            .get()
        )['filename']
        if self.prefix:
            filename = str(Path(self.prefix)/filename)
        dst_path = destination_path_from_filename(filename)
        dst_path = remove_leading_slash(dst_path)
        tmp_path = temporary_path_from_file_id(file_id)
        tmp_path = remove_leading_slash(tmp_path)
        s3 = get_s3_client()
        with retry():
            s3.copy_object(
                CopySource={
                    'Bucket': bucket,
                    'Key': tmp_path
                },
                Bucket=bucket,
                Key=dst_path
            )
        with retry(swallow_error=True):
            s3.delete_object(
                Bucket=bucket,
                Key=tmp_path
            )
            tmpfile_query.delete().execute()
        return filename


@active_config
def upload_resolver(filename, config=None):
    file_id = Q(Tmpfile).insert(filename=filename)
    tmp_path = temporary_path_from_file_id(file_id)
    tmp_path = remove_leading_slash(tmp_path)
    s3 = get_s3_client()
    bucket = config.filefield.aws_bucket,
    params = {
        'Bucket': bucket,
        'Key': tmp_path,
        # 'ACL': 'bucket-owner-full-control'
    }
    expiry = config.filefield.upload_expiry
    presigned_url = s3.generate_presigned_url(
        'put_object',
        Params=params,
        ExpiresIn=expiry
    )
    return {
        'file_id': file_id,
        'presigned_url': presigned_url
    }
