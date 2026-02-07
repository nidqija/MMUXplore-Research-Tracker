
import datetime
import csv
from fpdf import FPDF
from multiprocessing import context
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from pytz import timezone
from .models import Admin, Bookmarks, Likes, ResearchPaper, Submissions, User,Researcher , TermsAndConditions , Announcements , Student, ProgrammeCoordinator , Violations , Comment , Notification

from django.shortcuts import render, redirect
from django.conf import settings
from .models import Admin, ResearchPaper, Submissions, User,Researcher , TermsAndConditions , Announcements , Student , Comment
from django.contrib import messages
from django.views.decorators.http import require_POST
from functools import wraps
from django.utils import timezone
from django.db.models import Q
from django.http import HttpResponse



# function to check if user is admin

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user_name = request.session.get('user_name')
        try:
            admin = Admin.objects.get(user_name=user_name)
            return view_func(request, *args, **kwargs)
        except Admin.DoesNotExist:
            messages.error(request, "You must be an admin to access this page.")
            return redirect('signin')
    return _wrapped_view


def index(request):
    user_name = request.session.get('user_name', 'Guest')
    announcements = Announcements.objects.all().order_by('-date_posted') 
    research_papers = ResearchPaper.objects.filter(paper_status='approved')
    user_id = request.session.get('user_id') # Make sure this is being set during sign-in!

    latest_tc = TermsAndConditions.objects.order_by('-last_updated').first()
    user = User.objects.filter(fullname=user_name).first()
    notifications = Notification.objects.filter(user_id=user).order_by('-created_at') if user else []       
    # Check if the latest terms and conditions were updated within the last 7 days
    new_tc_update = False

    # if there is at least one terms and conditions entry 
    if latest_tc:

        # calculate the time limit
        recent_limit = timezone.now() - timezone.timedelta(days=7)

        # compare the last updated time with the limit
        if latest_tc.last_updated >= recent_limit:

            new_tc_update = True

    is_admin = False

    if user_name != 'Guest':
        is_admin = Admin.objects.filter(user_name=user_name).exists()

    return render(request, 'home.html', {'user_name': user_name , 'announcements': announcements, 'is_admin': is_admin , 'new_tc_update': new_tc_update, 'research_papers': research_papers, 'user_id': user_id } )



def user_signup(request):
    if request.method == 'POST':
        university_id = request.POST.get('university_id')
        email = request.POST.get('email')
        role = request.POST.get('role')
        password = request.POST.get('password')

        if not role:
            messages.error(request, 'Please select a valid role.')
            return render(request, 'signup.html')

        # 1. Handle Admin Logic
        if university_id.upper().startswith('MQA123'):
            admin = Admin.objects.create(
                user_name=email, 
                email=email, 
                password=password
            )
            # Store admin session immediately
            request.session['user_name'] = admin.user_name
            messages.success(request, 'Admin account created.')
            return redirect('admin_homepage')

        # 2. Check if user already exists to prevent crashes
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'signup.html')

        
        user = User.objects.create(
            fullname='', 
            university_id=university_id, 
            email=email, 
            password=password, 
            role=role
        )

      
        if role == 'researcher':
            Researcher.objects.create(user_id=user) #
        elif role == 'student':
            Student.objects.create(user_id=user) #
        elif role == 'program_coordinator': 
            ProgrammeCoordinator.objects.create(user_id=user)
            request.session['user_id'] = user.user_id  #  store ID for URL redirects
       

       
        request.session['temp_user_email'] = email

        messages.success(request, 'Account created! Now let\'s set up your profile.')
        return redirect('avatar_register')

    return render(request, 'signup.html') 





        


