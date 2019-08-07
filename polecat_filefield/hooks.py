from polecat.model import TextField, UUIDField
from polecat.utils.stringcase import pascalcase

from .resolvers import upload_resolver


def add_upload_mutation(context):
    bp = context.blueprint
    upload_type = add_upload_type(bp)
    mutation_name = (
        'Upload' +
        context.model_class.Meta.name +
        pascalcase(context.field_name)
    )
    bp.create_mutation(mutation_name, upload_resolver, upload_type)


def add_upload_type(blueprint):
    type_name = 'UploadFile'
    if type_name not in blueprint.types:
        blueprint.create_type('UploadFile', fields={
            'file_id': UUIDField(),
            'presigned_url': TextField()
        })
    return blueprint.types[type_name]
