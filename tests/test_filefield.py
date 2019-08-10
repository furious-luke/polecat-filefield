from contextlib import contextmanager
from unittest.mock import patch
from uuid import uuid4

import pytest
from polecat.model import Model
from polecat.model.db import Q
from polecat.model.db.migrate import sync
from polecat.test import fixture
from polecat_filefield import FileField
from polecat_filefield.models import Tmpfile


def build_test_model():
    class TestModel(Model):
        file = FileField()
    return TestModel


@contextmanager
def filefield_config():
    with fixture.config(
            filefield__aws_access_key_id='test',
            filefield__aws_secret_access_key='test',
            filefield__aws_default_region='test',
            filefield__aws_bucket='test',
            filefield__query_expiry='60s',
            filefield__upload_expiry='60s'
    ):
        yield


def test_upload(db, push_blueprint):
    build_test_model()
    with fixture.server() as server:
        with filefield_config():
            result = server.mutation('UploadTestModelFile', filename='a.txt')
    assert result['file_id'] is not None
    assert result['presigned_url'] is not None


def test_mutation_without_tmpfile(testdb, push_blueprint):
    TestModel = build_test_model()
    with fixture.server() as server:
        sync()
        with filefield_config():
            with pytest.raises(Exception, match=r'Invalid file ID'):
                server.create_mutation(TestModel, {'file': str(uuid4())})


def test_mutation(testdb, push_blueprint):
    with patch('polecat_filefield.resolvers.get_s3_client') as mocked_s3_client:
        TestModel = build_test_model()
        with fixture.server() as server:
            sync()
            key = str(uuid4())
            Q(Tmpfile).insert(key=key, filename='a.txt').execute()
            with filefield_config():
                server.create_mutation(TestModel, {'file': key})
        # TODO: I can check the arguments here.
        assert len(mocked_s3_client.mock_calls) == 3


def test_query(testdb, push_blueprint):
    with patch('polecat_filefield.resolvers.get_s3_client') as mocked_s3_client:
        TestModel = build_test_model()
        with fixture.server() as server:
            sync()
            key = str(uuid4())
            Q(Tmpfile).insert(key=key, filename='a.txt').execute()
            with filefield_config():
                server.create_mutation(TestModel, {'file': key})
            result = Q(TestModel).select('file').get()
            assert result['file'] == 'a.txt'
            with filefield_config():
                results = server.all_query(TestModel)
                # TODO: Test the input to the magicmock.
                assert results[0]['file'] is not None
                assert results[0]['file'] != 'a.txt'
