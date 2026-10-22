from rest_framework import generics
from .models import ChaletModel, Option, Terrain
from .serializers import (
    ChaletModelSerializer,
    OptionSerializer,
    TerrainSerializer,
)

class ChaletModelListView(generics.ListAPIView):
    queryset = ChaletModel.objects.all()
    serializer_class = ChaletModelSerializer


class ChaletModelDetailView(generics.RetrieveAPIView):
    queryset = ChaletModel.objects.all()
    serializer_class = ChaletModelSerializer
    lookup_field = 'slug'


class TerrainListView(generics.ListAPIView):
    queryset = Terrain.objects.all()
    serializer_class = TerrainSerializer


class OptionListView(generics.ListAPIView):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
