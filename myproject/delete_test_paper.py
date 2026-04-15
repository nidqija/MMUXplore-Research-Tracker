import os
import sys
import django

# Setup Django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import ResearchPaper

# Delete the test paper
deleted_count, _ = ResearchPaper.objects.filter(paper_title='Co-Authored Test Paper').delete()
print(f'Deleted {deleted_count} test paper(s)')
