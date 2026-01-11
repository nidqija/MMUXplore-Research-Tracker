from django.db import models
from django.contrib.auth.models import AbstractUser


     # Create your models here.
class User(models.Model):
     fullname = models.CharField(max_length=150 , default='unknown')
     university_id = models.CharField(max_length=50, unique=True , default='0000')
     email = models.EmailField(unique=True , default='unknown@example.com')
     password = models.CharField(max_length=250 , default='password')
     date_joined = models.DateTimeField(auto_now_add=True )

     def __str__(self):
          return self.fullname
     
class Researcher(models.Model):

     researcher_id = models.AutoField(primary_key=True)
     user = models.ForeignKey(User, on_delete=models.CASCADE)
     bio_description = models.TextField(blank=True)
     OCRID = models.CharField(max_length=50, blank=True)
     google_scholar_id = models.CharField(max_length=50, blank=True)
     publications = models.TextField(blank=True)