def user_avatar_register(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        avatar = request.FILES.get('avatar')

        # Retrieve the email we just stored in the signup view
        temp_email = request.session.get('temp_user_email')
        user = User.objects.filter(email=temp_email).first()

        if user:
            user.fullname = fullname
            user.avatar = avatar
            user.save()
            
            # Now that the profile is complete, set the main session
            request.session['user_name'] = user.fullname
            
            # Clean up the temporary session
            del request.session['temp_user_email']
            
            messages.success(request, 'Profile updated successfully.')
            if user.role == 'program_coordinator':
                return redirect('coordinator_home', user_id=user.user_id)
            
            return redirect('home')
        else:
            messages.error(request, 'Session expired. Please sign up again.')
            return redirect('user_signup')
            
    return render(request, 'user_avatar_register.html')




def user_logout(request):
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


def update_profile(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        avatar = request.FILES.get('avatar')

        current_user_name = request.session.get('user_name')
        user = User.objects.filter(fullname=current_user_name).first()

        if user:
            user.fullname = fullname
            if avatar:
                user.avatar = avatar
            user.save()
            
            # Update session
            request.session['user_name'] = user.fullname
            
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
        else:
            messages.error(request, 'User not found. Please sign in again.')
            return redirect('signin')
            
    return render(request, 'update_profile.html')



#==================================== Researcher Parts ====================================#
def researcher_home(request, researcher_id):
    researcher = Researcher.objects.get(researcher_id=researcher_id)

    if request.method == 'POST':
        paper_id = request.POST.get('paper_id')
        title = request.POST.get('title')
        abstract = request.POST.get('abstract')
        category = request.POST.get('category')
        doi = request.POST.get('doi')
        
        if paper_id:
            try:
                paper = ResearchPaper.objects.get(paper_id=paper_id)
                paper.paper_title = title
                paper.paper_desc = abstract
                if category:
                    paper.paper_category = category
                if doi:
                    paper.paper_doi = doi
                
                # Logic: If editing a paper (especially one in revision/rejected), reset to pending
                paper.paper_status = 'pending'
                paper.save() # save() method on model handles syncing to Submissions

                messages.success(request, 'Paper updated successfully.')
            except ResearchPaper.DoesNotExist:
                messages.error(request, 'Paper not found.')
        return redirect('researcher_home', researcher_id=researcher_id)
    
    # Get all papers by this researcher
    all_papers = ResearchPaper.objects.filter(researcher_id=researcher)
    

    # Count by status
    pending_count = all_papers.filter(paper_status='pending').count()
    revision_count = all_papers.filter(paper_status='revision').count()
    approved_count = all_papers.filter(paper_status='approved').count()
    rejected_count = all_papers.filter(paper_status='rejected').count()
    
    # Get papers for display
    pending_papers = all_papers.filter(paper_status='pending')
    papers = all_papers  # All papers for the "Your Papers" section

    context = {
        'researcher': researcher,
        'pending_count': pending_count,
        'revision_count': revision_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'pending_papers': pending_papers,
        'revision_papers': all_papers.filter(paper_status='revision'),
        'rejected_papers': all_papers.filter(paper_status='rejected'),
        'approved_papers': all_papers.filter(paper_status='approved'),
        'papers': papers
    }

    return render(request, 'researcher/researcher_home.html', context)


def researcher_upload_page(request, researcher_id):
    researcher = Researcher.objects.get(researcher_id=researcher_id)
    all_users = User.objects.all().exclude(role='admin').exclude(user_id=researcher.user_id.user_id)

    context = {
        'researcher': researcher,
        'all_users': all_users
    }

    if request.method == 'POST':
        paper_title = request.POST.get('paper_title')
        paper_category = request.POST.get('paper_category')
        paper_abstract = request.POST.get('paper_abstract')
        paper_file = request.FILES.get('paper_pdf')
        paper_coauthor = request.POST.getlist('paper_coauth')



        if paper_title and paper_abstract and paper_file:
            new_paper = ResearchPaper(
                researcher_id=researcher,
                paper_title=paper_title,
                paper_category=paper_category,
                paper_desc=paper_abstract,
                paper_pdf=paper_file,
                paper_status='pending'
            )

            new_submission = Submissions(
                paper_id=new_paper,
                status='pending',
                submitted_at=timezone.now()
            )

            

        
            new_paper.save()
            new_submission.save()

            if paper_coauthor:
                new_paper.paper_coauthor.set(paper_coauthor)

            messages.success(request, 'Research paper uploaded successfully.')
            return redirect('researcher_home', researcher_id=researcher_id)
        else:
            messages.error(request, 'All fields are required to upload a research paper.')


       

    return render(request, 'researcher/researcher_upload_page.html', context)

def researcher_profile(request, researcher_id):
    researcher = Researcher.objects.get(researcher_id=researcher_id)
    
    if request.method == 'POST':
        # Update user fields
        fullname = request.POST.get('fullname')
        if fullname:
            researcher.user_id.fullname = fullname
            researcher.user_id.save()
            # Update session
            request.session['user_name'] = fullname
        
        # Update researcher fields
        researcher.bio_description = request.POST.get('bio_description', '')
        researcher.OCRID = request.POST.get('OCRID', '')
        researcher.google_scholar_id = request.POST.get('google_scholar_id', '')
        researcher.save()
        
        messages.success(request, 'Profile updated successfully.')
        return redirect('researcher_profile', researcher_id=researcher_id)

    context = {
        'researcher': researcher
    }

    return render(request, 'researcher/researcher_profile.html', context)
#====================================Researcher Parts End ====================================#


def view_research_paper(request, paper_id):
    research_papers = ResearchPaper.objects.get(paper_id=paper_id)
    researcher = research_papers.researcher_id
    researchname = researcher.user_id.fullname
    comments = Comment.objects.filter(paper_id=research_papers)
    user_name = request.session.get('user_name', 'Guest')
    user_id = request.session.get('user_id')
    
    notifications = Notification.objects.filter(user_id__fullname=user_name).order_by('-created_at') if user_name != 'Guest' else []


    has_liked = False
    has_bookmarked = False

    if user_id:
      has_liked = Likes.objects.filter(paper_id=research_papers, user_id=user_id).exists()
      has_bookmarked = Bookmarks.objects.filter(paper_id=research_papers, user_id=user_id).exists()


    if user_name != 'Guest':
        is_admin = Admin.objects.filter(user_name=user_name).exists()

    user_role = request.session.get('role')
    is_coordinator = False 

    if user_role == 'program_coordinator':
        is_coordinator = ProgrammeCoordinator.objects.filter(user_id=request.user).exists()

    return render(request , 'view_research_paper.html', {'user_name': user_name , 'research_papers': research_papers , 'researcher': researcher , 'is_coordinator': is_coordinator, 'is_admin': is_admin ,'researchname': researchname, 'comments': comments , 'notifications': notifications , 'has_liked': has_liked, 'has_bookmarked': has_bookmarked , 'user_id': user_id} )


def like_research_paper(request, paper_id):
    research_paper = get_object_or_404(ResearchPaper, paper_id=paper_id)

    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "You must be logged in to like a paper.")
        return redirect('signin')

    # 3. Fetch the actual User object instance
    user_instance = get_object_or_404(User, user_id=user_id)

    paper_likes = Likes.objects.create(
        paper_id=research_paper,
        liked_at=timezone.now(),
        user_id = user_instance
    )

    paper_likes.save()

    research_paper.total_likes += 1
    research_paper.save()
    messages.success(request, 'You liked this research paper!')
    return redirect('view_research_paper', paper_id=paper_id)


def unlike_research_paper(request, paper_id):
    research_paper = get_object_or_404(ResearchPaper, paper_id=paper_id)

    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "You must be logged in to unlike a paper.")
        return redirect('signin')

    # 3. Fetch the actual User object instance
    user_instance = get_object_or_404(User, user_id=user_id)

    try:
        paper_likes = Likes.objects.get(
            paper_id=research_paper,
            user_id=user_instance
        )
        paper_likes.delete()

        research_paper.total_likes -= 2
        research_paper.save()
        messages.success(request, 'You unliked this research paper!')
    except Likes.DoesNotExist:
        messages.error(request, 'You have not liked this paper yet.')

    return redirect('view_research_paper', paper_id=paper_id)

