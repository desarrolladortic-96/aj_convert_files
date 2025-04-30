from django import forms
from django.forms import ModelForm
from .models import Task
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class CustomUserCreationForm(UserCreationForm):
    
    cargo = forms.CharField(max_length=100, required=True, label="Cargo")

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'cargo', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            profile = Profile(user=user, cargo=self.cleaned_data['cargo'], email=self.cleaned_data['email'])
            profile.save()
        return user

class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'area', 'description', 'data_file']
        labels = {
            'title': 'Título',
            'area': 'Area',
            'description': 'Descripción',
            'start_time': 'Hora de inicio',
            'data_file': 'Archivo adjunto',
        }

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField