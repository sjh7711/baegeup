# photolist/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from photos import views as photo_views
from django.contrib.auth import views as auth_views
from .views import CustomLoginView

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('signup/', photo_views.signup, name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('', photo_views.photo_list, name='photo_list'),
    path('my_photos/', photo_views.my_photos, name='my_photos'),
    path('today/', photo_views.today_photos, name='today_photos'),
    path('liked_photos/', photo_views.liked_photos, name='liked_photos'),
    path('photo/<int:photo_id>/', photo_views.photo_detail, name='photo_detail'),
    
    path('upload/', photo_views.upload_photo, name='upload_photo'),
    path('download_liked_photos/', photo_views.download_liked_photos, name='download_liked_photos'),
    path('download_selected_photos/', photo_views.download_selected_photos, name='download_selected_photos'),
    
    path('update_descriptions/', photo_views.update_descriptions, name='update_descriptions'),
    path('edit_profile/', photo_views.edit_profile, name='edit_profile'),
    path('reset_password/', photo_views.reset_password, name='reset_password'),

    path('like_photo/<int:photo_id>/', photo_views.like_photo, name='like_photo'),
    path('comment/delete/<int:comment_id>/', photo_views.delete_comment, name='delete_comment'),
    path('delete_photos/', photo_views.delete_photos, name='delete_photos'),
    path('photo/<int:photo_id>/delete/', photo_views.delete_photo, name='delete_photo'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
