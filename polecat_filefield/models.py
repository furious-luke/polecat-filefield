from polecat import model
from polecat.model import omit

__all__ = ('Tmpfile',)


class Tmpfile(model.Model):
    key = model.UUIDField(unique=True, default=model.Auto)
    filename = model.TextField(null=False)
    initiated = model.DatetimeField(default=model.Auto)

    class Meta:
        omit = omit.ALL
