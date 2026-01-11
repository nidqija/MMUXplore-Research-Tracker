from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('signup/', views.user_signup, name='signup'),
    path('signin/', views.user_signin, name='signin'),
    path('researcher/researcher_home/<int:user_id>/', views.researcher_home, name='researcher_home'),
]