def bookmark_research_paper(request, paper_id):
    research_paper = get_object_or_404(ResearchPaper, paper_id=paper_id)

    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "You must be logged in to bookmark a paper.")
        return redirect('signin')

    # 3. Fetch the actual User object instance
    user_instance = get_object_or_404(User, user_id=user_id)

    paper_bookmarks = Bookmarks.objects.create(
        paper_id=research_paper,
        bookmarked_at=timezone.now(),
        user_id = user_instance
    )

    paper_bookmarks.save()

    research_paper.total_bookmarked += 1
    research_paper.save()
    messages.success(request, 'You bookmarked this research paper!')
    return redirect('view_research_paper', paper_id=paper_id)


def unlike_bookmark_research_paper(request, paper_id):
    research_paper = get_object_or_404(ResearchPaper, paper_id=paper_id)

    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "You must be logged in to remove bookmark from a paper.")
        return redirect('signin')

    # 3. Fetch the actual User object instance
    user_instance = get_object_or_404(User, user_id=user_id)

    try:
        paper_bookmarks = Bookmarks.objects.get(
            paper_id=research_paper,
            user_id=user_instance
        )
        paper_bookmarks.delete()

        research_paper.total_bookmarked -= 1
        research_paper.save()
        messages.success(request, 'You removed bookmark from this research paper!')
    except Bookmarks.DoesNotExist:
        messages.error(request, 'You have not bookmarked this paper yet.')

    return redirect('view_research_paper', paper_id=paper_id)

#programme coordinator
def get_logged_in_coordinator(request): #id and role retrieval
    user_id = request.session.get('user_id')
    user_role = request.session.get('user_role')

    if not user_id or user_role != 'program_coordinator':
        return None

    try:
        return ProgrammeCoordinator.objects.get(user_id=user_id)
    except ProgrammeCoordinator.DoesNotExist:
        return None

def coordinator_home(request, user_id):
    # Fetch the coordinator associated with the user_id passed in the URL
    # use user_id__user_id because the model field is named 'user_id' (FK) 
    # and we are looking for the 'user_id' field on the User model.
    coordinator = get_object_or_404(ProgrammeCoordinator, user_id__user_id=user_id)
    user_name = request.session.get('user_name')


    submission = Submissions.objects.filter(status__in=['pending', 'revision']).select_related('paper_id')
    pastSubmission = Submissions.objects.filter(status__in=['approved', 'rejected']).select_related('paper_id')
    
    return render(request, 'coordinator/coordinator_home.html', {
        'coordinator': coordinator,
        'user_name': user_name,
        'submissions': submission,
        'pastSubmissions': pastSubmission,
    })

def submissions(request):
    # Only get submissions with status 'under review'
    user_id = request.session.get('user_id')
    


    # 2. Correctly query the coordinator using the user_id
    # We use user_id__user_id because the field in ProgrammeCoordinator is named 'user_id'
    # and it points to the User model's 'user_id' field.
    user_id = request.session.get('user_id')
    user_name = request.session.get('user_name')
    coordinator = ProgrammeCoordinator.objects.filter(user_id__user_id=user_id).first()
    submission = Submissions.objects.filter(status__in=['pending', 'revision']).select_related('paper_id')
    pastSubmission = Submissions.objects.filter(status__in=['approved', 'rejected']).select_related('paper_id')
    context = {
        'coordinator': coordinator,
        'submissions': submission,
        'pastSubmissions': pastSubmission,
        'user_name': user_name
    }
    return render(request, 'coordinator/submissions.html', context)

   
    



