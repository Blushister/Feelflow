from aflohap.forms import UserForm
from aflohap.models import (  # replace 'aflohap' with your actual app name
    Message, Room, Topic, User)
from django import forms
from django.test import Client, TestCase
from django.urls import reverse


class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='12345')

        self.room = Room.objects.create(
            name='Room 1',
            description='Room 1 description',
            host=self.user
        )

        self.topic = Topic.objects.create(
            name='Topic 1',
            room=self.room
        )

        self.message = Message.objects.create(
            user=self.user,
            room=self.room,
            body='Hello, world!'
        )

    def login_test_user(self):
        self.client.post(reverse('login'), data={
            'email': 'test@example.com',
            'password': '12345',
        })

    def test_home(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_activity_page(self):
        response = self.client.get(reverse('activity'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/activity.html')

    def test_topics_page(self):
        response = self.client.get(reverse('topics'), {'q': 'Topic 1'})
        self.assertEqual(response.status_code, 200)

    def test_room(self):
        response = self.client.get(reverse('room', args=[str(self.room.id)]))
        self.assertEqual(response.status_code, 200)

    def test_create_room(self):
        self.login_test_user()
        response = self.client.post(reverse('create-room'), {
            'name': 'Test Room',
            'description': 'Room description',
            'topic_name': 'Test Topic',  # Add this line
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_update_room(self):
        self.login_test_user()
        response = self.client.post(reverse('update-room', args=[str(self.room.id)]), {
            'name': 'Test 1 Room',
            'description': 'Room 1 description updated',
            'topic_name': 'Test Topic Updated',  # Add this line
        })
        self.assertEqual(response.status_code, 302)

    def test_delete_room(self):
        self.login_test_user()
        response = self.client.post(reverse('delete-room', args=[str(self.room.id)]))
        self.assertEqual(response.status_code, 302)

    def test_delete_message(self):
        self.login_test_user()
        # Assurez-vous d'abord que le message existe
        message = Message.objects.create(body="Test message", user=self.user, room=self.room)
        response = self.client.post(reverse('delete-message', args=[str(message.id)]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_register_page(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_logout_user(self):
        self.login_test_user()
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)

    def test_update_user(self):
        # Connecte l'utilisateur
        self.login_test_user()

        # Effectue une requête POST pour mettre à jour l'utilisateur
        response = self.client.post(reverse('update-user'), {
            'username': 'testuserupdated',
            'email': 'testuserupdated@example.com',
        })

        # Vérifie que la redirection a été effectuée avec succès
        self.assertEqual(response.status_code, 200)

        # Récupère l'utilisateur mis à jour depuis la base de données
        updated_user = User.objects.get(id=self.user.id)

        # Vérifie que les attributs de l'utilisateur ont été mis à jour correctement
        self.assertEqual(updated_user.username, 'testuserupdated')
        self.assertEqual(updated_user.email, 'testuserupdated@example.com')

    def test_user_profile(self):
        response = self.client.get(reverse('user-profile', args=[str(self.user.id)]))
        self.assertEqual(response.status_code, 200)
