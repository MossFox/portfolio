from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    pass

class Listing(models.Model):
    name = models.CharField(max_length=64) #item name
    price = models.IntegerField() #item price
    description = models.CharField(max_length=64) #item description
    created = models.DateTimeField() #when was the item listed
    listed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings_created')
    category = models.CharField(max_length=64)
    active = models.BooleanField(default=True)
    closed = models.DateTimeField(null=True, blank=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='listings_won') # will set the winner field to NULL if the referenced user is deleted.
    image = models.ImageField(upload_to='photos/', default='/photos/default_image.png')


    def __str__ (self):
        return f"{self.id}: {self.active} {self.description}. Cost: {self.price}. Created by {self.listed_by} on {self.created}. Category: {self.category}"

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    bid = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"'{self.listing.name}' has a bid of {self.bid} by {self.user}"

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    comment = models.CharField(max_length=128)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField()

    def __str__(self):
        return f"{self.user} left a comment: '{self.comment}' for the listing '{self.listing.name}' at {self.date}"

class Watchlist(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    watching = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} watchlisted: '{self.listing}"
