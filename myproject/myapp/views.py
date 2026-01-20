
from django.shortcuts import render, redirect
from django.conf import settings
from .models import Admin, User,Researcher , TermsAndConditions , Announcements
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
           fullname = request.POST.get('fullname')
           university_id = request.POST.get('university_id')
           email = request.POST.get('email')
           password = request.POST.get('password')  

           if  university_id.upper().startswith('MQA123') :
               admin = Admin(user_name=fullname , email=email , password=password)
               admin.save()
               return redirect('/admin/admin_homepage/')

           else :

             user = User(fullname=fullname , university_id=university_id , email=email , password=password)
             user.save()


           messages.success(request, 'Account created successfully. Please sign in.')
           return redirect('signin')
      

      else :
       messages.error(request , 'Invalid email or password. Please try again.')
       return render(request , 'signup.html')
      

#==================================== Researcher Parts ====================================#
def researcher_home(request, user_id):
    researcher = Researcher.objects.get(user_id=user_id)
    context = {
        'researcher': researcher
    }

    return render(request, 'researcher/researcher_home.html', context)

def researcher_upload_page(request, user_id):
    researcher = Researcher.objects.get(user_id=user_id)
    context = {
        'researcher': researcher
    }

    return render(request, 'researcher/researcher_upload_page.html', context)

def researcher_profile(request, user_id):
    researcher = Researcher.objects.get(user_id=user_id)
    context = {
        'researcher': researcher
    }

    return render(request, 'researcher/researcher_profile.html', context)
#====================================Researcher Parts End ====================================#

def user_signin(request):

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

# Check for admin or user

        admin = None
        user = None
        
# try to get admin first , if not found then get user

        try: 
            admin = Admin.objects.get(email=email)

        except Admin.DoesNotExist:

# if not admin , get user

            try: 
              user = User.objects.get(email=email)

            except User.DoesNotExist:
                messages.error(request, "Invalid email or password. Please try again.")
                return render(request, 'signin.html')
            

        except User.DoesNotExist:
            messages.error(request, "Invalid email or password. Please try again.")
            return render(request, 'signin.html')


        if admin and admin.password == password:
            request.session['user_name'] = admin.user_name
            messages.success(request, 'Admin Signed in successfully.')
            return redirect('admin_homepage')
           
        if user and user.password == password:
            request.session['user_name'] = user.fullname
            messages.success(request, 'Signed in successfully.')
            return redirect('home')
        
        
        
        messages.error(request , 'Invalid email or password. Please try again.')
        return render(request , 'signin.html')
            
       
    return render(request , 'signin.html')


        

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
