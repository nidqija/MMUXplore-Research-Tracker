
import datetime
from multiprocessing import context
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from pytz import timezone
from .models import Admin, ResearchPaper, Submissions, User,Researcher , TermsAndConditions , Announcements , Student, ProgrammeCoordinator , Violations , Comment , Notification

from django.shortcuts import render, redirect
from django.conf import settings
from .models import Admin, ResearchPaper, Submissions, User,Researcher , TermsAndConditions , Announcements , Student , Comment
from django.contrib import messages
from django.views.decorators.http import require_POST
from functools import wraps
from django.utils import timezone
from django.db.models import Q



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

    return render(request, 'home.html', {'user_name': user_name , 'announcements': announcements, 'is_admin': is_admin , 'new_tc_update': new_tc_update, 'research_papers': research_papers } )



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

       
        request.session['temp_user_email'] = email

        messages.success(request, 'Account created! Now let\'s set up your profile.')
        return redirect('avatar_register')

    return render(request, 'signup.html') 



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
                request.session['user_id'] = user.user_id  # Make sure this matches your User model PK
                request.session['user_name'] = user.fullname
              
                
                if user.role == 'researcher':
                    # Check if researcher profile exists
                    try:
                        researcher = Researcher.objects.get(user_id=user.user_id)
                        messages.success(request, 'Researcher Signed in successfully.')
                        # Redirect using researcher_id
                        return redirect('researcher_home', researcher_id=researcher.researcher_id)
                    except Researcher.DoesNotExist:
                        messages.warning(request, "Researcher profile missing. Please contact admin.")
                        return redirect('home')

                elif user.role == 'student':
                    messages.success(request, 'Student Signed in successfully.')
                    return redirect('home')
            else:
                messages.error(request, "Invalid password.")
                return render(request, 'signin.html')

        # 3. If neither admin nor user found
        messages.error(request, "Invalid email or password. Please try again.")
        return render(request, 'signin.html')

    return render(request, 'signin.html')

        


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
            return redirect('home')
        else:
            messages.error(request, 'Session expired. Please sign up again.')
            return redirect('user_signup')
            
    return render(request, 'user_avatar_register.html')


def user_logout(request):
    try:
        del request.session['user_name']
    except KeyError:
        pass
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
        
            ProgrammeCoordinator.objects.create(
                user_id=user,
                faculty_id='', 
                prog_name='', 
                faculty=''
            )
            

       
        request.session['temp_user_email'] = email

        messages.success(request, 'Account created! Now let\'s set up your profile.')
        return redirect('avatar_register')

    return render(request, 'signup.html') 

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
                paper.save()
                messages.success(request, 'Paper updated successfully.')
            except ResearchPaper.DoesNotExist:
                messages.error(request, 'Paper not found.')
        return redirect('researcher_home', researcher_id=researcher_id)
    
    # Get all papers by this researcher
    all_papers = ResearchPaper.objects.filter(researcher_id=researcher)
    
    # Count by status
    pending_count = all_papers.filter(paper_status='pending').count()
    revision_count = all_papers.filter(paper_status='rejected').count()
    approved_count = all_papers.filter(paper_status='approved').count()
    
    # Get papers for display
    pending_papers = all_papers.filter(paper_status='pending')
    papers = all_papers  # All papers for the "Your Papers" section

    context = {
        'researcher': researcher,
        'pending_count': pending_count,
        'revision_count': revision_count,
        'approved_count': approved_count,
        'pending_papers': pending_papers,
        'papers': papers
    }

    return render(request, 'researcher/researcher_home.html', context)


def researcher_upload_page(request, researcher_id):
    researcher = Researcher.objects.get(researcher_id=researcher_id)
    all_users = User.objects.all().exclude(role='admin')

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
    notifications = Notification.objects.filter(user_id__fullname=user_name).order_by('-created_at') if user_name != 'Guest' else []


    if user_name != 'Guest':
        is_admin = Admin.objects.filter(user_name=user_name).exists()

    return render(request , 'view_research_paper.html', {'user_name': user_name , 'research_papers': research_papers , 'researcher': researcher , 'is_admin': is_admin ,'researchname': researchname, 'comments': comments , 'notifications': notifications } )

