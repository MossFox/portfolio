from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Gift(models.Model):
    username = models.ForeignKey (User, on_delete=models.CASCADE)
    code = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    validation = models.CharField(max_length=255)
    duration = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.username} has code: {self.code} for duration of {self.duration}. Status: {self.status}; Validation: {self.validation}"

class User_plus(models.Model):
    username = models.OneToOneField(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    validation = models.CharField(max_length=255)
    reset = models.CharField(max_length=255, default="none")      
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User: {self.username}"

class Schedule(models.Model):
    date = models.IntegerField()
    time = models.IntegerField()
    availability = models.CharField(max_length=255) 
    booked = models.CharField(max_length=255, default="False") 
    user = models.CharField(max_length=255, default="none")
    class Meta:
        ordering = ['date', 'time'] 

    def __str__(self):
        return f"Date: {self.date} @ {self.time}. Availability: {self.availability}"
    
class Reviews(models.Model):
    review = models.CharField(max_length=1028)
    author = models.CharField(max_length=28)
    
    def __str__(self):
        return f"Review by {self.author}"