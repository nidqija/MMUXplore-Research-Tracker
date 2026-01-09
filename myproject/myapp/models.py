from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
         return self.username

class Item(models.Model):
     name = models.CharField(max_length=255)
     description = models.TextField()
     owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
     created_at = models.DateTimeField(auto_now_add=True)

class AdminProfile(models.Model):
     user = models.OneToOneField(User, on_delete=models.CASCADE)
     is_superadmin = models.BooleanField(default=False)

     def __str__(self):
         return f"Admin Profile for {self.user.username}"
