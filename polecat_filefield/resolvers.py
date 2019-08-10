from pathlib import Path

import boto3
from polecat.core.config import default_config
from polecat.model.db import Q
from polecat.utils import retry

from .models import Tmpfile
from .utils import (destination_path_from_filename, remove_leading_slash,
                    temporary_path_from_file_id)


def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=default_config.filefield.aws_access_key_id,
        aws_secret_access_key=default_config.filefield.aws_secret_access_key,
        region_name=default_config.filefield.aws_default_region
    )


class Resolver:
    def __init__(self, expiry=None):
        self._expiry = expiry

    @property
    def expiry(self):
        if self._expiry is None:
            self._expiry = default_config.filefield.query_expiry
        return self._expiry


class QueryResolver(Resolver):
    def __call__(self, context, model, field, field_name):
        filename = model.get(field_name)
        if not filename:
            return None
        s3 = get_s3_client()
        path = destination_path_from_filename(filename)
        path = remove_leading_slash(path)
        model[field_name] = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': default_config.filefield.aws_bucket,
                'Key': path
            },
            ExpiresIn=self.expiry
        )


class MutationResolver(Resolver):
    def __init__(self, prefix=None, expiry=None):
        super().__init__(expiry=expiry)
        self.prefix = prefix

    def __call__(self, context, model, field, field_name):
        file_id = getattr(model, field_name)
        bucket = default_config.filefield.aws_bucket
        tmpfile_query = (
            Q(Tmpfile)
            .filter(key=file_id)
        )
        try:
            filename = (
                tmpfile_query
                .select('filename')
                .get()
            )['filename']
        except TypeError:
            # TODO: Better error.
            raise Exception('Invalid file ID')
        if self.prefix:
            filename = str(Path(self.prefix)/filename)
        dst_path = destination_path_from_filename(filename)
        dst_path = remove_leading_slash(dst_path)
        tmp_path = temporary_path_from_file_id(file_id)
        tmp_path = remove_leading_slash(tmp_path)
        s3 = get_s3_client()
        self.copy_file(s3, bucket, tmp_path, dst_path)
        self.delete_tmpfile(s3, bucket, tmp_path, tmpfile_query)
        setattr(model, field_name, filename)

    @retry
    def copy_file(self, s3, bucket, tmp_path, dst_path):
        s3.copy_object(
            CopySource={
                'Bucket': bucket,
                'Key': tmp_path
            },
            Bucket=bucket,
            Key=dst_path
        )

    @retry(swallow_error=True)
    def delete_tmpfile(self, s3, bucket, tmp_path, tmpfile_query):
        s3.delete_object(
            Bucket=bucket,
            Key=tmp_path
        )
        tmpfile_query.delete().execute()


def upload_resolver(mutation, context):
    input = context.parse_input()
    file_id = (
        Q(Tmpfile)
        .insert(filename=input['filename'])
        .select('key')
        .get()
    )['key']
    tmp_path = temporary_path_from_file_id(file_id)
    tmp_path = remove_leading_slash(tmp_path)
    s3 = get_s3_client()
    bucket = default_config.filefield.aws_bucket
    params = {
        'Bucket': bucket,
        'Key': tmp_path,
        # 'ACL': 'bucket-owner-full-control'
    }
    expiry = default_config.filefield.upload_expiry
    presigned_url = s3.generate_presigned_url(
        'put_object',
        Params=params,
        ExpiresIn=expiry
    )
    return {
        'file_id': file_id,
        'presigned_url': presigned_url
    }
