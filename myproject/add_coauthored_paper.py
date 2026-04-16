import os
import django
import sys
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import User, Researcher, Student, ResearchPaper

def create_coauthored_paper(student_name=None):
    # Create a researcher if not exists
    researcher_user, created = User.objects.get_or_create(
        email='researcher@example.com',
        defaults={
            'fullname': 'Test Researcher',
            'university_id': 'RES001',
            'password': 'password',
            'role': 'researcher'
        }
    )
    if created:
        Researcher.objects.create(user_id=researcher_user)

    # Get student by name or create default
    if student_name:
        student_user = User.objects.filter(fullname=student_name, role='student').first()
        if not student_user:
            print(f"Student '{student_name}' not found. Creating default student.")
            student_user, created = User.objects.get_or_create(
                email='student@example.com',
                defaults={
                    'fullname': 'Test Student',
                    'university_id': 'STU001',
                    'password': 'password',
                    'role': 'student'
                }
            )
            if created:
                Student.objects.create(user_id=student_user)
    else:
        student_user, created = User.objects.get_or_create(
            email='student@example.com',
            defaults={
                'fullname': 'Test Student',
                'university_id': 'STU001',
                'password': 'password',
                'role': 'student'
            }
        )
        if created:
            Student.objects.create(user_id=student_user)

    # Get the researcher object
    researcher = Researcher.objects.get(user_id=researcher_user)

    # Create a co-authored paper
    paper = ResearchPaper.objects.create(
        researcher_id=researcher,
        paper_title='Co-Authored Test Paper',
        paper_category='Computer Science',
        paper_desc='A test paper for co-authorship',
        paper_status='approved',
        published_date=timezone.now()
    )
    paper.paper_coauthor.add(student_user)
    paper.save()

    print(f'Co-authored paper created and approved for student: {student_user.fullname}')

if __name__ == '__main__':
    student_name = sys.argv[1] if len(sys.argv) > 1 else None
    create_coauthored_paper(student_name)
