from polecat.model.field import TextField

# from .builders import build_upload_mutation
from .hooks import add_upload_mutation
from .resolvers import MutationResolver, QueryResolver


class FileField(TextField):
    query_resolver = QueryResolver
    mutation_resolver = MutationResolver
    hooks = [add_upload_mutation]

    def __init__(self, *args, upload_resolver=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.upload_resolver = upload_resolver
