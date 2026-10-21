from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient

from .models import ChaletModel, Option, Terrain


class CatalogApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_catalog', verbosity=0)

    def setUp(self):
        self.client = APIClient()

    def test_catalog_collections_match_seed(self):
        self.assertEqual(ChaletModel.objects.count(), 3)
        self.assertEqual(Terrain.objects.count(), 4)
        self.assertEqual(Option.objects.count(), 12)

    def test_terrain_endpoint_returns_frontend_shape(self):
        response = self.client.get('/api/catalog/terrains/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]['id'], 'ain-draham')
        self.assertIn('surfaceArea', response.json()[0])

    def test_all_catalog_collections_are_available(self):
        for resource in ('models', 'options', 'terrains'):
            with self.subTest(resource=resource):
                response = self.client.get(f'/api/catalog/{resource}/')
                self.assertEqual(response.status_code, 200)
