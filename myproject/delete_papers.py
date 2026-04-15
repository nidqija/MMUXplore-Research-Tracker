import os
import sys
import django

# Setup Django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import ResearchPaper

# List of paper titles to delete
papers_to_delete = ['sdasva', 'SELURVE', 'SELURVE2', 'aaaaa']

# Find and delete each paper
total_deleted = 0
for title in papers_to_delete:
    deleted_count, _ = ResearchPaper.objects.filter(paper_title=title).delete()
    if deleted_count > 0:
        print(f"Deleted {deleted_count} paper(s) with title: {title}")
        total_deleted += deleted_count
    else:
        print(f"No paper found with title: {title}")

print(f"\nTotal deleted: {total_deleted} paper(s)")

# Verify the remaining papers
remaining_papers = ResearchPaper.objects.all()
print(f"\nRemaining papers in database: {remaining_papers.count()}")
for paper in remaining_papers:
    print(f"  - {paper.paper_title}")
