from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime
from django.db.models import Subquery, OuterRef




from .models import User, Listing, Bid, Comment, Watchlist

def checklist(request):
    return render(request, "auctions/checklist.html")

def index(request):
    highest_bid = Bid.objects.filter(listing=OuterRef('pk')).order_by('-bid').values('bid')[:1]
    # OuterRef('pk'): Refers to the primary key of the outer query (each Listing).
    # order_by('-bid'): Orders the bids in descending order.
    # values('bid')[:1]: Selects the highest bid value.
    listings = Listing.objects.filter(active=True).annotate(highest_bid=Subquery(highest_bid)).order_by('name')
    # filter(active=True): Filters listings by active status.
    # annotate(highest_bid=Subquery(highest_bid)): Adds the highest bid as an annotation to each listing.
    past = Listing.objects.filter(active=False).annotate(highest_bid=Subquery(highest_bid))
    return render(request, "auctions/index.html", {
        "listings": listings,
        "past": past
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def listing(request, listing_name):
    try:
        listing = Listing.objects.get(name=listing_name)  # Retrieve all listings
        bids = Bid.objects.filter(listing=listing)
        comments = Comment.objects.filter(listing=listing)
        user = request.user
        watched = False
        highest_bid = Bid.objects.filter(listing=listing).order_by('-bid').first()
        context = {
            "listing": listing,
            "bids": bids,
            "highest_bid": highest_bid,
            "comments": comments,
            "watched": watched
        }
        if user.is_authenticated:
            user_watchlist = Watchlist.objects.filter(listing = listing, user=user, watching=True)

    except Listing.DoesNotExist:
        return HttpResponseNotFound("Listing not found")

    if request.method == "GET":
        if user.is_authenticated:
            if user_watchlist.exists():
                watched = True
                context["watched"] = watched
        return render(request, "auctions/listing.html", context)
    else:
        action = request.POST.get('action')
        if user.is_authenticated:
            if action == "bid":
                try:
                    bid_amount = int(request.POST["bid"])
                except ValueError:
                    context["bid_message_red"] = "Incorrect Bid"
                    return render(request, "auctions/listing.html", context)

                if highest_bid is None or bid_amount > highest_bid.bid:
                    new_bid = Bid(listing=listing, bid=bid_amount, user=user)
                    new_bid.save()
                    highest_bid = Bid.objects.filter(listing=listing).order_by('-bid').first()
                    context["bid_message_green"] = "Bid successful!"
                    context["highest_bid"] = highest_bid
                    return render(request, "auctions/listing.html", context)
                else:
                    context["bid_message_red"] = "Place a higher bid"
                    return render(request, "auctions/listing.html", context)
            if action == "comment":
                comment = request.POST.get('comment')
                if comment:
                    date = datetime.now()
                    new_comment = Comment(listing=listing, comment=comment, user=user, date=date)
                    new_comment.save()
                    context["bid_message_green"] = "Commented"
                    return render(request, "auctions/listing.html", context)
                else:
                    context["bid_message_red"] = "Make a comment"
                    return render(request, "auctions/listing.html", context)
            if action == "watchlist_add":
                existing_watch = Watchlist.objects.filter(listing=listing, user=user).first()
                if existing_watch:
                    context["bid_message_red"] = "Item already on watchlist"
                else:
                    new_watch = Watchlist(listing=listing, user=user, watching=True)
                    new_watch.save()
                    context["bid_message_green"] = "Item watchlisted"
                    context["watched"] = True
                return render(request, "auctions/listing.html", context)
            if action == "watchlist_remove":
                watched = False
                Watchlist.objects.filter(listing = listing, user=user, watching=True).delete()
                context["bid_message_green"] = "Item removed"
                return render(request, "auctions/listing.html", context)
            if action == "end":
                if request.user == listing.listed_by:
                    listing.active = False
                    listing.closed = datetime.now()
                    listing.winner = highest_bid.user
                    listing.save()
                    context["bid_message_green"] = "Listing closed"
                    return render(request, "auctions/listing.html", context)
                else:
                    context["bid_message_red"] = "Not Listing owner"
                    return render(request, "auctions/listing.html", context)
        else:
            context["bid_message_red"] = "Please login to place a bid"
            return render(request, "auctions/listing.html", context)

def new_listing (request):
    user = request.user
    if user.is_authenticated:
        if request.method == "POST":
            name = request.POST["name"].capitalize()
            try:
                price = int(request.POST["price"])
            except ValueError:
                 return render(request, "auctions/new_listing.html", {
                    "message": "Price must be an integer"
                })
            description = request.POST["description"].capitalize()
            listed_by = request.user
            created = datetime.now()
            category = request.POST["category"].capitalize()
            image = request.FILES["image"]
            if not name or not price or not description or not category or not image:
                 return render(request, "auctions/new_listing.html", {
                    "message": "Incorrect input"
                })
            new_listing = Listing(name=name, price=price, description=description, created=created, listed_by=listed_by, category=category,image=image, active=True, closed=None)
            new_listing.save()
            starting_bid = Bid(listing=new_listing, bid=price, user=listed_by)
            starting_bid.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/new_listing.html")

def categories(request):
    categories = Listing.objects.values('category').distinct().order_by('category')
    return render(request, "auctions/categories.html",{
        "categories": categories,
    })


def category(request, category_name):
    categories = Listing.objects.filter(category=category_name, active=True).order_by('category')
    closed_categories = Listing.objects.filter(category=category_name, active=False).order_by('category')
    return render(request, "auctions/category.html",{
        "categories": categories,
        "category_name": category_name,
        "closed_categories": closed_categories
    })

def watchlist(request):
    user = request.user
    watchlist = Watchlist.objects.filter(user=user, watching=True).select_related('listing').order_by('listing')
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist
    })

def my_listings(request):
    user = request.user
    highest_bid = Bid.objects.filter(listing=OuterRef('pk')).order_by('-bid').values('bid')[:1]
    my_listings_active = Listing.objects.filter(listed_by=user, active=True).annotate(highest_bid=Subquery(highest_bid)).order_by('name')
    my_listings_past = Listing.objects.filter(listed_by=user, active=False).annotate(highest_bid=Subquery(highest_bid)).order_by('name')
    winner = Listing.objects.filter(winner=user).annotate(highest_bid=Subquery(highest_bid)).order_by('name')
    return render(request, "auctions/my_listings.html", {
        "my_listings_active": my_listings_active,
        "my_listings_past": my_listings_past,
        "winner": winner,
    })

