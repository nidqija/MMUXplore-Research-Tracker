import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import ResearchPaper, User

def check_paper():
    paper = ResearchPaper.objects.filter(paper_title='Co-Authored Test Paper').first()
    if paper:
        print(f'Paper found: {paper.paper_title}')
        print(f'Status: {paper.paper_status}')
        print(f'Researcher: {paper.researcher_id.user_id.fullname}')
        co_authors = paper.paper_coauthor.all()
        print(f'Co-authors: {[u.fullname for u in co_authors]}')
    else:
        print('Paper not found')

if __name__ == '__main__':
    check_paper()
