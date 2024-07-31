# photos/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import Paginator
from .models import Photo, Comment
from .forms import MultiPhotoForm, PhotoSearchForm, SignUpForm, EditProfileForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
import datetime
import os
import zipfile
from django.http import HttpResponse, JsonResponse
from django.conf import settings


User = get_user_model()

class CustomLoginView(LoginView):
    template_name = 'photos/login.html'

    def form_invalid(self, form):
        messages.error(self.request, '로그인에 실패했습니다. 사용자 이름 또는 비밀번호를 확인하세요.')
        return super().form_invalid(form)

def photo_list(request):
    sort = request.GET.get('sort', 'latest')
    search_type = request.GET.get('search_type', 'description')
    query = request.GET.get('query', '')

    photos = Photo.objects.all()

    if search_type == 'description' and query:
        photos = photos.filter(description__icontains=query)
    elif search_type == 'username' and query:
        photos = photos.filter(uploaded_by__username__icontains=query)

    if sort == 'likes':
        photos = photos.order_by('-likes')
    else:
        photos = photos.order_by('-uploaded_at')
        
    # 각 사진의 댓글 수를 가져와 템플릿에 전달
    for photo in photos:
        photo.comment_count = photo.comments.count()

    paginator = Paginator(photos, 16)
    page_number = request.GET.get('page')
    photos = paginator.get_page(page_number)
    
    search_form = PhotoSearchForm(initial={'search_type': search_type, 'query': query})
    
    return render(request, 'photos/photo_list.html', {'photos': photos, 'search_form': search_form})

def today_photos(request):
    today = datetime.date.today()
    sort = request.GET.get('sort', 'latest')
    search_type = request.GET.get('search_type', 'description')
    query = request.GET.get('query', '')

    photos = Photo.objects.filter(uploaded_at__date=today)

    if search_type == 'description' and query:
        photos = photos.filter(description__icontains=query)
    elif search_type == 'username' and query:
        photos = photos.filter(uploaded_by__username__icontains=query)

    if sort == 'likes':
        photos = photos.order_by('-likes')
    else:
        photos = photos.order_by('-uploaded_at')
        
     # 각 사진의 댓글 수를 가져와 템플릿에 전달
    for photo in photos:
        photo.comment_count = photo.comments.count()


    paginator = Paginator(photos, 16)
    page_number = request.GET.get('page')
    photos = paginator.get_page(page_number)
    
    search_form = PhotoSearchForm(initial={'search_type': search_type, 'query': query})
    
    return render(request, 'photos/today_photos.html', {'photos': photos, 'search_form': search_form})

@login_required
def my_photos(request):
    photos = Photo.objects.filter(uploaded_by=request.user)
    
    sort = request.GET.get('sort', 'latest')
    if sort == 'likes':
        photos = Photo.objects.filter(uploaded_by=request.user).order_by('-likes')
    else:
        photos = Photo.objects.filter(uploaded_by=request.user).order_by('-uploaded_at')
        
     # 각 사진의 댓글 수를 가져와 템플릿에 전달
    for photo in photos:
        photo.comment_count = photo.comments.count()


    paginator = Paginator(photos, 16)
    page_number = request.GET.get('page')
    photos = paginator.get_page(page_number)
    
    return render(request, 'photos/my_photos.html', {'photos': photos})

@login_required
def liked_photos(request):
    sort = request.GET.get('sort', 'latest')
    search_type = request.GET.get('search_type', 'description')
    query = request.GET.get('query', '')

    photos = Photo.objects.filter(liked_by=request.user)

    if search_type == 'description' and query:
        photos = photos.filter(description__icontains=query)
    elif search_type == 'username' and query:
        photos = photos.filter(uploaded_by__username__icontains=query)

    if sort == 'likes':
        photos = photos.order_by('-likes')
    else:
        photos = photos.order_by('-uploaded_at')
        
     # 각 사진의 댓글 수를 가져와 템플릿에 전달
    for photo in photos:
        photo.comment_count = photo.comments.count()


    paginator = Paginator(photos, 16)
    page_number = request.GET.get('page')
    photos = paginator.get_page(page_number)
    
    search_form = PhotoSearchForm(initial={'search_type': search_type, 'query': query})
    
    return render(request, 'photos/liked_photos.html', {'photos': photos, 'search_form': search_form})

