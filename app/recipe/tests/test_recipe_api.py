
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status, test
from core.models import Recipe

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_url):
    return reverse('recipe:recipe-detail', args=[recipe_url])


def create_recipe(user, **params):
    defaults = {
        'title': 'Sample Recipe',
        'price': Decimal('5.50'),
        'time_minutes': 10,
        'description': 'Sample Description',
        'link': 'http://www.sample.com/recipe.pdf'
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicRecipeAPITests(TestCase):

    def setUp(self):
        self.client = test.APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):

    def setUp(self):
        self.client = test.APIClient()

        self.user = create_user(
            email='user@example.com',
            password='pass123'
        )

        self.client.force_authenticate(self.user)

    def test_get_recipe_list(self):
        """Test getting a list of recipes"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 2)

    def test_recupe_list_limited_to_user(self):
        """Test that recipes returned are for the authenticated user"""
        user2 = create_user(
            email='example2@example.com',
            password='pass123'
        )
        create_recipe(user=user2)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user).order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_recipe(self):
        payload = {
            'title': 'Sample Recipe',
            'price': '5.50',
            'time_minutes': 10,
            'description': 'Sample Description',
            'link': 'http://www.sample.com/recipe.pdf'
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        original_link = 'http://www.sample.com/recipe.pdf'

        recipe = create_recipe(
            user=self.user, link=original_link, title='original title')

        payload = {
            'title': 'New Title',
            'link': 'http://www.sample.com/new_recipe.pdf'
        }

        url = detail_url(recipe.id)

        res = self.client.patch(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], recipe.title)
        self.assertEqual(res.data['link'], recipe.link)
