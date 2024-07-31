# photos/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Photo, Comment

class SignUpForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ['username', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
        return user

# class PhotoForm(forms.ModelForm):
#     class Meta:
#         model = Photo
#         fields = ['image', 'description']

class EditProfileForm(forms.ModelForm):
    password1 = forms.CharField(label='비밀번호', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label='비밀번호 확인', widget=forms.PasswordInput, required=False)

    class Meta:
        model = get_user_model()
        fields = ['username', 'phone', 'password1', 'password2']

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class MultiPhotoForm(forms.Form):
    images = MultipleFileField(label='Images', required=False)
    descriptions = forms.CharField(widget=forms.Textarea, required=False)

    def clean_images(self):
        images = self.files.getlist('images')
        if len(images) > 20:
            raise forms.ValidationError("You can upload a maximum of 20 files.")
        return images
    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class PhotoSearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=255, required=False)