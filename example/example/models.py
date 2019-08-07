from polecat import model
from polecat_filefield import FileField


class TestModel(model.Model):
    file = FileField()