def submission_detail(request, submission_id):
    # Get the paper and the specific submission entry linked to it
    user_id = request.session.get('user_id')
    coordinator = ProgrammeCoordinator.objects.get(user_id__user_id=user_id)
    # Try to find the linked submission ID for display (if it exists)
    submission = get_object_or_404(Submissions, submission_id=submission_id)
    paper = submission.paper_id   # get the related ResearchPaper
   

    if request.method == 'POST':
        action = request.POST.get('action')
        reason = request.POST.get('reason', 'No specific reason provided.')
        
        if action == 'approve':
            paper.paper_status = 'approved'
            paper.published_date = timezone.now()
            submission.status = 'approved'

            Notification.objects.create(
                user_id=paper.researcher_id.user_id,
                notify_title="Paper Approval",
                notify_message=f"{coordinator.user_id.fullname} approved your paper: '{paper.paper_title}'",
                created_at=timezone.now(),
                sender_id = coordinator.user_id 
            )
            messages.success(request, "Paper Approved! Submission entry removed.")
            
        elif action == 'reject':
            paper.paper_status = 'rejected'
            submission.status = 'rejected'
            messages.error(request, "Paper Rejected. Submission entry removed.")

            Notification.objects.create(
                user_id=paper.researcher_id.user_id,
                notify_title="Paper Rejected",
                notify_message=f"{coordinator.user_id.fullname} rejected your paper: '{paper.paper_title}' \n Reason:",
                created_at=timezone.now(),
                sender_id = coordinator.user_id 
            )

        elif action == 'reopen':
            paper.paper_status = 'pending'
            submission.status = 'pending'

            Notification.objects.create(
                user_id=paper.researcher_id.user_id,
                notify_title="Paper reopened for evaluation",
                notify_message=f"{coordinator.user_id.fullname} has reopened your paper submission: '{paper.paper_title}' for evaluation again.",
                created_at=timezone.now(),
                sender_id = coordinator.user_id 
            )
            messages.success(request, "Paper reopened for evaluation.")
            
        elif action == 'revision':

            paper.paper_status = 'revision'
            submission.status = 'revision'

            Notification.objects.create(
                user_id=paper.researcher_id.user_id,
                notify_title="Revision Requested",
                # We inject the reason here
                notify_message=f"{coordinator.user_id.fullname} requested a revision for: '{paper.paper_title}'.\nComments: {reason}",
                created_at=timezone.now(),
                sender_id=coordinator.user_id
            )
            messages.warning(request, "Revision requested from the researcher.")
            # Optional: paper.paper_status = 'revision_requested'
        
        paper.save() # The signal will handle deleting the submission entry if approved/rejected
        submission.save()

        return redirect('coordinator_submissions')

    context = {
        'coordinator':coordinator,
        'paper': paper,
        'submission_id': submission.submission_id,
        'submission': submission
    }
    return render(request, 'coordinator/submission_detail.html', context)




def coordinator_view_research_paper(request, paper_id):
    #  Get the paper safely
    research_paper = get_object_or_404(ResearchPaper, paper_id=paper_id)

    # Get related researcher info
    researcher = research_paper.researcher_id
    researchname = researcher.user_id.fullname

    #  Get comments for this paper
    comments = Comment.objects.filter(paper_id=research_paper)

    #  Get logged-in user from session
    user_name = request.session.get('user_name', 'Guest')

    #. Coordinator check
    is_coordinator = False
    coordinator = None

    if user_name != 'Guest':
        coordinator = ProgrammeCoordinator.objects.filter(
            user_id__fullname=user_name
        ).first()
        is_coordinator = coordinator is not None

    # 6. Pass everything to template
    context = {
        'user_name': user_name,
        'research_paper': research_paper,
        'researcher': researcher,
        'researchname': researchname,
        'comments': comments,
        'is_coordinator': is_coordinator,
        'coordinator': coordinator,
    }

    return render(request, 'coordinator/view_research_paper.html', context)


def analytics_page(request):

    user_id = request.session.get('user_id')
    user_name = request.session.get('user_name')
    coordinator = ProgrammeCoordinator.objects.get(user_id__user_id=user_id)
    researchpapers = ResearchPaper.objects.filter(paper_status='approved').order_by('-published_date')

    context = {
        'coordinator' : coordinator,
        'researchpapers' : researchpapers,
        'user_name': user_name


    }

    return render(request, 'coordinator/analytics_page.html', context)

