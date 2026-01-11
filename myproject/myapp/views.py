
from django.shortcuts import render, redirect
from django.conf import settings
from .models import User,Researcher
from django.contrib import messages




def index(request):
    user_name = request.session.get('user_name', 'Guest')
    return render(request, 'home.html', {'user_name': user_name})



def user_signup(request):

      if request.method == 'POST':
           fullname = request.POST.get('fullname')
           university_id = request.POST.get('university_id')
           email = request.POST.get('email')
           password = request.POST.get('password')       
           user = User(fullname=fullname , university_id=university_id , email=email , password=password)
           user.save()
           messages.success(request, 'Account created successfully. Please sign in.')
           return redirect('signin')
      

      else :
       messages.error(request , 'Invalid email or password. Please try again.')
       return render(request , 'signup.html')
      

def researcher_home(request, user_id):
    researcher = Researcher.objects.get(user_id=user_id)
    context = {
        'researcher': researcher
    }

    return render(request, 'researcher/researcher_home.html/', context)
def user_signin(request):

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            messages.error(request, "Invalid email or password. Please try again.")
            return render(request, 'signin.html')

        if user.password == password:
            request.session['user_name'] = user.fullname
            messages.success(request, 'Signed in successfully.')
            return redirect('home')
            
        else:
            messages.error(request , 'Invalid email or password. Please try again.')
            return render(request , 'signin.html')
            
       
    return render(request , 'signin.html')


        
        

  



    




