from aflohap.models import Room, User
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class TestUrls(TestCase):
    User = get_user_model()
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.register_url = reverse('register')
        Room.objects.create(id=1, name='Salle 1', description='Description de la salle 1')
        self.client = Client()
        self.user = User.objects.create_user(email='test@example.com', password='testpassword', pk=1)
        # Ajoutez les autres URL que vous souhaitez tester

    def test_room_exists(self):
        # Vérification que la salle avec l'ID 1 existe dans la base de données de test
        room = Room.objects.get(id=1)
        self.assertEqual(room.name, 'Salle 1')
        self.assertEqual(room.description, 'Description de la salle 1')

    def test_login_url(self):
        response = self.client.get(self.login_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/login_register.html')

    def test_logout_url(self):
        response = self.client.get(self.logout_url)
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_register_url(self):
        response = self.client.get(self.register_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/login_register.html')

    # Ajoutez les autres tests pour les autres URL

    # Exemple de test pour l'URL home
    def test_home_url(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/home.html')

        # Ajoutez cette ligne pour vérifier le reverse de l'URL 'user-profile'
        self.assertEqual(reverse('user-profile', args=[self.user.pk]), '/profile/1/')

    # Exemple de test pour l'URL room avec un utilisateur authentifié
    def test_room_url_authenticated_user(self):
        user = User.objects.create_user(email='test@example.com', username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('room', args=['1']))  # Remplacez '1' par un ID de salle existant
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/room.html')

    # Exemple de test pour l'URL room avec un utilisateur non authentifié
    def test_room_url_unauthenticated_user(self):
        response = self.client.get(reverse('room', args=['1']))  # Remplacez '1' par un ID de salle existant
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/room/1/')  # Remplacez '1' par un ID de salle existant
