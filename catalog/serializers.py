from rest_framework import serializers

from .models import ChaletModel, Option, Terrain
from .image_migration import resolve_gallery, resolve_image_url


class StorageImageMixin:
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['image'] = resolve_image_url(data['image'])
        data['gallery'] = resolve_gallery(data['gallery'])
        return data


class ChaletModelSerializer(StorageImageMixin, serializers.ModelSerializer):
    id = serializers.CharField(source='slug', read_only=True)
    surfaceArea = serializers.IntegerField(source='surface_area', read_only=True)
    surfaceUnit = serializers.CharField(source='surface_unit', read_only=True)
    basePrice = serializers.IntegerField(source='base_price', read_only=True)
    maxGuests = serializers.IntegerField(source='max_guests', read_only=True)

    class Meta:
        model = ChaletModel
        fields = ('id', 'name', 'subtitle', 'category', 'surfaceArea', 'surfaceUnit', 'bedrooms', 'bathrooms', 'maxGuests', 'basePrice', 'description', 'image', 'gallery', 'features')


class TerrainSerializer(StorageImageMixin, serializers.ModelSerializer):
    id = serializers.CharField(source='slug', read_only=True)
    surfaceArea = serializers.IntegerField(source='surface_area', read_only=True)
    surfaceUnit = serializers.CharField(source='surface_unit', read_only=True)
    basePrice = serializers.IntegerField(source='base_price', read_only=True)

    class Meta:
        model = Terrain
        fields = ('id', 'name', 'region', 'country', 'description', 'surfaceArea', 'surfaceUnit', 'basePrice', 'image', 'gallery', 'features')


class OptionSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='slug', read_only=True)
    shortDescription = serializers.CharField(source='short_description', read_only=True)

    class Meta:
        model = Option
        fields = ('id', 'name', 'shortDescription', 'description', 'price', 'image', 'popular')
