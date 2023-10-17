from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status, test
from core.models import Recipe, Tag
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email="example@example.com", password="test123"):
    return get_user_model().objects.create_user(email, password)


class PublicTagsAPITests(TestCase):

    def setUp(self):
        self.client = test.APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):

    def setUp(self):
        self.client = test.APIClient()

        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 2)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user"""
        user2 = create_user(email="example2@example.com")
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.filter(user=self.user).order_by('-name')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_patch_recipe_detail(self):
        tag = Tag.objects.create(user=self.user, name='After dinner')

        payload = {'name': 'Dessert'}
        url = detail_url(tag.id)
        res = self.client.patch(url)

        tag.refresh_from_db()

        serializer = TagSerializer(tag)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_tag(self):
        tag = Tag.objects.create(user=self.user, name='After dinner')
        url = detail_url(tag.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    # def test_get_recipe_detail(self):
    #     tag = Tag.objects.create(user=self.user, name='After dinner')
    #     url = detail_url(tag.id)
    #     res = self.client.get(url)
    #     serializer = TagSerializer(tag)
    #     self.assertEqual(res.data, serializer.data)
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
