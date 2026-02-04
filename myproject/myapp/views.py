
from django.shortcuts import render, redirect
from django.conf import settings
from .models import Admin, ResearchPaper, Submissions, User,Researcher , TermsAndConditions , Announcements , Student
from django.contrib import messages
from django.views.decorators.http import require_POST
from functools import wraps



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

    is_admin = False

    if 'user_name' != 'Guest':
        is_admin = Admin.objects.filter(user_name=user_name).exists()

    return render(request, 'home.html', {'user_name': user_name , 'announcements': announcements, 'is_admin': is_admin})



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
                request.session['user_name'] = user.fullname
                
                if user.role == 'researcher':
                    # Check if researcher profile exists
                    try:
                        researcher = Researcher.objects.get(user_id=user.user_id)
                        messages.success(request, 'Researcher Signed in successfully.')
                        # Redirect using the correct user_id field
                        return redirect('researcher_home', user_id=user.user_id)
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



#==================================== Researcher Parts ====================================#
def researcher_home(request, user_id):
    researcher = Researcher.objects.get(user_id=user_id)
    pending_count = ResearchPaper.objects.filter(researcher_id=researcher, paper_status='pending').count()
    pending_papers = ResearchPaper.objects.filter(researcher_id=researcher, paper_status='pending')


    context = {
        'researcher': researcher ,
        'pending_count': pending_count ,
        'pending_papers': pending_papers
    }

    return render(request, 'researcher/researcher_home.html', context)


def researcher_upload_page(request, user_id):
    researcher = Researcher.objects.get(user_id=user_id)
    all_users = User.objects.all().exclude(role='admin')

    context = {
        'researcher': researcher,
        'all_users': all_users
    }

    if request.method == 'POST':
        paper_title = request.POST.get('paper_title')
        paper_abstract = request.POST.get('paper_abstract')
        paper_file = request.FILES.get('paper_pdf')
        paper_coauthor = request.POST.getlist('paper_coauth')



        if paper_title and paper_abstract and paper_file:
            new_paper = ResearchPaper(
                researcher_id=researcher,
                paper_title=paper_title,
                paper_desc=paper_abstract,
                paper_pdf=paper_file,
                paper_status='pending'
            )

        
            new_paper.save()


            if paper_coauthor:
                new_paper.paper_coauthor.set(paper_coauthor)

            messages.success(request, 'Research paper uploaded successfully.')
            return redirect('researcher_home', user_id=user_id)
        else:
            messages.error(request, 'All fields are required to upload a research paper.')


       

    return render(request, 'researcher/researcher_upload_page.html', context)

def researcher_profile(request, user_id):
    researcher = Researcher.objects.get(user_id=user_id)
    

    context = {
        'researcher': researcher
    }

    return render(request, 'researcher/researcher_profile.html', context)
#====================================Researcher Parts End ====================================#





def research_paper_page(request):
    user_name = request.session.get('user_name', 'Guest')
    is_admin = False

    if 'user_name' != 'Guest':
        is_admin = Admin.objects.filter(user_name=user_name).exists()


    return render(request , 'researchpaper.html', {'user_name': user_name , 'is_admin': is_admin} )      


@admin_required
def admin_page(request):
    user_name = request.session.get('user_name', 'Guest')
    return render(request , 'adminguy/admin_homepage.html', {'user_name': user_name})


#===================================== Terms and Conditions Page =====================================#

@admin_required
def term_condition_page(request):
    user_name = request.session.get('user_name', 'Guest')
    view_terms = TermsAndConditions.objects.all()


    if request.method == 'POST':
          ruletitle = request.POST.get('ruletitle')
          ruledescription = request.POST.get('ruledescription')

          if ruletitle and ruledescription :
            new_term = TermsAndConditions(title=ruletitle, content=ruledescription)
            new_term.save()

            messages.success(request, 'New term and condition added successfully.')
            return redirect('term_condition_page')
    
          else :
            messages.error(request , 'Failed to add new term and condition. Please try again.')

          return redirect('term_condition_page')

    return render(request , 'adminguy/term_condition_page.html', {'user_name': user_name , 'view_terms': view_terms} )


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