def generate_report(request) :

    user_id = request.session.get('user_id')
    user_name = request.session.get('user_name')
    coordinator = ProgrammeCoordinator.objects.get(user_id__user_id=user_id)
    researchers = Researcher.objects.all()
    

    query = request.GET.get('q', '').strip()

    if query:
        researchers = researchers.filter(
            Q(user_id__fullname__icontains=query) |
            Q(user_id__university_id__icontains=query) |
            Q(OCRID__icontains=query) |
            Q(google_scholar_id__icontains=query)
        )
        


    file_format = request.POST.get("format")

    if request.method == "POST" and request.POST.get("generate"):

        res_id = request.POST.get("researcher_id")

        researcher = Researcher.objects.get(researcher_id=res_id)
        email = researcher.user_id.email
        bio_desc = researcher.bio_description
        OCRID = researcher.OCRID
        google_sch = researcher.google_scholar_id
        publication_count = ResearchPaper.objects.filter(researcher_id=researcher).count()

        paper_titles = ResearchPaper.objects.filter(researcher_id= researcher).values_list('paper_title', flat=True)

        if file_format == "csv":
            # Create CSV response
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{researcher.user_id.fullname}_report.csv"'

            writer = csv.writer(response)

            # CSV header
            writer.writerow([
                'Researcher Name',
                'email',
                'OCRID',
                'Google Scholar ID',
                'Bio Description',
                'Total Publications'
            ])

            # CSV data
            writer.writerow([
                researcher.user_id.fullname,
                email,
                OCRID,
                google_sch,
                bio_desc,
                publication_count
            ])

            return response   # ⬅ return file, NOT render
        

        if file_format == "pdf":

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial","B",16)
            pdf.cell(0, 10, f"Research Report: {researcher.user_id.fullname}", ln=True, align='C')
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 10, f"Email: {email}", ln=True)
            pdf.cell(0, 10, f"ORCID: {OCRID}", ln=True)
            pdf.cell(0, 10, f"Google Scholar: {google_sch}", ln=True)
            pdf.cell(0, 10, f"Number of Publications: {publication_count}", ln=True)

            pdf.ln(10)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Publications:", ln=True)
            pdf.set_font("Arial", "", 12)
            for paper in paper_titles:
                    pdf.multi_cell(pdf.w - 2*pdf.l_margin, 10, f"- {paper}")
            
            response = HttpResponse( content_type="application/pdf")
            clean_filename = f"{researcher.user_id.fullname}_report.pdf".replace(" ", "_")
            response['Content-Disposition'] = f'attachment; filename="{clean_filename}"'
            pdf_output = pdf.output(dest='S')
            response.write(pdf_output)
            return response

    if request.method == "POST" and request.POST.get("faculty_gen"):


        
        filename = f"Faculty_of_Computing_Report_{timezone.now().strftime('%Y-%m-%d')}.csv"
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)

        # 2. Define the Header Row
        writer.writerow([
            'Paper ID', 
            'Research Title', 
            'Researcher', 
            'Category', 
            'Status', 
            'DOI', 
            'Total Likes', 
            'Total Bookmarks', 
            'Published Date',
            'Co-Author Count'
        ])

        # 3. Filter Papers
        # We filter papers where the linked ProgrammeCoordinator's faculty is 'Faculty of Computing'
        papers = ResearchPaper.objects.all()

        # 4. Write Data Rows
        for paper in papers:
            # Get count of co-authors for this paper
            co_author_count = paper.paper_coauthor.count()
            
            writer.writerow([
                paper.paper_id,
                paper.paper_title,
                paper.researcher_id.user_id.fullname,
                paper.paper_category,
                paper.paper_status, # Shows 'Approved' instead of 'approved'
                paper.paper_doi if paper.paper_doi else "N/A",
                paper.total_likes,
                paper.total_bookmarked,
                paper.published_date if paper.published_date else "Not Published",
                co_author_count
            ])

        return response
        

    

            

    context = {
        'coordinator' : coordinator,
        'user_name': user_name,
        'researchers': researchers,
        'researchers': researchers, #only pass researchers that match the query
        'query' : query

    }
    

    return render(request, 'coordinator/generate_report.html', context)


def researcher_directory(request):

    user_id = request.session.get('user_id')
    user_name = request.session.get('user_name')
    coordinator = ProgrammeCoordinator.objects.get(user_id__user_id=user_id)
    researchers = Researcher.objects.all()

    query = request.GET.get('q', '').strip()

    if query:
        researchers = researchers.filter(
            Q(user_id__fullname__icontains=query) |
            Q(user_id__university_id__icontains=query) |
            Q(OCRID__icontains=query) |
            Q(google_scholar_id__icontains=query)
        )

    #match_count = researchers.count()

    context = {
        'coordinator' : coordinator,
        'user_name': user_name,
        'researchers': researchers, #only pass researchers that match the query
        'query' : query,
        #"match_count" : match_count

    }



    return render(request, 'coordinator/researcher_directory.html', context)


def view_researcher_profile(request, researcher_id) :

    user_id = request.session.get('user_id')
    user_name = request.session.get('user_name')

    coordinator = ProgrammeCoordinator.objects.get(user_id__user_id=user_id)
    researcher = get_object_or_404(Researcher, researcher_id = researcher_id)
    researcher_id = researcher.researcher_id



    context = {
        'coordinator' : coordinator,
        'user_name' : user_name,
        'researcher' : researcher,
        'researcher_id' : researcher_id
    }



    return render(request, 'coordinator/view_researcher_profile.html' , context )






def user_signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # 1. Try to find an Admin first
        admin = Admin.objects.filter(email=email).first()
        if admin:
            if admin.password == password:
                request.session['user_name'] = admin.user_name
                messages.success(request, 'Admin Signed in successfully.')
                return redirect('admin_homepage')
            else:
                messages.error(request, "Invalid password.")
                return render(request, 'signin.html')

        # 2. If not admin, try to find a User
        user = User.objects.filter(email=email).first()
        if user:
            if user.password == password:
                request.session['user_name'] = user.fullname
                request.session['user_id'] = user.user_id  

                if user.role == 'researcher':
                    # Check if researcher profile exists
                    try:
                        researcher = Researcher.objects.get(user_id=user.user_id)
                        messages.success(request, 'Researcher Signed in successfully.')
                        # Redirect using the correct user_id field
                        return redirect('researcher_home', researcher_id=researcher.researcher_id)
                    except Researcher.DoesNotExist:
                        messages.warning(request, "Researcher profile missing. Please contact admin.")
                        return redirect('home')

                elif user.role == 'student':
                    messages.success(request, 'Student Signed in successfully.')
                    return redirect('home')
                

                elif user.role == 'program_coordinator':
                        try:
                            # We need the coordinator object to verify they exist, 
                            # but for the redirect, we pass the User's ID
                            coordinator_profile = ProgrammeCoordinator.objects.get(user_id=user)
                            
                            messages.success(request, 'Programme Coordinator Signed in successfully.')
                            
                            # Redirect passes the INTEGER user_id
                            return redirect('coordinator_home', user_id=user.user_id)
        
                        except ProgrammeCoordinator.DoesNotExist:
                            messages.warning(request, "Coordinator profile missing.")
                            return redirect('home')
                        
            else:
                messages.error(request, "Invalid password.")
                return render(request, 'signin.html')

        # 3. If neither admin nor user found
        messages.error(request, "Invalid email or password. Please try again.")
        return render(request, 'signin.html')

    return render(request, 'signin.html')




