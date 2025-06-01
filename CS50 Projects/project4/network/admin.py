from django.contrib import admin
from .models import User, Post,Post_Like, Comment, Comment_Like, Following

# Register your models here.

admin.site.register(User)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Post_Like)
admin.site.register(Comment_Like)
admin.site.register(Following)

# Register your models here.
