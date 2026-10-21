from rest_framework import generics
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .models import ChaletModel, Option, Terrain
from .serializers import (
    ChaletModelSerializer,
    OptionSerializer,
    TerrainSerializer,
)

catalog_cache = cache_page(settings.CACHE_TTL_SECONDS)


@method_decorator(catalog_cache, name='dispatch')
class ChaletModelListView(generics.ListAPIView):
    queryset = ChaletModel.objects.all()
    serializer_class = ChaletModelSerializer


@method_decorator(catalog_cache, name='dispatch')
class ChaletModelDetailView(generics.RetrieveAPIView):
    queryset = ChaletModel.objects.all()
    serializer_class = ChaletModelSerializer
    lookup_field = 'slug'


@method_decorator(catalog_cache, name='dispatch')
class TerrainListView(generics.ListAPIView):
    queryset = Terrain.objects.all()
    serializer_class = TerrainSerializer


@method_decorator(catalog_cache, name='dispatch')
class OptionListView(generics.ListAPIView):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
