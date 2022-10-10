from django.db import models
from django.contrib.postgres.fields import ArrayField


class Collection(models.Model):
    field_id = models.SlugField(max_length=200, blank=False, null=False, unique=True)

    def __str__(self):
        return self.field_id


class CollectionItem(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    item_id = models.IntegerField(blank=False, null=False)

    def __str__(self):
        return str(self.item_id)


class Message(models.Model):
    message = models.CharField(max_length=200, blank=False, null=False)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)

    def __str__(self):
        return self.message

