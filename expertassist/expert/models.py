from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal, InvalidOperation
import os
from pathlib import Path
import pandas as pd

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=100,null=True, blank=True)
    email = models.CharField(max_length=100,null=True, blank=True)

    def __str__(self):
        return self.user.username

class Task(models.Model):
  title = models.CharField(max_length=200)
  area = models.CharField(max_length=200, null=True, blank=True)
  description = models.TextField(max_length=1000)
  created = models.DateTimeField(auto_now_add=True)
  data_file = models.FileField(upload_to='uploads/', null=True, blank=True)
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  def __str__(self):
    return self.title + ' - ' + self.user.username
