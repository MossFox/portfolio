from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseNotFound, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime
import json
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import User, Post, Post_Like, Following

#Pagination function
def paginate_posts(request, posts_queryset):
    #gets the page number/ by default it's 1
    page = request.GET.get('page', 1)
    paginator = Paginator(posts_queryset, 10)  # 10 posts per page

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return posts

def index(request):
    #Gets all the posts from the database and orders them
    posts = Post.objects.order_by('-date_time')
    #PAginates the posts
    paginated_posts = paginate_posts(request, posts)
    #Gets the logged in user
    user = request.user
    #Send the information to the index.html page: paginated posts and logged in user details
    return render(request, "network/index.html", {
        "posts": paginated_posts,
        "user": user
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

# new post function
def new_post (request):
    #gets logged in user details
    user = request.user
    #if user is logged in and request method is post
    if user.is_authenticated:
        if request.method == "POST":
            #gets the post and title
            post = request.POST["post"].capitalize()
            title = request.POST["title"].capitalize()
            #saves who posted and when
            listed_by = request.user
            created = datetime.now()
            #default amount of likes is 0
            likes = 0#
            # if input is empty the returns error
            if not post or not title:
                return render(request, "/", {
                    "message": "Incorrect input"
                })
            # saves the new post in the database
            new_post = Post(title=title, post=post, user=listed_by, date_time=created, like=likes)
            new_post.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/post.html")

#Post edit function, takes the post id as an argument
def post_edit(request, post_id):
    try:
        #gets the post by it's id and the logged in users credentials.
        post = Post.objects.get(user=request.user, pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    #if the request method is get loads the edit with the specific posts details
    if request.method == "GET":
        return render(request, "network/edit.html", {
            "post_id": post.id,
            "post_title": post.title,
            "post_content": post.post,
            "post_user": post.user
        })
    #If the post is submitted, gets the information from the json and parses it
    elif request.method =="POST":
        data = json.loads(request.body)
        #gets the post title and post from the data
        post.title = data["title"].capitalize()
        post.post = data["post"].capitalize()
        #then saves it in the database
        post.save()
        return JsonResponse({"success": True})

# like function, only available if the user is logged in. takes the post id as a condition
@login_required
def like(request, post_id):
    #gets the logged in user details
    user = request.user

    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    post = Post.objects.get(id=post_id)
    user_liked = Post_Like.objects.filter(user=user, post=post).first()

    if user_liked is None:
        post.like += 1
        post.save()

        liked = Post_Like(post=post, user=user, like=True)
        liked.save()

        return JsonResponse({"message": "You liked it."}, status=201)
    else:
        post.like -= 1
        post.save()

        user_liked.delete()

        return JsonResponse({"message": "You unliked it."}, status=201)

def posts(request, username=None):
    if username:
        user = User.objects.get(username=username)
        posts = Post.objects.filter(user=user).order_by('-date_time')
    else:
        posts = Post.objects.all().order_by('-date_time')

    paginated_posts = paginate_posts(request, posts)

    liked_posts = []
    user_liked = Post_Like.objects.filter(user=request.user, like=True)
    post_ids = [like.post.id for like in user_liked]
    for post in paginated_posts:
        if post.id in post_ids:
            liked_posts.append(post.id)

    posts_data = [post.serialize() for post in paginated_posts]

    return JsonResponse({
        "posts": posts_data,
        "liked_posts": liked_posts,
        "has_previous": paginated_posts.has_previous(),
        "has_next": paginated_posts.has_next()
    })

def profile(request, username):
    try:
        prof_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponseNotFound("User not found")

    loggedinuser = request.user
    following_object, _ = Following.objects.get_or_create(user=loggedinuser, other_user=prof_user)
    following = following_object.following

    # Get posts for the profile
    posts = Post.objects.filter(user=prof_user).order_by('-date_time')

    # Paginate the posts
    paginated_posts = paginate_posts(request, posts)
    #creates a list of serialized post data. Iterates over each post in
    #paginated_posts and calls the serialize method on each post to convert
    #it into a dictionary or JSON-friendly format.
    posts_data = [post.serialize() for post in paginated_posts]
    #define a list of dictionaries with information about selected user
    user_data = {
        "id": prof_user.id,
        "name": prof_user.username,
        "followers": prof_user.followers,
        "following": prof_user.following,
        "is_following": following
    }

    if request.method == "GET":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            print("AJAX request detected")

            return JsonResponse({
                "user_data": user_data,
                "posts": posts_data,
                "has_previous": paginated_posts.has_previous(),
                "has_next": paginated_posts.has_next(),
            })
        else:
            #renders the profile.html with json format data sent as context
            return render(request, "network/profile.html", {
                "user_data": json.dumps(user_data),
                "posts": json.dumps(posts_data),
                "has_previous": paginated_posts.has_previous(),
                "has_next": paginated_posts.has_next(),
            })
    # needs to be finished.
    if request.method == "PUT":
        return render(request, "network/profile.html", {
            "user_data": json.dumps(user_data),
            "posts": json.dumps(posts_data),
            "has_previous": paginated_posts.has_previous(),
            "has_next": paginated_posts.has_next(),
        })


def following(request):
    #get the loggedin user
    loggedinuser = request.user
    #get the users the user is following based on true condition
    following_users = Following.objects.filter(user=loggedinuser, following=True)
    #create an empty list
    posts = []

    #for every user in the following_users, get posts by the followerd user and add to the empty list
    for user in following_users:
        posts.extend(Post.objects.filter(user=user.other_user).order_by('-date_time'))
    print(following_users)

    # Paginate the posts
    paginated_posts = paginate_posts(request, posts)


    posts_list = [post.serialize() for post in paginated_posts]

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            "posts": posts_list,
            "has_previous": paginated_posts.has_previous(),
            "has_next": paginated_posts.has_next(),
        })
    else:
        return render(request, "network/following.html", {
            "posts": json.dumps(posts_list),
            "has_previous": paginated_posts.has_previous(),
            "has_next": paginated_posts.has_next(),
        })
