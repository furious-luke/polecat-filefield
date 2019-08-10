from polecat.model.field import TextField

# from .builders import build_upload_mutation
from .hooks import add_upload_mutation
from .resolvers import MutationResolver, QueryResolver


class FileField(TextField):
    query_resolvers = QueryResolver()
    mutation_resolvers = MutationResolver()
    hooks = [add_upload_mutation]

    def __init__(self, *args, upload_resolvers=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.upload_resolvers = upload_resolvers
