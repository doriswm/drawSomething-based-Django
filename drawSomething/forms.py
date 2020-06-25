from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from drawSomething.models import *

MAX_UPLOAD_SIZE = 250000

class register_form(forms.Form):
    username = forms.CharField(max_length=500,widget=forms.TextInput(attrs={'id':'id_username','size':20}))
    password = forms.CharField(max_length=500,widget=forms.PasswordInput(attrs={'id':'id_password'}))
    confirm = forms.CharField(max_length=500,widget=forms.PasswordInput(attrs={'id':'id_confirm_password'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'id':'id_description','rows':5, 'cols':65}))
    email = forms.CharField(max_length=500,widget=forms.EmailInput(attrs={'id':'id_email'}))
    picture = forms.FileField()

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password')
        password2 = cleaned_data.get('confirm')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.") 
        return cleaned_data
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")
        return username

class login_form(forms.Form):
    username = forms.CharField(max_length=20,widget=forms.TextInput(attrs={'id':'id_username'}))
    password = forms.CharField(max_length=200,widget=forms.PasswordInput(attrs={'id':'id_password'}))

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username = username, password = password)
        if not user:
            raise forms.ValidationError("Invalid username/password")

        return cleaned_data

'''
class ProfilePicture(forms.ModelForm):
    class Meta:
        model = User
        fields = ('Picture',)
'''