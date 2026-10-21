from django.urls import path

from .views import (
    ChaletModelDetailView,
    ChaletModelListView,
    OptionListView,
    TerrainListView,
)

urlpatterns = [
    path('models/', ChaletModelListView.as_view(), name='model-list'),
    path('models/<slug:slug>/', ChaletModelDetailView.as_view(), name='model-detail'),
    path('terrains/', TerrainListView.as_view(), name='terrain-list'),
    path('options/', OptionListView.as_view(), name='option-list'),
]
