from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta


# =================================== User Model ======================================== 

class User(models.Model):
     user_id = models.AutoField(primary_key=True)
     fullname = models.CharField(max_length=150 , default='unknown' , blank=True)
     university_id = models.CharField(max_length=50, unique=True , default='0000')
     email = models.EmailField(unique=True , default='unknown@example.com')
     password = models.CharField(max_length=250 , default='password')
     role = models.CharField(max_length=50, default='student')
     avatar = models.FileField(upload_to='profile/', blank=True, null=True)
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
     
# =================================== Programme Coordinator Model ========================================

class ProgrammeCoordinator(models.Model):
    prog_coor_id = models.AutoField(primary_key=True)
    # Add null=True, blank=True to make them optional
    faculty_id = models.CharField(max_length=50, null=True, blank=True) 
    prog_name = models.CharField(max_length=150, null=True, blank=True)
    faculty = models.CharField(max_length=150, null=True, blank=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE) 

    def __str__(self):
        # Update str to handle potential None values
        return f"{self.prog_name or 'No Program'} ({self.faculty or 'No Faculty'})"

# =================================== Researcher Model ========================================


class Researcher(models.Model):

     researcher_id = models.AutoField(primary_key=True)
     user_id = models.ForeignKey(User, on_delete=models.CASCADE)
     bio_description = models.TextField(blank=True)
     OCRID = models.CharField(max_length=50, blank=True)
     google_scholar_id = models.CharField(max_length=50, blank=True)
     publications = models.TextField(blank=True)

     def __str__(self):
        return self.user.fullname

# =================================== Research Paper Model ========================================

class ResearchPaper(models.Model):
    PAPER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    paper_id = models.AutoField(primary_key=True)
    researcher_id = models.ForeignKey(Researcher, on_delete=models.CASCADE)
    prog_coor_id = models.ForeignKey(ProgrammeCoordinator, on_delete=models.SET_NULL, null=True, blank=True)
    paper_title = models.CharField(max_length=250)
    paper_category = models.CharField(max_length=100)
    paper_desc = models.TextField()
    paper_doi = models.CharField(max_length=100, blank=True, verbose_name="DOI")
    paper_pdf = models.FileField(upload_to='research_papers/')
    paper_status = models.CharField(max_length=20, choices=PAPER_STATUS_CHOICES, default='Pending')
    paper_coauthor = models.ManyToManyField(User, related_name='coauthored_papers', blank=True)
    total_bookmarked = models.IntegerField(default=0)
    total_likes = models.IntegerField(default=0)
    
    published_date = models.DateField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.paper_title
# =================================== Student Model ========================================

class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    program_of_studies = models.CharField(max_length=150)
    year_of_studies = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.fullname} - {self.program_of_studies}"

 # =================================== Comments Model ========================================

class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    paper_id = models.ForeignKey(ResearchPaper, on_delete=models.CASCADE, related_name='comments')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    admin_id = models.ForeignKey(Admin, on_delete=models.SET_NULL, null=True, blank=True)
    message_desc = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.fullname}"
# =================================== Notifications Model ========================================

class Notification(models.Model):
    notify_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    paper_id = models.ForeignKey(ResearchPaper, on_delete=models.CASCADE, null=True, blank=True)
    notify_title = models.CharField(max_length=100)
    notify_message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.notify_title} for {self.user.fullname}"
# =================================== Terms and Conditions Model ========================================


class TermsAndConditions(models.Model):
     term_id = models.AutoField(primary_key=True)
     title = models.CharField(max_length=200)
     content = models.TextField()
     last_updated = models.DateTimeField(auto_now=True)


     def __str__(self):
          return self.title , self.content
     
# =================================== Co-Author Model ========================================

class CoAuthor(models.Model):
    coauth_id = models.AutoField(primary_key=True)
    paper_id = models.ForeignKey(ResearchPaper, on_delete=models.CASCADE, related_name='co_authors')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user.fullname} on {self.paper.paper_title}"
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
     


class Submissions(models.Model):
     submission_id = models.AutoField(primary_key=True)
     paper_id = models.ForeignKey(ResearchPaper, on_delete=models.CASCADE)
     submitted_at = models.DateTimeField(auto_now_add=True)
     status = models.CharField(max_length=50, default='under review')

     def __str__(self):
          return f"Submission {self.submission_id} for Paper {self.paper_id.paper_title}"
     

class Violations(models.Model):
     violation_id = models.AutoField(primary_key=True)
     user = models.ForeignKey(User, on_delete=models.CASCADE)
     violation_type = models.TextField()
     date_reported = models.DateTimeField(auto_now_add=True)

     def __str__(self):
          return f"Violation {self.violation_id} by {self.user.fullname}"
     


     
class Bookmarks(models.Model):
    bookmark_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    paper_id = models.ForeignKey(ResearchPaper, on_delete=models.CASCADE)
    bookmarked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bookmark {self.bookmark_id} by {self.user_id.fullname} for {self.paper_id.paper_title}"
    

class Likes(models.Model):
    like_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    paper_id = models.ForeignKey(ResearchPaper, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Like {self.like_id} by {self.user_id.fullname} for {self.paper_id.paper_title}"
    


