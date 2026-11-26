
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from apps.utils.response import res


User = get_user_model()


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class SignupViewTestCase(APITestCase):
    def setUp(self):
        # Définir l'URL de la vue
        self.url = reverse('signup')

        # Définir les données de test valides et non valides
        self.valid_data = {
            'email': 'test@example.com',
            'firstName': 'Test',
            'lastName': 'User',
            'password': 'Testpass@123',
            'confirmPassword': 'Testpass@123',
        }
        self.invalid_data = {
            'email': 'test@example.com',
            'firstName': 'Test',
            'lastName': 'User',
            'password': 'invalidpass',
            'confirmPassword': 'invalidpass',
        }

    def test_signup_success(self):
        # Envoyer une requête POST à la vue avec des données valides
        response = self.client.post(self.url, data=self.valid_data, format='json')

        # Vérifier que la réponse a un code de statut 201
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Vérifier que la réponse contient le message de succès attendu
        self.assertEqual(response.data['message'], res["SUCCESSFUL_REGISTRATION"])

        # Vérifier que l'utilisateur est bien dans base de données'
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_resend_activation_email_for_pending_account(self):
        user = User.objects.create_user(
            email="pending@example.com",
            password="Testpass@123",
            first_name="Pending",
            last_name="User",
        )
        response = self.client.post(
            reverse("resend_activation"),
            data={"email": user.email},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(user.email, mail.outbox[0].to)

    def test_signup_failure(self):
        # Envoyer une requête POST à la vue avec des données non valides
        response = self.client.post(self.url, data=self.invalid_data, format='json')

        # Vérifier que la réponse a un code de statut 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


