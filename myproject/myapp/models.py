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
    faculty_id = models.CharField(max_length=50, null=True, blank=True) 
    prog_name = models.CharField(max_length=150, null=True, blank=True)
    faculty = models.CharField(max_length=150, null=True, blank=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) 
    

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

# =================================== Student Model ========================================

class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    program_of_studies = models.CharField(max_length=150)
    year_of_studies = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.fullname} - {self.program_of_studies}"


# =================================== Research Paper Model ========================================

class ResearchPaper(models.Model):
    PAPER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('revision', 'Revision'),
    ]

    paper_id = models.AutoField(primary_key=True)
    researcher_id = models.ForeignKey(Researcher, on_delete=models.CASCADE , null=True, blank=True)
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
    student_id = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    published_date = models.DateField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Sync status with Submissions table
        submission = Submissions.objects.filter(paper_id=self).first()
        if submission:
            if submission.status != self.paper_status:
                submission.status = self.paper_status
                submission.save()
        else:
            # Create a submission entry if it doesn't exist (e.g. for papers 1-10)
            Submissions.objects.create(
                paper_id=self,
                status=self.paper_status,
                submitted_at=timezone.now()
            )

    def __str__(self):
        return self.paper_title


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
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications') #recipient id
    notify_title = models.CharField(max_length=100)
    notify_message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sender_id = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='violations_received')
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='violations_filed')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE , null=True , blank=True) 
    violation_type = models.TextField() 
    date_reported = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report on {self.user.fullname} - Reason: {self.violation_type}"
     

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
    

class Report(models.Model):
    REPORT_TYPE = [
            ('faculty', 'Faculty KPI'),
            ('individual', 'Individual Summary'),
        ]

   
    report_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE)
    faculty_name = models.CharField(max_length=255, default="Faculty of Computing")
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name='individual_reports')
    generated_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='reports_generated')
    date_generated = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='report/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)


    def __str__(self):
        if self.report_type == 'individual' and self.user:
            return f"{self.title} - {self.user.fullname} ({self.date_generated.date()})"
        
        return f"{self.title} - {self.faculty_name} ({self.date_generated.date()})"