def research_paper_page(request):
    user_name = request.session.get('user_name', 'Guest')
    user_id = request.session.get('user_id')

    researchpapers = ResearchPaper.objects.filter(paper_status='approved').order_by('-published_date')
    is_admin = False
    researcher = None
    role = None

    if user_name != 'Guest':
        is_admin = Admin.objects.filter(user_name=user_name).exists()

    if not user_id and not is_admin:
        return redirect('signin')
    
    # Fetch user to check role
    if user_id:
        user = User.objects.filter(user_id=user_id).first()
        if user:
            role = user.role
            if role == 'researcher':
                researcher = Researcher.objects.filter(user_id=user).first()
            elif role == 'program_coordinator':
                coordinator = ProgrammeCoordinator.objects.filter(user_id=user).first()

    context = {
        'user_name': user_name,
        'is_admin': is_admin, 
        'user_id': user_id,
        'researchpapers': researchpapers,
        'role': role,
        'researcher': researcher,
        'coordinator': coordinator if 'coordinator' in locals() else None
    }

    return render(request , 'researchpaper.html', context)
    
@admin_required
def admin_page(request):
    user_name = request.session.get('user_name', 'Guest')
    return render(request , 'adminguy/admin_homepage.html', {'user_name': user_name})


#===================================== Terms and Conditions Page =====================================#

def term_condition_page(request):
    user_name_session = request.session.get('user_name', 'Guest')
    view_terms = TermsAndConditions.objects.all()
    
    is_admin = Admin.objects.filter(user_name=user_name_session).exists()

    if request.method == 'POST':
        if not is_admin:
            messages.error(request, 'You do not have permission to modify terms.')
            return redirect('term_condition_page')
            
        ruletitle = request.POST.get('ruletitle')
        ruledescription = request.POST.get('ruledescription')

        if ruletitle and ruledescription:
            TermsAndConditions.objects.create(title=ruletitle, content=ruledescription)
            messages.success(request, 'New term added successfully.')
        else:
            messages.error(request, 'Failed to add. Fields cannot be empty.')
        return redirect('term_condition_page')

    context = {
        'user_name': user_name_session,
        'view_terms': view_terms,
        'is_admin': is_admin  
    }
    return render(request, 'term_condition_page.html', context)

@require_POST
def delete_term_condition(request, term_id):
    try:
        term = TermsAndConditions.objects.get(term_id=term_id)
        term.delete()
        messages.success(request, 'Term and condition deleted successfully.')
    except TermsAndConditions.DoesNotExist:
        messages.error(request, 'Term and condition not found.')

    return redirect('term_condition_page')



@require_POST
def update_term_condition(request, term_id):

    if request.method == 'POST':
     try:
        term = TermsAndConditions.objects.get(term_id=term_id)
        new_title = request.POST.get('ruletitle')
        new_content = request.POST.get('ruledescription')

        if new_title and new_content :
            term.title = new_title
            term.content = new_content
            term.save()
            messages.success(request, 'Term and condition updated successfully.')

        else:
            messages.error(request , 'Failed to update term and condition. Please try again.')
     
     except TermsAndConditions.DoesNotExist:
        messages.error(request, 'Term and condition not found.')
        return redirect('term_condition_page')
     
    return redirect('term_condition_page')



#==============================================================================================================#

@admin_required
def announcement_page(request):
    user_name = request.session.get('user_name', 'Guest')
    announcement_list = Announcements.objects.all()

    if request.method == 'POST':
         announcement_title = request.POST.get('announcementtitle')
         announcement_description = request.POST.get('announcementdescription')
         announcement_attachment = request.FILES.get('announcementattachment')


         if announcement_title and announcement_description :
             new_announcement = Announcements(announcement_title=announcement_title , announcement_desc=announcement_description , attachment=announcement_attachment)
             new_announcement.save()
             messages.success(request, "New announcement added successfully.")
             return redirect('announcement_page')
         
         else:
                messages.error(request , 'Failed to add new announcement. Please try again.')
                return redirect('announcement_page')
            
    return render(request , 'adminguy/announcement_page.html', {'user_name': user_name , 'announcement_list': announcement_list} )




@require_POST
def delete_announcement(request, announcement_id):
    try:
        announcement = Announcements.objects.get(announcement_id=announcement_id)
        announcement.delete()
        messages.success(request, 'Announcement deleted successfully.')
    
    except Announcements.DoesNotExist:
        messages.error(request, 'Announcement not found.')


    return redirect('announcement_page')


