from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('signup/', views.user_signup, name='signup'),
    path('signin/', views.user_signin, name='signin'),
    path('researcher/researcher_home/<int:user_id>/', views.researcher_home, name='researcher_home'),
    path('researchpaper/', views.research_paper_page, name='researchpaper'),
    path('adminguy/admin_page/', views.admin_page, name='admin_homepage' ),
    path('adminguy/term_condition_page/', views.term_condition_page, name='term_condition_page' ),
    path('adminguy/delete_term/<int:term_id>/', views.delete_term_condition, name='delete_term_condition' ),
    path('adminguy/update_term/<int:term_id>/', views.update_term_condition, name='update_term_condition' ),
    path('adminguy/announcement_page/', views.announcement_page, name='announcement_page' ),
]