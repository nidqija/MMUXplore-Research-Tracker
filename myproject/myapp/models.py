from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta


# =================================== User Model ======================================== 

class User(models.Model):
     user_id = models.AutoField(primary_key=True)
     fullname = models.CharField(max_length=150 , default='unknown')
     university_id = models.CharField(max_length=50, unique=True , default='0000')
     email = models.EmailField(unique=True , default='unknown@example.com')
     password = models.CharField(max_length=250 , default='password')
     role = models.CharField(max_length=50, default='student')
     date_joined = models.DateTimeField(auto_now_add=True )

     def __str__(self):
          return self.fullname


# =================================== Admin Model ======================================== 


class Admin(models.Model):
     admin_id = models.AutoField(primary_key=True)
     user_name = models.CharField(max_length=150)
     email = models.EmailField(unique=True)
     password = models.CharField(max_length=250)
     date_joined = models.DateTimeField(auto_now_add=True)

     def __str__(self):
          return self.user_name
     


# =================================== Researcher Model ========================================


class Researcher(models.Model):

     researcher_id = models.AutoField(primary_key=True)
     user = models.ForeignKey(User, on_delete=models.CASCADE)
     bio_description = models.TextField(blank=True)
     OCRID = models.CharField(max_length=50, blank=True)
     google_scholar_id = models.CharField(max_length=50, blank=True)
     publications = models.TextField(blank=True)


# =================================== Terms and Conditions Model ========================================


class TermsAndConditions(models.Model):
     term_id = models.AutoField(primary_key=True)
     title = models.CharField(max_length=200)
     content = models.TextField()
     last_updated = models.DateTimeField(auto_now=True)


     def __str__(self):
          return self.title , self.content
     

# =================================== Announcements Model ========================================

class Announcements(models.Model):
     announcement_id = models.AutoField(primary_key=True)
     announcement_title = models.CharField(max_length=200)
     announcement_desc = models.TextField()
     attachment = models.FileField(upload_to='announcements_folder/', blank=True, null=True)
     date_posted = models.DateTimeField(auto_now_add=True)

     def __str__(self):
          return self.announcement_title
     
     @property
     def is_new(self):
          return timezone.now() - self.date_posted <= timedelta(hours=24)
     

class Violations(models.Model):
     violation_id = models.AutoField(primary_key=True)
     user = models.ForeignKey(User, on_delete=models.CASCADE)
     violation_type = models.TextField()
     date_reported = models.DateTimeField(auto_now_add=True)

     def __str__(self):
          return f"Violation {self.violation_id} by {self.user.fullname}"
     

class Violation_User(models.Model):
     violation_user_id = models.AutoField(primary_key=True)
     user_id = models.ForeignKey(User, on_delete=models.CASCADE)
     violation_id = models.ForeignKey(Violations, on_delete=models.CASCADE)
     date_recorded = models.DateTimeField(auto_now_add=True)

     def __str__(self):
          return f"User {self.user_id.fullname} - Violation {self.violation_id.violation_id}"
     
     