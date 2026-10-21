from django.db import models


class ChaletModel(models.Model):
    slug = models.SlugField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    surface_area = models.PositiveIntegerField()
    surface_unit = models.CharField(max_length=10, default='m²')
    bedrooms = models.PositiveSmallIntegerField()
    bathrooms = models.PositiveSmallIntegerField()
    max_guests = models.PositiveSmallIntegerField()
    base_price = models.PositiveIntegerField()
    description = models.TextField()
    image = models.URLField(max_length=500)
    gallery = models.JSONField(default=list)
    features = models.JSONField(default=list)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Terrain(models.Model):
    slug = models.SlugField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100)
    region = models.CharField(max_length=150)
    country = models.CharField(max_length=100)
    description = models.TextField()
    surface_area = models.PositiveIntegerField()
    surface_unit = models.CharField(max_length=10, default='m²')
    base_price = models.PositiveIntegerField()
    image = models.URLField(max_length=500)
    gallery = models.JSONField(default=list)
    features = models.JSONField(default=list)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Option(models.Model):
    slug = models.SlugField(primary_key=True, max_length=100)
    name = models.CharField(max_length=150)
    short_description = models.TextField()
    description = models.TextField()
    price = models.PositiveIntegerField()
    image = models.URLField(max_length=500)
    popular = models.BooleanField(default=False)
    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name
