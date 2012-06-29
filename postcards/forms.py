from django import forms

from postcards import models

from django.contrib.auth.forms import UserCreationForm

# Used in the API to valudate input
class PostcardAPIForm(forms.ModelForm):
    class Meta: 
        model = models.Postcard
        fields = ('author', 'title', 'description', 'privacy')

# Used in the API to valudate input
class PhotoAPIForm(forms.ModelForm):
    class Meta: 
        model = models.Photo
        fields = ('author', 'title', 'description', 'postcard')

class RegisterForm(UserCreationForm):
    class Meta:
        model = models.PostcardUser
        fields = ('username',)

