from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from aflohap.models import (  # replace 'aflohap' with your actual app name
    Message, Room, Topic, User)

from .forms import UserForm


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
        response = self.client.post(reverse('create-room'), {
            'name': 'New Room',
            'description': 'Room description',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))


    def test_update_room(self):
        response = self.client.post(reverse('update-room', args=[str(self.room.id)]), {
            'name': 'Room 1 updated',
            'description': 'Room 1 description updated',
        })
        self.assertEqual(response.status_code, 302)

    def test_delete_room(self):
        response = self.client.post(reverse('delete-room', args=[str(self.room.id)]))
        self.assertEqual(response.status_code, 302)


    def test_delete_message(self):
        # Connecte l'utilisateur
        self.client.login(username='testuser', password='12345')

        # Effectue une requête POST pour supprimer le message
        response = self.client.post(reverse('delete-message', args=[str(self.message.id)]))

        # Vérifie que la redirection a été effectuée avec succès
        self.assertRedirects(response, reverse('home'))

    def test_register_page(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_logout_user(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)

    def test_update_user(self):
        # Connecte l'utilisateur
        self.client.login(username='testuser', password='12345')

        # Effectue une requête POST pour mettre à jour l'utilisateur
        response = self.client.post(reverse('update-user'), {
            'name': 'Test_User_Updated',
            'username': 'testuser',
            'email': 'testuserupdated@example.com',
        })

        # Vérifie que la redirection a été effectuée avec succès
        self.assertEqual(response.status_code, 302)

        # Récupère l'utilisateur mis à jour depuis la base de données
        updated_user = User.objects.get(id=self.user.id)

        # Vérifie que les attributs de l'utilisateur ont été mis à jour correctement
        self.assertEqual(updated_user.name, 'Test_User_Updated')
        self.assertEqual(updated_user.email, 'testuserupdated@example.com')
        # Vérifie que les attributs de l'utilisateur correspondent aux valeurs du formulaire
        self.assertEqual(updated_user.name, form.cleaned_data['name'])
        self.assertEqual(updated_user.username, form.cleaned_data['username'])
        self.assertEqual(updated_user.email, form.cleaned_data['email'])
        self.assertEqual(updated_user.bio, form.cleaned_data['bio'])

    def test_user_profile(self):
        response = self.client.get(reverse('user-profile', args=[str(self.user.id)]))
        self.assertEqual(response.status_code, 200)
