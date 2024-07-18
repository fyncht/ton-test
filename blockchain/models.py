from django.db import models


class Address(models.Model):
    address = models.CharField(max_length=255, unique=True)
    raw_data = models.BinaryField()
    status = models.IntegerField(default=0)
    code = models.BinaryField(null=True, blank=True)
    data = models.BinaryField(null=True, blank=True)
    status_updated_at = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return self.address
