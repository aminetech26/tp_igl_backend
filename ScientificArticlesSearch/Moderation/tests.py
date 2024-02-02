from django.test import TestCase
from rest_framework.test import APIClient
from Authentication.models import User
from django.urls import reverse
from rest_framework import status


class ModerationApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.moderateur = User.objects.create(
            first_name="Khaled",
            last_name="BENMACHICHE",
            username="khaledbenmachiche",
            password="secure-password",
            email="lk_benmachiche@esi.dz",
            user_type="Mod"
        )
        
    def setUp(self) -> None:
        self.client = APIClient()
        
    def test_create_moderator_successfully(self):
        url = reverse('moderation-list')
        data = {
            'email':"xxxx@xxx.x",
            'username':"xxxx",
            'password':"xxxx",
            'first_name':"xxxx",
            'last_name':"xxxx",
            "user_type":"Mod"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get(id=2).username, 'xxxx')
        self.assertEqual(User.objects.get(id=2).email, 'xxxx@xxx.x')
        self.assertEqual(User.objects.get(id=2).first_name, 'xxxx')
        self.assertEqual(User.objects.get(id=2).last_name, 'xxxx')
        self.assertEqual(User.objects.get(id=2).user_type, 'Mod')
    
    def test_create_moderator_missing_fields(self):
        url = reverse('moderation-list')
        data = {
            'email':"xxxx@xxx.x",
            'username':"xxxx",
            'first_name':"xxxx",
            'last_name':"xxxx",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
    
    def test_create_moderator_existing_username(self):
        url = reverse('moderation-list')
        data = {
            "first_name":"Khaled",
            "last_name":"BENMACHICHE",
            "username":"khaledbenmachiche",
            "password":"secure-password",
            "email":"lk_benmachiche@esi.dz",
            "user_type":"Mod",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
    
    def test_update_moderator_successfully(self):
        url = reverse('moderation-detail', args=[self.moderateur.id])
        data = {
            "first_name":"Khaled",
            "last_name":"BENMACHICHE",
            "username":"khaledbenmachiche",
            "password":"secure-password",
            "email":"lk_benmachiche@esi.dz"
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get(id=self.moderateur.id).username, 'khaledbenmachiche')
        self.assertEqual(User.objects.get(id=self.moderateur.id).email, 'lk_benmachiche@esi.dz')
        self.assertEqual(User.objects.get(id=self.moderateur.id).first_name, 'Khaled')
        self.assertEqual(User.objects.get(id=self.moderateur.id).last_name, 'BENMACHICHE')
        
    def test_update_moderator_not_found(self):
        url = reverse('moderation-detail', args=[100])
        data = {
            "first_name":"Khaled",
            "last_name":"BENMACHICHE",
            "username":"khaledbenmachiche",
            "password":"secure-password",
            "email":"lk_benmachiche@esi.dz"
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_delete_moderator_not_found(self):
        url = reverse('moderation-detail', args=[100])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_moderator_by_ids_successfully(self):
        url = reverse('moderation-delete_by_ids')
        data = {
            "moderators_ids":[1]
        }
        response = self.client.delete(url, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 0)
            