def photo_detail(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    if request.method == 'POST':
        if request.user.is_authenticated:
            text = request.POST.get('comment')
            if text:
                Comment.objects.create(photo=photo, user=request.user, text=text)
                return redirect('photo_detail', photo_id=photo.id)
    return render(request, 'photos/photo_detail.html', {'photo': photo})

@login_required
def upload_photo(request):
    if request.method == 'POST':
        form = MultiPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('images')
            print(files)
            descriptions = request.POST.getlist('descriptions')
            print(descriptions)
            for i, f in enumerate(files):
                description = descriptions[i] if i < len(descriptions) else ''
                photo = Photo(image=f, description=description, uploaded_by=request.user)
                photo.save()
            return redirect('photo_list')
    else:
        form = MultiPhotoForm()
    return render(request, 'photos/photo_upload.html', {'form': form})

@login_required
def download_liked_photos(request):
    if not request.user.is_authenticated:
        return redirect('login')

    photos = Photo.objects.filter(liked_by=request.user)
    
    search_type = request.GET.get('search_type')
    query = request.GET.get('query')
    
    if search_type and query:
        if search_type == 'description':
            photos = photos.filter(description__icontains=query)
        elif search_type == 'username':
            photos = photos.filter(uploaded_by__username__icontains=query)
    
    zip_filename = "liked_photos.zip"
    zip_filepath = os.path.join(settings.MEDIA_ROOT, zip_filename)

    with zipfile.ZipFile(zip_filepath, 'w') as zip_file:
        for photo in photos:
            file_path = photo.image.path
            zip_file.write(file_path, os.path.basename(file_path))

    with open(zip_filepath, 'rb') as zip_file:
        response = HttpResponse(zip_file.read(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename={zip_filename}'
        return response

@login_required
def download_selected_photos(request):
    if not request.user.is_authenticated:
        return redirect('login')

    photo_ids = request.POST.getlist('photo_ids')
    photos = Photo.objects.filter(id__in=photo_ids, liked_by=request.user)
    zip_filename = "selected_photos.zip"
    zip_filepath = os.path.join(settings.MEDIA_ROOT, zip_filename)

    with zipfile.ZipFile(zip_filepath, 'w') as zip_file:
        for photo in photos:
            file_path = photo.image.path
            zip_file.write(file_path, os.path.basename(file_path))

    with open(zip_filepath, 'rb') as zip_file:
        response = HttpResponse(zip_file.read(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename={zip_filename}'
        return response    
    
@login_required
def update_descriptions(request):
    if request.method == 'POST':
        photo_ids = request.POST.getlist('photo_ids')
        descriptions = request.POST.getlist('descriptions')
        
        for photo_id, description in zip(photo_ids, descriptions):
            try:
                photo = Photo.objects.get(id=photo_id, uploaded_by=request.user)
                if photo.description != description:
                    photo.description = description
                    photo.save()
            except Photo.DoesNotExist:
                continue
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def reset_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        phone = request.POST.get('phone')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, '비밀번호가 일치하지 않습니다.')
            return redirect('reset_password')

        user = User.objects.filter(username=username, phone=phone).first()
        if not user:
            messages.error(request, '일치하는 정보가 없습니다.')
            return redirect('reset_password')

        user.set_password(new_password)
        user.save()
        messages.success(request, '비밀번호가 성공적으로 변경되었습니다. 로그인 해주세요.')
        return redirect('login')
    return render(request, 'photos/reset_password.html')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            password1 = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')
            if password1 and password1 != password2:
                form.add_error('password2', '비밀번호가 일치하지 않습니다.')
            else:
                user = form.save(commit=False)
                if password1 and password1.strip():
                    user.set_password(password1)
                    user.save()
                    messages.success(request, '비밀번호가 성공적으로 변경되었습니다. 다시 로그인 해주세요.')
                    return redirect('login')  # 로그인 페이지로 리디렉션
                user.save()
                messages.success(request, '프로필이 성공적으로 수정되었습니다.')
                return redirect('edit_profile')  # 프로필 페이지로 리디렉션
    else:
        form = EditProfileForm(instance=request.user)
    
    return render(request, 'photos/edit_profile.html', {'form': form})

@login_required
@require_POST
def like_photo(request, photo_id):
    if request.method == 'POST':
        try:
            photo = Photo.objects.get(id=photo_id)
            if request.user in photo.liked_by.all():
                photo.liked_by.remove(request.user)
                liked = False
            else:
                photo.liked_by.add(request.user)
                liked = True
            photo.likes = photo.liked_by.count()
            photo.save()
            return JsonResponse({'success': True, 'liked': liked, 'likes': photo.likes})
        except Photo.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Photo not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            phone = form.cleaned_data.get('phone')
            user = authenticate(username=username, password=raw_password, phone=phone)
            login(request, user)
            return redirect('photo_list')
    else:
        form = SignUpForm()
    return render(request, 'photos/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('photo_list')

@login_required
def delete_photos(request):
    if request.method == 'POST':
        photo_ids = request.POST.getlist('photos')
        print(photo_ids)
        Photo.objects.filter(id__in=photo_ids, uploaded_by=request.user).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def delete_photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    if request.user == photo.uploaded_by:
        photo.delete()
        return redirect('photo_list')  # 사진 목록 페이지로 리디렉션
    else:
        return redirect('photo_detail', photo_id=photo_id)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user == comment.user:
        comment.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))