def manage_users(request):
    user_name = request.session.get('user_name', 'Guest')
    users = User.objects.all()
    total_users = users.count()
    return render(request , 'adminguy/manage_users.html', {'user_name': user_name , 'users': users, 'total_users': total_users} )



def profile_page(request):


    user_name = request.session.get('user_name', 'Guest')

    user_data = User.objects.filter(fullname=user_name).first()

    return render(request , 'profile_page.html', {'user_name': user_name, 'user_data': user_data} )



def view_announcement_page(request , announcement_id):
    user_name = request.session.get('user_name', 'Guest')
    announcements = Announcements.objects.filter(announcement_id=announcement_id)

    is_admin = False

    if 'user_name' != 'Guest':
        is_admin = Admin.objects.filter(user_name=user_name).exists()

    return render(request, 'view_announcement.html', {'user_name': user_name , 'announcements': announcements, 'is_admin': is_admin})


# add comment to research paper 

@require_POST
def add_comment(request, paper_id):
    user_name = request.session.get('user_name', 'Guest')
    
    # 1. Use get_object_or_404 to prevent crashes
    research_paper = get_object_or_404(ResearchPaper, paper_id=paper_id)
    
    # 2. Identify the commenter (User or Admin)
    user = User.objects.filter(fullname=user_name).first()
    current_admin = Admin.objects.filter(user_name=user_name).first()

    message_desc = request.POST.get('message_desc')

    # Check if we have a valid commenter and a message
    if (user or current_admin) and message_desc:
        new_comment = Comment(
            paper_id=research_paper,
            user_id=user, # Will be None if Admin is commenting
            message_desc=message_desc,
            admin_id=current_admin # Will be None if Student is commenting
        )
        new_comment.save()

        # 3. Trigger Notification for the Paper Author
        # Logic: Don't notify the author if they are the one commenting
        author_user = research_paper.researcher_id.user_id
        if user != author_user:
            Notification.objects.create(
                user_id=author_user,
                notify_title="New Comment",
                notify_message=f"{user_name} commented on your paper: '{research_paper.paper_title}'",
                created_at=timezone.now()
            )

        messages.success(request, 'Comment added successfully.')
    else:
        messages.error(request, 'Failed to add comment. Message cannot be empty.')

    return redirect('view_research_paper', paper_id=paper_id)

def delete_comment(request, comment_id, paper_id):
    user_name = request.session.get('user_name', 'Guest')
    
    try:
        comment = get_object_or_404(Comment, comment_id=comment_id) 
        is_admin = Admin.objects.filter(user_name=user_name).exists()
        
        # Security Check: Is the user an admin OR the owner of the comment?
        if is_admin or comment.user_id.fullname == user_name:
            comment.delete()
            messages.success(request, 'Comment deleted successfully.')
        else:
            messages.error(request, 'You do not have permission to delete this comment.')
            
    except Comment.DoesNotExist:
        messages.error(request, 'Comment not found.')

    return redirect('view_research_paper', paper_id=paper_id)



def search_paper(request):
    user_name = request.session.get('user_name', 'Guest')
    query = request.GET.get('search_query', '').strip() # Added strip() to clean whitespace

    # Base queryset
    base_results = ResearchPaper.objects.filter(paper_status='approved')

    if query:
        # Search within the approved results
        researchpapers = base_results.filter(
            Q(paper_title__icontains=query) |
            Q(paper_desc__icontains=query) | 
            Q(researcher_id__user_id__fullname__icontains=query)
        ).distinct() # distinct() prevents duplicates if multiple Q conditions hit
    else:
        researchpapers = base_results

    is_admin = False
    if user_name != 'Guest':
        is_admin = Admin.objects.filter(user_name=user_name).exists()

    context = {
        'user_name': user_name,
        'is_admin': is_admin,
        'researchpapers': researchpapers,
        'search_query': query
    }
    
    return render(request, 'researchpaper.html', context)



@require_POST
def report_comment(request):
    comment_id = request.POST.get('comment_id')
    paper_id = request.POST.get('paper_id')
    reason = request.POST.get('reason')
    
    session_user_name = request.session.get('user_name', 'Guest')
    reporter_user = User.objects.filter(fullname=session_user_name).first()
    
    comment_obj = Comment.objects.get(comment_id=comment_id)
    reported_user = comment_obj.user_id 

   
    violations = Violations(
        comment=comment_obj,       
        user=reported_user,        
        reporter=reporter_user,    
        violation_type=reason,
        date_reported=timezone.now()
    )
    violations.save()

   
    notification = Notification(
        user_id=reported_user, 
        notify_title="Comment Reported",
        notify_message=f"Your comment on paper {paper_id} was reported for {reason}. Please follow community guidelines.",
        created_at=timezone.now()
    )
    notification.save()

    messages.success(request, f"Comment reported successfully.")
    return redirect('view_research_paper', paper_id=paper_id )


def your_view_name(request):
    user_name = request.session.get('user_name')
    notifications = Notification.objects.filter(user_id__fullname=user_name).order_by('-created_at')
    
    context = {
        'user_name': user_name,
        'notifications': notifications,
    }
    return render(request, 'your_template.html', context)




