from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers = models.IntegerField(default=0)
    following = models.IntegerField(default=0)

class Post(models.Model):
    title = models.CharField(max_length=16) #post title
    post = models.CharField(max_length=1024) #Post content
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_by') #Who posted
    date_time = models.DateTimeField() #When was the post made
    like = models.IntegerField() #like amount

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "post": self.post,
            "user": self.user.username,
            "date_time": self.date_time.strftime("%b %d %Y, %I:%M %p"),
            "like": self.like,
            "user_id": self.user.id,
        }

    def __str__ (self):
        return f"{self.id}: {self.user} posted a post titled: {self.title} on {self.date_time}. {self.post}. It has {self.like} likes"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    comment = models.CharField(max_length=128) #comment
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_by') #Who commented
    date_time = models.DateTimeField() #When was the comment made
    like = models.IntegerField() #comment like ammount

    def __str__(self):
        return f"{self.id}: {self.author} commented on {self.post.title} at {self.date_time}: {self.comment}. It has {self.like} likes"

class Post_Like (models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='Post')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_like_user')
    like = models.BooleanField(default=False)

    class Meta:
        unique_together = ('post', 'user')

class Following (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    other_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_who')
    following = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'other_user')


    def __str__(self):
        return f"{self.user} is following {self.other_user} - {self.following}"

class Comment_Like (models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='Comment')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_like_user')
    like = models.BooleanField(default=False)

    class Meta:
        unique_together = ('comment', 'user')


