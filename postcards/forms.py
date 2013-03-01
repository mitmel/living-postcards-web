from django import forms

from postcards import models

from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _

# Used in the API to valudate input
class PostcardAPIForm(forms.ModelForm):
    class Meta: 
        model = models.Postcard
        fields = ('uuid', 'author', 'title', 'description', 'privacy', 'frame_delay')

    frame_delay = forms.IntegerField(max_value = 2000, min_value = -2000)

# Used in the API to valudate input
class PhotoAPIForm(forms.ModelForm):
    class Meta: 
        model = models.Photo
        fields = ('uuid', 'author', 'postcard')

class RegisterForm(UserCreationForm):
    email = forms.EmailField(label=_('Email'))

    class Meta:
        model = models.PostcardUser
        fields = ('username','email')

    def clean_email(self):
        email = self.cleaned_data['email']
        if len(models.PostcardUser.objects.filter(email=email)):
            raise forms.ValidationError(_('This Email has already been registered.'))

        return email
