from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    # General URLs
    path('', views.index, name='home'),
    path('signup/', views.user_signup, name='signup'),
    path('signin/', views.user_signin, name='signin'),
    path('profile/', views.profile_page, name='profile'),
    path('avatar_register/', views.user_avatar_register, name='avatar_register'),
    # End General URLs

    #researcher URLs
    path('researcher/researcher_profile/<int:user_id>/', views.researcher_profile, name='researcher_profile'),
    path('researcher/researcher_home/<int:user_id>/', views.researcher_home, name='researcher_home'),
    path('researcher/researcher_upload_page/<int:user_id>/', views.researcher_upload_page, name='researcher_upload_page'),
    path('researchpaper/', views.research_paper_page, name='researchpaper'),
    #end researcher URLs


    # Admin URLs
    path('adminguy/admin_page/', views.admin_page, name='admin_homepage' ),
    path('adminguy/term_condition_page/', views.term_condition_page, name='term_condition_page' ),
    path('adminguy/delete_term/<int:term_id>/', views.delete_term_condition, name='delete_term_condition' ),
    path('adminguy/update_term/<int:term_id>/', views.update_term_condition, name='update_term_condition' ),
    path('adminguy/announcement_page/', views.announcement_page, name='announcement_page' ),
    path('adminguy/delete_announcement/<int:announcement_id>/', views.delete_announcement, name='delete_announcement' ),
    path('adminguy/manage_users/', views.manage_users, name='manage_users' ),
    # End Admin URLs
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    