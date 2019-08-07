from polecat import model
from polecat.project import Project

from .models import *  # noqa


class DefaultRole(model.Role):
    pass


class ExampleProject(Project):
    default_role = DefaultRole
