from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Users(models.Model):
    Userobj = models.ForeignKey(User, on_delete=models.PROTECT, related_name="Userobj")
    Username = models.CharField(max_length=500,blank=False)
    Password = models.CharField(max_length=500,blank=False)
    Description = models.CharField(max_length=500,blank=False)
    Email = models.CharField(max_length=500,blank=False)
    Picture = models.FileField(blank=True)
    Friendlist = models.ManyToManyField(User, blank=True)

class Rooms(models.Model):
    Roomname = models.CharField(max_length=20, blank=False)
    Roomdescription = models.CharField(max_length=200, blank=False)
    Roomstate = models.BooleanField(default=True) 
    Roomcreator = models.ForeignKey(User, on_delete=models.PROTECT, related_name="roomcreatorobj")
    winner = models.CharField(max_length=20,blank=True)
    players = models.ManyToManyField(User, blank=True, related_name='players')
    painterName = models.CharField(max_length=20, blank=True)
    word = models.CharField(max_length=20, blank=True)
    Gamestate = models.BooleanField(default=False) 
    backgroundphoto = models.CharField(max_length=200, blank=True)
