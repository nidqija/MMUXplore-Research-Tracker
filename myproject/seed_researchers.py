"""
Seed script for researchers and research papers.
Run with: python manage.py shell < seed_researchers.py
Or: python seed_researchers.py (if Django settings are configured)

This script is idempotent - it will replace existing data when re-run.
"""

import os
import sys
import django
from datetime import date

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from myapp.models import User, Researcher, ResearchPaper

def seed_data():
    print("=" * 50)
    print("SEEDING RESEARCHERS AND PAPERS")
    print("=" * 50)

    # ==================== USERS ====================
    users_data = [
        {
            'university_id': '1001',
            'fullname': 'Dr. Sarah Chen',
            'email': 'sarah.chen@mmu.edu.my',
            'password': 'sarah123',
            'role': 'researcher',
        },
        {
            'university_id': '1002',
            'fullname': 'Prof. Ahmad Malik',
            'email': 'ahmad.malik@mmu.edu.my',
            'password': 'ahmad123',
            'role': 'researcher',
        },
        {
            'university_id': '1003',
            'fullname': 'Dr. Priya Nair',
            'email': 'priya.nair@mmu.edu.my',
            'password': 'priya123',
            'role': 'researcher',
        },
    ]

    created_users = []
    for user_data in users_data:
        user, created = User.objects.update_or_create(
            email=user_data['email'],
            defaults=user_data
        )
        created_users.append(user)
        status = "CREATED" if created else "UPDATED"
        print(f"[{status}] User: {user.fullname} (ID: {user.user_id})")

    # ==================== RESEARCHERS ====================
    researchers_data = [
        {
            'user': created_users[0],  # Dr. Sarah Chen
            'bio_description': 'AI researcher specializing in computer vision and deep learning.',
            'OCRID': '0000-0001-2345-6789',
            'google_scholar_id': 'sarahchen_cv',
        },
        {
            'user': created_users[1],  # Prof. Ahmad Malik
            'bio_description': 'Expert in cybersecurity and network protocols with 15 years of experience.',
            'OCRID': '0000-0002-3456-7890',
            'google_scholar_id': 'ahmadmalik_sec',
        },
        {
            'user': created_users[2],  # Dr. Priya Nair
            'bio_description': 'Data science researcher focusing on healthcare analytics and machine learning.',
            'OCRID': '0000-0003-4567-8901',
            'google_scholar_id': 'priyanair_ds',
        },
    ]

    created_researchers = []
    for r_data in researchers_data:
        researcher, created = Researcher.objects.update_or_create(
            user_id=r_data['user'],
            defaults={
                'bio_description': r_data['bio_description'],
                'OCRID': r_data['OCRID'],
                'google_scholar_id': r_data['google_scholar_id'],
            }
        )
        created_researchers.append(researcher)
        status = "CREATED" if created else "UPDATED"
        print(f"[{status}] Researcher: {r_data['user'].fullname} (ID: {researcher.researcher_id})")

    # ==================== RESEARCH PAPERS ====================
    # Delete existing papers for these researchers to avoid duplicates
    for researcher in created_researchers:
        deleted_count, _ = ResearchPaper.objects.filter(researcher_id=researcher).delete()
        if deleted_count > 0:
            print(f"[DELETED] {deleted_count} existing papers for {researcher.user_id.fullname}")

    papers_data = [
        # Dr. Sarah Chen's papers
        {
            'researcher': created_researchers[0],
            'paper_title': 'Deep Learning for Medical Image Segmentation',
            'paper_category': 'AI',
            'paper_desc': 'A novel approach using U-Net for tumor detection in MRI scans.',
            'paper_doi': '10.1000/ai2024.001',
            'paper_status': 'approved',
            'published_date': date(2025, 6, 15),
            'total_likes': 45,
            'total_bookmarked': 23,
        },
        {
            'researcher': created_researchers[0],
            'paper_title': 'Real-time Object Detection in Autonomous Vehicles',
            'paper_category': 'AI',
            'paper_desc': 'Improving YOLO architecture for faster inference in self-driving cars.',
            'paper_doi': '',
            'paper_status': 'pending',
            'published_date': None,
            'total_likes': 0,
            'total_bookmarked': 0,
        },
        {
            'researcher': created_researchers[0],
            'paper_title': 'Explainable AI in Healthcare Decision Systems',
            'paper_category': 'AI',
            'paper_desc': 'Survey on interpretable machine learning models for clinical use.',
            'paper_doi': '',
            'paper_status': 'rejected',
            'published_date': None,
            'total_likes': 0,
            'total_bookmarked': 0,
        },
        # Prof. Ahmad Malik's papers
        {
            'researcher': created_researchers[1],
            'paper_title': 'Zero-Trust Architecture for Cloud Security',
            'paper_category': 'Security',
            'paper_desc': 'Implementation framework for enterprise cloud environments.',
            'paper_doi': '10.1000/sec2024.005',
            'paper_status': 'approved',
            'published_date': date(2025, 3, 20),
            'total_likes': 78,
            'total_bookmarked': 56,
        },
        {
            'researcher': created_researchers[1],
            'paper_title': 'Blockchain-based Authentication Protocols',
            'paper_category': 'Security',
            'paper_desc': 'Novel decentralized identity verification system.',
            'paper_doi': '10.1000/sec2024.006',
            'paper_status': 'approved',
            'published_date': date(2025, 8, 10),
            'total_likes': 92,
            'total_bookmarked': 41,
        },
        {
            'researcher': created_researchers[1],
            'paper_title': 'Vulnerability Analysis in IoT Networks',
            'paper_category': 'Security',
            'paper_desc': 'Comprehensive study of attack vectors in smart home devices.',
            'paper_doi': '',
            'paper_status': 'pending',
            'published_date': None,
            'total_likes': 0,
            'total_bookmarked': 0,
        },
        {
            'researcher': created_researchers[1],
            'paper_title': 'Quantum-Resistant Cryptography Standards',
            'paper_category': 'Security',
            'paper_desc': 'Preparing enterprise systems for post-quantum security threats.',
            'paper_doi': '',
            'paper_status': 'rejected',
            'published_date': None,
            'total_likes': 0,
            'total_bookmarked': 0,
        },
        # Dr. Priya Nair's papers
        {
            'researcher': created_researchers[2],
            'paper_title': 'Predictive Analytics for Patient Readmission',
            'paper_category': 'Data Science',
            'paper_desc': 'Machine learning models to reduce hospital readmission rates.',
            'paper_doi': '10.1000/ds2024.010',
            'paper_status': 'approved',
            'published_date': date(2025, 1, 25),
            'total_likes': 65,
            'total_bookmarked': 38,
        },
        {
            'researcher': created_researchers[2],
            'paper_title': 'Natural Language Processing in Clinical Notes',
            'paper_category': 'Data Science',
            'paper_desc': 'Extracting insights from unstructured medical records using BERT.',
            'paper_doi': '',
            'paper_status': 'pending',
            'published_date': None,
            'total_likes': 0,
            'total_bookmarked': 0,
        },
        {
            'researcher': created_researchers[2],
            'paper_title': 'Federated Learning for Privacy-Preserving Healthcare AI',
            'paper_category': 'Data Science',
            'paper_desc': 'Distributed training without sharing sensitive patient data.',
            'paper_doi': '',
            'paper_status': 'pending',
            'published_date': None,
            'total_likes': 0,
            'total_bookmarked': 0,
        },
    ]

    for paper_data in papers_data:
        paper = ResearchPaper.objects.create(
            researcher_id=paper_data['researcher'],
            paper_title=paper_data['paper_title'],
            paper_category=paper_data['paper_category'],
            paper_desc=paper_data['paper_desc'],
            paper_doi=paper_data['paper_doi'],
            paper_status=paper_data['paper_status'],
            published_date=paper_data['published_date'],
            total_likes=paper_data['total_likes'],
            total_bookmarked=paper_data['total_bookmarked'],
            paper_pdf='',  # Empty for seed data
        )
        print(f"[CREATED] Paper: {paper.paper_title[:40]}... ({paper.paper_status})")

    # ==================== SUMMARY ====================
    print("\n" + "=" * 50)
    print("SEEDING COMPLETE!")
    print("=" * 50)
    print(f"Users created/updated: {len(created_users)}")
    print(f"Researchers created/updated: {len(created_researchers)}")
    print(f"Papers created: {len(papers_data)}")
    print("\nYou can now login as:")
    for user in created_users:
        print(f"  - {user.email} / {user.password}")


if __name__ == '__main__':
    seed_data()