#programme coordinator
def coordinator_home(request, user_id):
    # Correct query
    coordinator = ProgrammeCoordinator.objects.get(user_id=user_id)
    
    context = {
        'coordinator': coordinator
    }
    return render(request , 'coordinator/coordinator_home.html', context)

def submissions(request):
    # Only get submissions with status 'under review'
    submission = Submissions.objects.filter(status='pending').select_related('paper_id')
    pastSubmission = Submissions.objects.filter(status__in=['approved', 'rejected']).select_related('paper_id')
    context = {
        'submissions': submission,
        'pastSubmissions': pastSubmission
    }
    return render(request, 'coordinator/submissions.html', context)

   
    



def submission_detail(request, submission_id):
    # Get the paper and the specific submission entry linked to it

    
    # Try to find the linked submission ID for display (if it exists)
    submission = get_object_or_404(Submissions, submission_id=submission_id)
    paper = submission.paper_id   # get the related ResearchPaper
   

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            paper.paper_status = 'approved'
            submission.status = 'approved'
            messages.success(request, "Paper Approved! Submission entry removed.")
            
        elif action == 'reject':
            paper.paper_status = 'rejected'
            submission.status = 'rejected'
            messages.error(request, "Paper Rejected. Submission entry removed.")

        elif action == 'reopen':
            paper.paper_status = 'pending'
            submission.status = 'pending'
            messages.success(request, "Paper reopened for evaluation.")
            
        elif action == 'revision':
            # You might want to keep the submission entry but change status
            # For now, let's keep it pending but notify user
            messages.warning(request, "Revision requested from the researcher.")
            # Optional: paper.paper_status = 'revision_requested'
        
        paper.save() # The signal will handle deleting the submission entry if approved/rejected
        submission.save()

        return redirect('coordinator_submissions')

    context = {
        'paper': paper,
        'submission_id': submission.submission_id,
        'submission': submission
    }
    return render(request, 'coordinator/submission_detail.html', context)



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
                        coordinator = ProgrammeCoordinator.objects.get(user_id=user.user_id)
                        messages.success(request, 'Programme Coordinator Signed in successfully.')
                        return redirect('coordinator_home', user_id=user.user_id)
                    except ProgrammeCoordinator.DoesNotExist:
                        messages.warning(request, "Programme Coordinator profile missing. Please contact admin.")
                        
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
    researchpaper = ResearchPaper.objects.filter(paper_status='approved')

    researchpapers = ResearchPaper.objects.filter(paper_status='approved')
    is_admin = False

    if user_name != 'Guest':
        is_admin = Admin.objects.filter(user_name=user_name).exists()

   

    return render(request , 'researchpaper.html', {'user_name': user_name , 'is_admin': is_admin, 'user_id': user_id , 'researchpapers': researchpapers} )
    
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
        comment = Comment.objects.get(comment_id=comment_id)
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
    user_id = User.objects.filter(fullname=user_name).values_list('user_id', flat=True).first()
    
    # Filter using the field name 'user_id' directly with the ID from session
    # We use user_id=user_id because Django accepts the ID integer for FK fields
    notifications = Notification.objects.filter(user_id=user_id).order_by('-created_at')
    
    return render(request, 'notification_page.html', {
        'user_name': user_name, 
        'notifications': notifications
    })


def notification_context(request):
    user_name = request.session.get('user_name', 'Guest')
    user_id = User.objects.filter(fullname=user_name).values_list('user_id', flat=True).first()
    if user_id:
        notifications = Notification.objects.filter(user_id=user_id).order_by('-created_at')
        return {'notifications': notifications}
    return {'notifications': []}