def notification_page(request):
    user_name = request.session.get('user_name', 'Guest')
    user_id = request.session.get('user_id')
    read_ids = request.session.get('read_notifications', [])
    
    unread_notifications = []
    read_notifications = []
    
    if user_id:
        # Get ALL notifications first to sort/split
        all_notifications = Notification.objects.filter(user_id_id=user_id).order_by('-created_at')
        
        unread_notifications = [n for n in all_notifications if n.notify_id not in read_ids]
        read_notifications = [n for n in all_notifications if n.notify_id in read_ids]
    
    return render(request, 'notification_page.html', {
        'user_name': user_name, 
        'unread_notifications': unread_notifications,
        'read_notifications': read_notifications,
        'user_id': user_id
    })


def notification_context(request):
    user_name = request.session.get('user_name', 'Guest')
    user_id = request.session.get('user_id')
    read_ids = request.session.get('read_notifications', [])
    
    notifications = [] # This will essentially be "unread_notifications" for the navbar
    
    if user_id:
        # Use user_id_id to match the DB column directly since the FK is named 'user_id'
        all_notifs = Notification.objects.filter(user_id_id=user_id).order_by('-created_at')
        # Filter out read ones
        notifications = [n for n in all_notifs if n.notify_id not in read_ids]
        
    elif user_name != 'Guest':
         # Fallback to name if id not in session
         user = User.objects.filter(fullname=user_name).first()
         if user:
             all_notifs = Notification.objects.filter(user_id=user).order_by('-created_at')
             notifications = [n for n in all_notifs if n.notify_id not in read_ids]

    return {'notifications': notifications}

def mark_notification_read(request, notify_id):
    if not request.session.get('user_id'):
         return redirect('signin')
         
    read_list = request.session.get('read_notifications', [])
    if notify_id not in read_list:
        read_list.append(notify_id)
        request.session['read_notifications'] = read_list
        request.session.modified = True
        
    # Redirect back to where the user came from, or home
    return redirect(request.META.get('HTTP_REFERER', 'researcher_home'))

@admin_required
def inspect_profile(request, user_id):
    user_name = request.session.get('user_name', 'Guest')
    # Use get_object_or_404 to ensure safe retrieval
    user_data = get_object_or_404(User, user_id=user_id)
    
    return render(request, 'profile_page.html', {
        'user_name': user_name, 
        'user_data': user_data
    })




def inventory_page(request):
    user_name = request.session.get('user_name', 'Guest')
    user_id = request.session.get('user_id')
    
    active_view = request.GET.get('view', 'all') 

    liked_papers = []
    bookmarked_papers = []
    co_authored_papers = []

    if not user_id:
        return redirect('signin')

    user = User.objects.filter(user_id=user_id).first()
    
    if user:
        if active_view in ['all', 'likes']:
            liked_entries = Likes.objects.filter(user_id=user).select_related('paper_id')
            liked_papers = [entry.paper_id for entry in liked_entries]

        if active_view in ['all', 'bookmarks']:
            bookmarked_entries = Bookmarks.objects.filter(user_id=user).select_related('paper_id')
            bookmarked_papers = [entry.paper_id for entry in bookmarked_entries]

        if active_view in ['all', 'co_authored']:
            co_authored_papers = ResearchPaper.objects.filter(paper_coauthor=user).distinct()


            
    context = {
        'user_name': user_name,
        'liked_papers': liked_papers,
        'bookmarked_papers': bookmarked_papers,
        'active_view': active_view,  # Send this to the template
        'user_id': user_id ,
        'co_authored_papers': co_authored_papers
    }
    return render(request, 'inventory_page.html', context)




def submit_fyp(request, user_id):
    session_user_id = request.session.get('user_id')

    fyp_paper = ResearchPaper.objects.filter(student_id__user_id=user_id, paper_status__in=['pending', 'approved', 'revision']).first()

    
    
    # Security Check
    if not session_user_id or int(session_user_id) != int(user_id):
        messages.error(request, "Unauthorized access.")
        return redirect('signin')

    user_name = request.session.get('user_name', 'Guest')

    if request.method == 'POST':
        fyp_title = request.POST.get('fyp_title')
        # match the name attribute in HTML
        fyp_category = request.POST.get('fyp_category', 'General') 
        fyp_desc = request.POST.get('fyp_description')
        fyp_pdf = request.FILES.get('fyp_file')
        fyp_doi = request.POST.get('fyp_doi')

        # Check required fields
        if fyp_title and fyp_desc and fyp_pdf:
            try:
                new_fyp = ResearchPaper(
                    paper_title=fyp_title,
                    paper_category=fyp_category,
                    paper_desc=fyp_desc,
                    paper_pdf=fyp_pdf,
                    paper_doi=fyp_doi,
                    paper_status='pending',
                    student_id=Student.objects.get(user_id=user_id),
                    total_likes=0,
                    total_bookmarked=0,
                    researcher_id=None
                )


                new_submission = Submissions(
                paper_id=new_fyp,
                status='pending',
                submitted_at=timezone.now()
                )

                
                new_fyp.save()
                new_submission.save()
                messages.success(request, "FYP submitted successfully!")
                return redirect('researchpaper')
            except Exception as e:
                messages.error(request, f"Error saving paper: {e}")
        else:
            messages.error(request, "Please fill in all required fields.")

    return render(request, 'submit_fyp.html', {'user_name': user_name, 'user_id': user_id , 'fyp_paper': fyp_paper})