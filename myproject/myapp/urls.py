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
    path('update_profile/', views.update_profile, name='update_profile'),
    path('view_announcements/<int:announcement_id>/', views.view_announcement_page, name='view_announcements'),
    path('term_condition_page/', views.term_condition_page, name='term_condition_page' ),
    path('logout/', views.user_logout, name='logout'),
    path('view_research_paper/<int:paper_id>/', views.view_research_paper, name='view_research_paper'),
    path('add_comment/<int:paper_id>/', views.add_comment, name='add_comment'),
    path('delete_comment/<int:comment_id>/<int:paper_id>', views.delete_comment, name='delete_comment'),
    path('search_paper/', views.search_paper, name='search_paper'),
    path('report_comment/', views.report_comment, name='report_comment'),
    path('notifications_page/', views.notification_page, name='notification_page'),
    path('mark_notification_read/<int:notify_id>/', views.mark_notification_read, name='mark_notification_read'),
    
    

    # End General URLs

    #researcher URLs
    path('researcher/researcher_profile/<int:researcher_id>/', views.researcher_profile, name='researcher_profile'),
    path('researcher/researcher_home/<int:researcher_id>/', views.researcher_home, name='researcher_home'),
    path('researcher/researcher_upload_page/<int:researcher_id>/', views.researcher_upload_page, name='researcher_upload_page'),
    path('researchpaper/', views.research_paper_page, name='researchpaper'),
    #end researcher URLs


    # Admin URLs
    path('adminguy/admin_page/', views.admin_page, name='admin_homepage' ),
    path('adminguy/delete_term/<int:term_id>/', views.delete_term_condition, name='delete_term_condition' ),
    path('adminguy/update_term/<int:term_id>/', views.update_term_condition, name='update_term_condition' ),
    path('adminguy/announcement_page/', views.announcement_page, name='announcement_page' ),
    path('adminguy/delete_announcement/<int:announcement_id>/', views.delete_announcement, name='delete_announcement' ),
    path('adminguy/manage_users/', views.manage_users, name='manage_users' ),
    path('term_condition_page/', views.term_condition_page, name='term_condition_page' ),
    path('adminguy/inspect_profile/<int:user_id>/', views.inspect_profile, name='inspect_profile' ),
    # End Admin URLs


   # Coordinator URLs
    path('coordinator/home/<int:user_id>/', views.coordinator_home, name='coordinator_home'),
    path('coordinator/submissions/', views.submissions, name='coordinator_submissions'),
    path('coordinator/submission/<int:submission_id>/', views.submission_detail, name='submission_detail'),
    path('coordinator/researchpaper/', views.coordinator_research_paper_page, name='coorresearchpaper'),
    path('coordinator/paper/<int:paper_id>/',views.coordinator_view_research_paper,name='coordinator_view_research_paper'),
    path('coordinator/reportpage/', views.reportpage, name ='reportpage')


    
    #End Coordinator URLS
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    