from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import User as CustomUser, ResearchPaper, Researcher, Student, ProgrammeCoordinator

class BasicTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create test user
        self.test_user = CustomUser.objects.create(
            fullname='Test User',
            email='test@example.com',
            password='testpass',
            role='student'
        )
        self.student = Student.objects.create(user_id=self.test_user)

    def test_index_view(self):
        """Test that index view returns 200 status code"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_signup_view_get(self):
        """Test signup page loads"""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)

    def test_signin_view_get(self):
        """Test signin page loads"""
        response = self.client.get(reverse('signin'))
        self.assertEqual(response.status_code, 200)

    def test_research_paper_page_view(self):
        """Test research paper page loads"""
        response = self.client.get(reverse('researchpaper'))
        self.assertEqual(response.status_code, 200)

    def test_user_creation(self):
        """Test user creation"""
        user_count = CustomUser.objects.count()
        self.assertEqual(user_count, 1)  # The one created in setUp

    def test_student_creation(self):
        """Test student profile creation"""
        student_count = Student.objects.count()
        self.assertEqual(student_count, 1)  # The one created in setUp
