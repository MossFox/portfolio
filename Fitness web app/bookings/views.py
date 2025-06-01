from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
import json
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.urls import reverse
from datetime import datetime, timedelta, date, time, timezone
from threading import Timer
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.db.models import Exists, OuterRef

from .models import User, Fit_Class, Notification,Placeholder, Day, History, Time, Timetable, Club, Favorites, Booking, Waiting_List, Profile


def index(request):
    club_selected = request.session.get('club_selected', None)

    try:
        club = Club.objects.get(name=club_selected)
    except ObjectDoesNotExist:
        club = None

    if club:
        timetables = list(Timetable.objects.filter(club=club).values(
            'id',
            'name__title',
            'slot__time',
            'day__day',
            'club__name'
        ))
        classes_object = list(Fit_Class.objects.all().values())
    else:
        timetables = []
        classes_object = []

    return render(request, "index.html", {
        "club_selected": club_selected,
        "timetables": json.dumps(timetables),
        "classes_object": json.dumps(classes_object)
    })

@csrf_protect
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
            return render(request, "login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

@csrf_protect
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "register.html")

def clear_session(request):
    request.session.flush()
    return JsonResponse({"message": "Session cleared"})

def get_timetable():
    timetable = Timetable.objects.get()
    return timetable

@csrf_protect
def schedule_class(time, day, fit_class):
    time = Time.objects.get(time=time)
    day = Day.objects.get(day=day)
    fit_class = Fit_Class.objects.get(title=fit_class)

    new_booking = Timetable(time=time, day=day, title=fit_class)
    new_booking.save()

@login_required
def timetable(request):
    club_selected = request.session.get('club_selected', None)
    user = request.user

    #club and classes options
    clubs = Club.objects.filter()
    fit_classes = Fit_Class.objects.filter()
    classes_object = list(Fit_Class.objects.all().values('id', 'title', 'description', 'capacity', 'active', 'teacher__username'))

    try:
        club = Club.objects.get(name=club_selected)
    except ObjectDoesNotExist:
        club = None
        print("no clubs")

    if club:
        timetables = list(Timetable.objects.filter(club=club, is_active=True).values(
            'id',
            'name__title',  # Replace 'name_field' with the actual field name
            'slot__time',  # Replace 'slot_field' with the actual field name
            'day__day',    # Replace 'day_field' with the actual field name
            'club__name',   # Replace 'club_field' with the actual field name
            'capacity'
        ))
        user_bookings = Booking.objects.filter(booked_in=user, class_name__club=club).values_list('class_name_id', flat=True)

        # Add booking status to each timetable entry
        for timetable in timetables:
            timetable['is_booked'] = timetable['id'] in user_bookings

    else:
        timetables = []
    return render (request, "timetable.html", {
        "club_selected": club_selected, #tracks the selected club
        "timetables": json.dumps(timetables), #passes over the timetable for the selected club
        "clubs": clubs, #passess over the list of clubs for the create timetable function
        "fit_classes": fit_classes, #list of classess for the same function
        "classes_object": json.dumps(classes_object) #list of classes and information about them

    })

# Profile page
@login_required
def profile(request):
    club_selected = request.session.get('club_selected', None)

    user = request.user
    favorites = list(Favorites.objects.filter(user=user).select_related('class_name', 'class_name__name', 'class_name__name__teacher', 'class_name__club', 'class_name__day', 'class_name__slot').values('class_name__name__title', 'class_name__name__description', 'class_name__name__capacity', 'class_name__name__active', 'class_name__name__teacher__username', 'class_name__club__name', 'class_name__day__date_today', 'class_name__day__day', 'class_name__slot__time'))

    for favorite in favorites:
        favorite['class_name__day__date_today'] = favorite['class_name__day__date_today'].isoformat()
    bookings = list(Booking.objects.filter(booked_in=user).select_related('class_name', 'class_name__name', 'class_name__name__teacher', 'class_name__club', 'class_name__day', 'class_name__slot').values('class_name__name__title', 'class_name__name__description', 'class_name__name__capacity', 'class_name__name__active', 'class_name__name__teacher__username', 'class_name__club__name', 'class_name__day__date_today', 'class_name__day__day', 'class_name__slot__time'))
    for booking in bookings:
        booking['class_name__day__date_today'] = booking['class_name__day__date_today'].isoformat()
    history = list(History.objects.filter(user=user).values())

    return render (request, "profile.html", {
        "club_selected": club_selected,
        "favorites": json.dumps(favorites),
        "bookings": json.dumps(bookings),
        "history": json.dumps(history)
    })

def todo(request):
    return render (request, "todo.html")

def club(request, club):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    request.session['club_selected'] = club


    return JsonResponse({"message": "Club selected", "club": club})

#Booking page
@login_required
def booking(request):
    club_selected = request.session.get('club_selected', None)

    clubs = Club.objects.filter()
    classes = Fit_Class.objects.filter()
    days = Day.objects.filter()
    times = Time.objects.filter()

    options = Timetable.objects.filter()

    return render (request, "booking.html", {
        "club_selected": club_selected,
        "clubs": clubs,
        "classes": classes,
        "days": days,
        "times": times,
        "options": options
    })


@login_required
def waitinglist (request, classId, action):
    user = request.user
    timetable_class = Timetable.objects.get(id=classId)
    #create an array of all waitlist objects for the selected class ordered by their que number
    waitlist = list(Waiting_List.objects.filter(class_name=timetable_class).order_by('que'))
    length = len(waitlist) #Length of the waitlist array

    on_list = Waiting_List.objects.filter(class_name=timetable_class, user=user).first()
    #Join the waitinglist and set the que number based on the length of the list of users booked in
    if action == "join":
        if on_list:
            print("You're already on the waitinglist")
            return JsonResponse({'status': 'on_waitlist'}, status=400)
        if waitlist:
            que = length + 1
        else:
            que = 1

        join = Waiting_List(class_name=timetable_class, user=user, que=que)
        join.save()
        #Checks if there is a placeholder with a user value of none and starts the timer to add this new user to it
        PH_none_check (request, timetable_class)
        print(f"Joined the waitinglist for class: {timetable_class}")
        return JsonResponse({'message': f'Joined the waitinglist for class: {classId}'})
    #Leave the waitinglist and update the rest of the que
    elif action == "leave":
        que = on_list.que
        try:
            PH = Placeholder.objects.filter(tt_class=timetable_class, user1=user, user2=None, user3=None).first()
            if PH:
                PH_token = PH.token
                next_on_WL = Waiting_List.objects.get(class_name=timetable_class, que=que+1)
                BK_token = Booking.objects.get(class_name=timetable_class, booked_in=PH_token)
                if BK_token and not next_on_WL:
                    BK_token.delete()
                    TT_class = Timetable.objects.get(id=timetable_class)
                    TT_class.capacity -=1
                    TT_class.save()
                    PH_update(request, timetable_class)
                    BK_update(request, timetable_class)
                    PH.delete()
                    PH_users_update(request, timetable_class, user)

                else:
                    try:
                        next_on_WL = Waiting_List.objects.get(class_name=timetable_class, que=que+1)
                        notify = Notification(tt_class=timetable_class, user=next_on_WL)
                        notify.save()
                    except Notification.DoesNotExist:
                        print("Noone next")
                    PH_users_update(request, timetable_class, user)

        except Placeholder.DoesNotExist:
            try:
                next_on_WL = Waiting_List.objects.get(class_name=timetable_class, que=que+1)
                notify = Notification(tt_class=timetable_class, user=next_on_WL)
                notify.save()
            except Notification.DoesNotExist:
                print("Noone next")
            PH_users_update(request, timetable_class, user)

            print("no placeholder")
        try:
            user_notif = Notification.objects.get(tt_class=timetable_class, user=user)
            user_notif.delete()
        except Notification.DoesNotExist:
            print("no notification")
        on_list.delete()

        updated_waitlist = Waiting_List.objects.filter(class_name=timetable_class).order_by('que')

        # Update the queue numbers for the remaining people on the list
        for index, entry in enumerate(updated_waitlist):
            entry.que = index + 1
            entry.save()
        return JsonResponse({'message': f'Left the waitinglist for class: {classId}'})


#Check if the user is on the waitinglist for classId
@login_required
def on_waitinglist (request, classId):
    user = request.user
    timetable_class = Timetable.objects.get(id=classId)
    on_list = Waiting_List.objects.filter(class_name=timetable_class, user=user)
    if on_list:
        print("You're already on the waitinglist")
        return JsonResponse({'status': 'on_waitlist', 'que_number': on_list.first().que}, status=200)
    else:
        print("Not on the list")
        return JsonResponse({'message': 'Not on the waitinglist'}, status=200)


def get_clubs(request):
    clubs = Club.objects.all()
    clubs_list = list(clubs.values('id', 'name'))
    return JsonResponse(clubs_list, safe=False)

def get_classes(request, select_club):
    user_booked = Booking.objects.filter(class_name=OuterRef('pk'),booked_in=request.user)

    classes = Timetable.objects.filter(club=select_club, capacity__lt=F('name__capacity')).annotate(user_is_booked=Exists(user_booked)).select_related('name')
    class_list = list(classes.values('id', 'name__title', 'name_id'))
    return JsonResponse(class_list, safe=False)

def get_days(request, select_club, select_class):

    days = Timetable.objects.filter(club_id=select_club, name_id=select_class).select_related('day')
    day_list = list(days.values('id', 'day__day'))
    return JsonResponse(day_list, safe=False)

def get_time(request, select_club, select_class, select_day):
    try:
        day = Day.objects.get(day=select_day)
        times = Timetable.objects.filter(club_id=select_club, name_id=select_class, day_id=day.id).select_related('slot')
        time_list = list(times.values('slot__id', 'slot__time'))
        return JsonResponse(time_list, safe=False)
    except Day.DoesNotExist:
        return JsonResponse({'error': 'Invalid day'}, status=400)

#Booking function
@login_required
def book(request, classId, action):
    print("CALLING BOOKED")
    if request.method == 'POST':
        user = request.user
        # Process the booking here

        class_slot = Timetable.objects.filter(id=classId).select_related('name') # the class slot based on its id
        class_name = class_slot.values('name__title')[0]['name__title'] #that classes name
        class_capacity = class_slot.values('capacity')[0]['capacity'] # the capacity for the slot

        fit_class = Fit_Class.objects.filter(title=class_name) # the fit_class based on the name
        class_id = Timetable.objects.get(id=classId)

        fit_class_capacity = fit_class.values('capacity')[0]['capacity'] #capacity of the fit_class
        # Is the user booked
        is_booked = Booking.objects.filter(class_name=class_id, booked_in=user).exists()
        try:
            notification = Notification.objects.get(user=user, tt_class=classId)
        except Notification.DoesNotExist:
            notification = None
            print("No notification")
        try:
            on_WL = Waiting_List.objects.get(class_name=classId, user=user)
        except Waiting_List.DoesNotExist:
            print("Not on the waitinglist")
        #If the class is full, but no token for user in PH_check
        if class_capacity == fit_class_capacity and not on_WL:
            print("Join the waiting list?")
            return JsonResponse({'message': 'Class is full. Join the Waiting list?'})
        #If already booked
        elif is_booked:
            return JsonResponse({'message': 'Already in the class'})
        #If there is a placeholder for the user
        elif notification:
            # If the action submited by the server is exit (Means booking came through the notification)
            if action == "exit":
                #Get and delete the notification for the user
                notification.delete()
                print("Placegolder found. Can be booked")
                token_check(request, user, class_id)
                return JsonResponse({'message': 'Placeholder found. Can be booked'})
            else:
                print("No action")
                return JsonResponse({'message': 'No action'})
        else:
            book = Booking(class_name = class_id, booked_in = user)
            book.save()
            class_id.capacity +=1
            class_id.save()
            return JsonResponse({'message': 'User booked in'})
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def cancel(request, classId):
    if request.method == 'POST':
        user = request.user
        # Process the booking here
        notifyAll = False

        try:
            class_id = Timetable.objects.get(id=classId)
        except Timetable.DoesNotExist:
            return JsonResponse({'error': 'Class slot not found'}, status=404)

        class_capacity = class_id.capacity

        is_booked = Booking.objects.filter(class_name=class_id, booked_in=user).exists()

        if is_booked:
            #Delete the booking
            book = Booking.objects.filter(class_name=class_id, booked_in=user).first()
            book.delete()
            #Check if anyone is on the waiting list
            WL_check = Waiting_List.objects.filter(class_name=class_id)
            #If so, runs notification and placeholder functions with the class details

            # Check if class starts soon
            time_diference = PH_class_time_check(request, classId)
            print(f"Time until class {time_diference}")
            #If there is a waiting list
            if WL_check:
                #And the class starts in less than 3h
                #notify the waitinglist
                if time_diference > timedelta(0) and time_diference < timedelta(hours=3):
                    print("Time is less than 12h")
                    notifyAll = True
                    notification(request, class_id, notifyAll)
                    class_capacity -= 1
                    class_id.capacity = class_capacity
                    class_id.save()
                #If more than 3h create a placeholder
                #run notification and placeholder functions with the class details
                else:
                    print("Time is more than 12h")
                    notification(request, class_id, notifyAll)
                    placeholder(request, class_id)
            else:
                class_capacity -= 1
                class_id.capacity = class_capacity
                class_id.save()
            return JsonResponse({'message': 'Cancelled successfully'})
        else:
            return JsonResponse({'error': 'You are not booked'}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def join_class(request):
    if request.method == 'POST':
        club_id = request.POST.get('clubs')
        if club_id is None:
            return JsonResponse({'error': 'Select a club'}, status=400)
        class_id = request.POST.get('classes')
        if class_id is None:
            return JsonResponse({'error': 'Select a class'}, status=400)
        day = request.POST.get('days')
        if day is None:
            return JsonResponse({'error': 'Select a day'}, status=400)
        time = request.POST.get('times')
        if time is None:
            return JsonResponse({'error': 'Select a time'}, status=400)
        day_object = Day.objects.get(day=day)
        time_object = Time.objects.get(id=time)

        user = request.user

        class_object = Timetable.objects.get(name=class_id, club=club_id, day=day_object, slot=time_object)
        is_booked = Booking.objects.filter(class_name=class_object, booked_in=user).exists()

        capacity = class_object.capacity

        fit_class = Fit_Class.objects.get(id=class_id)
        if class_object:
            if capacity == fit_class:
                print("Join the waiting list?")
                return JsonResponse({'message': 'Class is full. Join the Waiting list?"'})
            elif is_booked:
                return JsonResponse({'message': 'Already in the class"'})
            else:
                capacity = capacity + 1

                book = Booking(class_name = class_object, booked_in = user)
                Timetable.objects.update_or_create(name=class_id, club=club_id, day=day_object, slot=time_object, defaults={'capacity': capacity}) #updates the capacity in the class
                book.save()
                return redirect('timetable')
        else:
            return JsonResponse({'error': 'Invalid request'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def favorites(request, classId, action):
    if request.method == 'POST':
        user = request.user
        class_slot = Timetable.objects.get(id=classId)
        in_favorites = Favorites.objects.filter(user=user, class_name=class_slot)

    if action == "add":
        if in_favorites:
            print("Already added")
            return JsonResponse({'message': f'Already added'})
        else:
            favorite = Favorites(user=user, class_name=class_slot)
            favorite.save()
            print("test")
            return JsonResponse({'message': f'Added {class_slot.name} to favorites'})
    elif action == "remove":
        print("remove!")
        in_favorites.delete()
        return JsonResponse({'message': f'Removed'})


#Check if the user is on the waitinglist for classId
@login_required
def in_favorites (request, classId):
    user = request.user
    timetable_class = Timetable.objects.get(id=classId)
    on_list = Favorites.objects.filter(class_name=timetable_class, user=user)
    if on_list:
        return JsonResponse({'fav_status': 'remove'}, status=200)
    else:
        return JsonResponse({'fav_status': 'add'}, status=200)

@login_required
def teacher(request):
    user = request.user
    club_selected = request.session.get('club_selected', None)
    clubs = list(Club.objects.all().values())
    days = list(Day.objects.all().values())
    times = list(Time.objects.all().values())

#Helps convert the timestamp into a string, ensuring that both time and timestamp
# fields are properly serialized to JSON.
    for tim3 in times:
        if isinstance(tim3['timestamp'], time):
            tim3['timestamp'] = tim3['timestamp'].strftime('%H:%M:%S')
            tim3['date'] = tim3['date'].strftime('%Y-%m-%d')

    for day in days:
        if isinstance(day['date_today'], date):
            day['date_today'] = day['date_today'].strftime('%Y-%m-%d')

    users = list(User.objects.all().values('id', 'username'))

    if user:
        user_info = {
            "username": user.username,
            "id": user.id
        }

    try:
        club = Club.objects.get(name=club_selected)
    except ObjectDoesNotExist:
        club = None

    if club:
        timetables = list(Timetable.objects.filter(club=club).values(
            'id',
            'name__title',
            'slot__time',
            'day__day',
            'club__name',
            'capacity'
        ))
    else:
        timetables = []

    classes_object = list(Fit_Class.objects.all().values())
    description = list(Fit_Class.objects.all().values('id', 'title', 'description', 'capacity', 'active', 'teacher__username'))
    fit_classes = Fit_Class.objects.filter()

    return render(request, "teachers.html", {
        "user_info": user_info,
        "clubz": clubs,
        "club_selected": club_selected,
        "clubs": json.dumps(clubs),
        "timetables": json.dumps(timetables),
        "classes_object": json.dumps(classes_object),
        "description": json.dumps(description),
        "days": json.dumps(days),
        "times": json.dumps(times),
        "users": json.dumps(users),
        "fit_classes": fit_classes,
    })

@login_required
def teacher_class(request, action):
    user = request.user
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        # Book a class
        #if request.user.username == "admin":

        if action == "book":
            club_id = data.get('club')
            if club_id is None:
                return JsonResponse({'error': 'Select a club'}, status=400)
            day_id = data.get('day')
            if day_id is None:
                return JsonResponse({'error': 'Select a day'}, status=400)
            time_id = data.get('time')
            if time_id is None:
                return JsonResponse({'error': 'Select a time'}, status=400)
            class_id = data.get('class')
            if not class_id:
                class_id = data.get('Class2')
            if not class_id:
                return JsonResponse({'error': 'Add a class'}, status=400)
            overwrite = data.get('overwrite', False)
            # Create the new class booking code here
            try:
                fit_class = Fit_Class.objects.get(id=class_id)
                club = Club.objects.get(id=club_id)
                time_slot = Time.objects.get(id=time_id)
                day_obj = Day.objects.get(id=day_id)
            except ObjectDoesNotExist:
                # Handle the error
                return HttpResponse("Fit_Class, Club, time, day does not exist")
            slot_check = Timetable.objects.filter(slot=time_slot, day=day_obj, club=club).first()
            if slot_check and not overwrite:
                return JsonResponse({'message': 'Class exists'})
            #If the new class is not the same as the old one, then delete the old one to clear bookings/ favorites.
            if slot_check and slot_check.name != fit_class:
                slot_check.delete()

            Timetable.objects.update_or_create(
                slot=time_slot, day=day_obj, club=club,
                defaults={'name': fit_class}
            )
            return JsonResponse({'message': 'Class booked successfully'})

        elif action == "create":
            class_title = data.get('class_title')
            if class_title is None:
                return JsonResponse({'error': 'Select a title'}, status=400)
            description = data.get('description')
            if description is None:
                return JsonResponse({'error': 'Write a description'}, status=400)
            capacity = data.get('capacity')
            if not capacity:
                return JsonResponse({'error': 'Select a capacity'}, status=400)
            is_active = data.get('active') == 'on'
            if not is_active:
                is_active = data.get('active') == 'off'

            # ADD A CHECK TO SEE IF A CLASS WITH THE SAME TITLE EXISTS
            class_check = Fit_Class.objects.filter(title=class_title).first()
            if not class_check:
                user = request.user
                if not request.user.username == "admin":
                    user = request.user
                else:
                    user_id = data.get('users')
                    user =  User.objects.get(id=user_id)
                    print(user)
                new_class = Fit_Class(title=class_title, description=description, capacity=capacity, active=is_active, teacher=user)
                new_class.save()
                return JsonResponse({'message': 'New Class Created successfully'})
            else:
                print("Class already exists")
                return JsonResponse({'message': 'Exists'})
        #else:
            #print("User isnt admin")
            #return JsonResponse({'error': 'User isnt admin'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


#Check if the user is the teacher for the class.
@login_required
def teacher_check(request, classId):
    user = request.user
    try:
        timetable_class = Timetable.objects.get(id=classId).name.title
        teacher = Fit_Class.objects.get(title=timetable_class).teacher
    except Fit_Class.DoesNotExist:
        return JsonResponse({'error': 'Class not found'}, status=404)
    #Lets the teacher of the class or admin be able to see the delete button
    if str(user.username) == str(teacher) or str(user.username) == "admin":
        return JsonResponse({'teacher': 'True'}, status=200)
    else:
        return JsonResponse({'teacher': 'False'}, status=200)

#If the delete button was clicked - delete the class from the timetable
@login_required
def teacher_delete(request, classId, action):
    if request.method == 'POST':
        class_slot = Timetable.objects.get(id=classId)
        if action == "Delete":
            class_slot.delete()
            return JsonResponse({'message': f'Deleted'})

@login_required
def create_timetable(request):
    class_id = request.POST.get("class_title")
    club_id = request.POST.get("club")

    time_slots = ["8-9", "9-10", "10-11", "11-12", "12-13", "13-14", "14-15", "15-16", "16-17", "17-18", "18-19", "19-20", "20-21"]
    days_of_week = ["Monday", "Tuesday", "Wednsday", "Thursday", "Friday", "Saturday", "Sunday"]

    try:
        fit_class = Fit_Class.objects.get(id=class_id)
        club = Club.objects.get(id=club_id)
    except ObjectDoesNotExist:
        # Handle the error, e.g., return an error message or redirect
        return HttpResponse("Fit_Class or Club does not exist")

    for slot in time_slots: #for every slot in time slot
        time_slot = Time.objects.get(time=slot) #gets timeslot value from list
        #for every day in days list
        for day in days_of_week:
            day_obj = Day.objects.get(day=day) #gets day value
            # creates or updates the timetable at those three values
            Timetable.objects.update_or_create(
                slot=time_slot, day=day_obj, club=club,
                defaults={'name': fit_class} #and the updated value is this
            )
    return redirect('teacher')


# Notification
@login_required
def notification(request, timetable_class, notifyAll):
    # Initialize user and is_booked variables
    user = None
    users = None
    is_booked = None
    timestamp = datetime.now()
    print(notifyAll)

    # Get the list of notifications for this class
    TT_class_notif = Notification.objects.filter(tt_class=timetable_class)
    amount = TT_class_notif.count()

    # Get the waiting list for this class, ordered by queue
    WL_class = Waiting_List.objects.filter(class_name=timetable_class).order_by('que')

    # Determine which user to notify based on the number of existing notifications
    if notifyAll or amount > 2:
        print("calling this")
        users = {slot.user for slot in WL_class}
    elif amount == 0:
        user = WL_class.first().user
    elif amount == 1:
        user = WL_class[1].user if WL_class.count() > 1 else None
    elif amount == 2:
        user = WL_class[2].user if WL_class.count() > 2 else None

    # Check the users set, or if it's notifyAll
    if users:
        for person in users:
            is_booked = Booking.objects.filter(class_name=timetable_class, booked_in=person).exists()
            if not is_booked:
                notif_check = Notification.objects.filter(user=person, tt_class=timetable_class).exists()
                if not notif_check:
                    Notification(user=person, tt_class=timetable_class, timestamp=timestamp).save()
                else:
                    print("Notification exists")
    # Check if the user exists and is already booked in
    elif user:
        is_booked = Booking.objects.filter(class_name=timetable_class, booked_in=user).exists()
        if not is_booked:
            notif_check = Notification.objects.filter(user=user, tt_class=timetable_class).exists()
            if not notif_check:
                Notification(user=user, tt_class=timetable_class, timestamp=timestamp).save()
            else:
                print("Notification exists")


@login_required
def notification_check(request):
    user = request.user
    is_notified = Notification.objects.filter(user=user, seen=False)
    if is_notified:
        return JsonResponse({'notice': 'NOTFICATION'}, status=200)
    else:
        return JsonResponse({'notice': 'No notifications'}, status=200)

# Notification popup info
@login_required
def notif_board(request):
    user = request.user
    notif = Notification.objects.filter(user=user)
    new_notif = Notification.objects.filter(user=user, seen=False)
    if notif.exists():
        flag = True
        notif_list = []
        for notification in notif:
            notif_data = {
                'user': notification.user.id,
                'tt_class': {
                    'id': notification.tt_class.id,
                    'name': notification.tt_class.name.title,
                    'day': notification.tt_class.day.day,
                    'slot': notification.tt_class.slot.time,
                    'club': notification.tt_class.club.name
                },
                'timestamp': notification.timestamp,
                'seen': notification.seen
            }
            notif_list.append(notif_data)
        if new_notif.exists():
            for new in new_notif:
                new.seen=True
                new.save()
        return JsonResponse({'notif_list': notif_list, 'flag': flag}, status=200)
    else:
        flag = False
        return JsonResponse({'message': "No notifications", 'flag': flag}, status=200)


# Placeholder set-up
@login_required
def placeholder (request, class_id):
    # Checks if a placeholder for the class exists
    PH_check = Placeholder.objects.filter(tt_class=class_id)
    #Gets the amount of placeholders for the class
    size = PH_check.count()
    #If there is a placeholder:
    if PH_check:
        #If the amount of placeholders is less than 3
        if size < 3:
            #Increase size by 1 and create a token with the size number. Then set the que to size
            size += 1
            token = f"token_{size}"
            que = size
        else:
            print("3 tokens used for this class")
            class_slot = Timetable.objects.get(id=class_id.id)
            class_slot.capacity -= 1
            class_slot.save()
            return  # Exit the function if the limit is reached

    # If there isn't a placeholder create the first token and set que to 1
    else:
        token = "token_1"
        que = 1
    # Get the WL for the class at que position
    try:
        WL_user = Waiting_List.objects.get(class_name=class_id.id, que=que)
    # If it doesn't exist, get the class and reduce its capacity by 1
    except Waiting_List.DoesNotExist:
        class_slot = Timetable.objects.get(id=class_id.id)
        class_slot.capacity -= 1
        class_slot.save()
        return  # No need to create a placeholder if no user is found
    # Get the user under the token username and book it in for the class
    user = User.objects.get(username=token)
    book = Booking(class_name=class_id, booked_in=user)
    book.save()
    #Create a placeholder for the class using the token user and the WL user
    placeholder = Placeholder(tt_class=class_id, token=user, user1=WL_user.user, timestamp=datetime.now())
    placeholder.save()
    #Set a timer to call the WL_que function which adds and notifies the next users in the que
    #Timer for 30min is 1800
    #Timers set for 30 seconds for testing
    Timer(30, WL_que, [request, class_id, placeholder]).start()
    print("PH created and timer set")
    return


#The 12h before classes check. DONE ON THE HOUR
def placeholder_time_checker(request):
    now = datetime.now() # get time now
    #get time in 12 hours
    twelve_beforeClass = now + timedelta(hours=12)
    # Filter classes for the current day from now
    classes_today = Timetable.objects.filter(
        day__date_today=now.date(),
        slot__timestamp__gte=now.time()
    )
    # Filter classes for the next day until the set time.
    classes_tomorrow = Timetable.objects.filter(
        day__date_today=twelve_beforeClass.date(),
        slot__timestamp__lte=twelve_beforeClass.time()
    )
    #Joins the classes lists
    classes = classes_today | classes_tomorrow
    #For class in classes
    for CL in classes:
        #Create a users set
        users= set()
        #Get the placeholders for the class
        placeholders = Placeholder.objects.filter(tt_class=CL)
        #For each placeholder in the class
        for PH in placeholders:
            #Get that placeholders booking and delete it
            BK = Booking.objects.filter(class_name=CL, booked_in=PH.token)
            BK.delete()
            #Delete the placeholder
            PH.delete()
            #Free up the capacity slot
            CL.capacity -= 1
            CL.save()
        #Get the waiting list for the class
        CL_WL = Waiting_List.objects.filter(class_name=CL)
        #For each user on the waitinglist, add that user to the users set
        for user in CL_WL:
            users.add(user.user)
        #For each person on the users set, create a notifycation, if it didn't exist
        for person in users:
            if not Notification.objects.filter(user=person, tt_class=CL).exists():
                notify = Notification(user=person, tt_class=CL)
                notify.save()
    return JsonResponse({"message": "Check completed"})

# A time until class check. Used to check if placeholders should be created at cancelation function
def PH_class_time_check(request, TT_class_id):
    current_datetime = datetime.now()
    TT_class = Timetable.objects.get(id=TT_class_id)
    TT_class_time = TT_class.slot.timestamp
    TT_class_date = TT_class.day.date_today
    class_datetime = datetime.combine(TT_class_date, TT_class_time)
    time_difference = class_datetime - current_datetime

    time_difference = timedelta(days=time_difference.days, seconds=time_difference.seconds)

    return time_difference


#To display the time until class in JS console
def class_time_check(request, TT_class_id):
    current_datetime = datetime.now()
    TT_class = Timetable.objects.get(id=TT_class_id)
    TT_class_time = TT_class.slot.timestamp
    TT_class_date = TT_class.day.date_today
    if TT_class_date == datetime.now().date() and TT_class_time < datetime.now().time():
        TT_class_date = TT_class.day.date_today + timedelta(days=7)
    class_datetime = datetime.combine(TT_class_date, TT_class_time)
    time_difference = class_datetime - current_datetime

    total_seconds = time_difference.total_seconds()
    days = time_difference.days
    hours, remainder = divmod(total_seconds, 3600)
    hours = hours % 24  # Adjust hours to be within a 24-hour range
    minutes, _ = divmod(remainder, 60)

    return JsonResponse({"Next class in: " 'days': days, 'hours': int(hours), 'minutes': int(minutes)})



# create a manual timestamp:
# instance.timestamp = datetime(2023, 10, 1, 12, 0)


#Updates the past dates
def date_update(request):
    print("calling date_update")
    current_datetime = datetime.now()
    current_date = datetime.now().date()
    current_time = datetime.now().time()
    days_to_update = set()
    times_to_update = set()

    # Collects all unique days that need updating
    # For each timetable in all of the timetable objects
    for timetable in Timetable.objects.all():
        #Get its date and time
        class_date_day = timetable.day.date_today
        class_time = timetable.slot.timestamp
        class_date = timetable.slot.date
        #Combine them
        class_datetime = datetime.combine(class_date, class_time)
        #Check if the date is less than current date (in the past)
        if class_datetime < current_datetime:
            times_to_update.add(timetable.slot)
        #If the class_date_day isn't equal to todays date
        if class_date_day < current_date:
            #Add that timetables day into the set
            days_to_update.add(timetable.day)

    # Process each day and its associated classes
    for day in days_to_update:
        if day.date_today < current_date:
            #Create the new date for the day in the set
            new_date = day.date_today + timedelta(weeks=1)
            #Get all the classess or that day
            timetables = Timetable.objects.filter(day=day)
            #For each timetable in the timetables
            for timetable in timetables:
                #Get the list of booked users for that timetable class
                booked_users = Booking.objects.filter(class_name=timetable).values('booked_in')
                #Save the original date of the class
                original_date = timetable.day.date_today
                #For each user create a history object
                for OB_user in booked_users:
                    history = History(
                        user_id=OB_user['booked_in'],
                        club=timetable.club.name,
                        fit_class=timetable.name.title,
                        day=original_date,
                        time=timetable.slot.time
                    )
                    history.save()
                #set the timetable to inactive so we can create a new unique timetable object next
                timetable.is_active = False
                timetable.save()
                #Create the new timetable entry
                new_class = Timetable(
                    name=timetable.name,
                    slot=timetable.slot,
                    day=timetable.day,
                    club=timetable.club,
                )
                new_class.save()
                #For each class that is in a users favorites with the old timetable, change the old to the new class
                favorites = Favorites.objects.filter(class_name=timetable)
                if favorites:
                    for favor in favorites:
                        favor.class_name = new_class
                        favor.save()
                #Delete the old timetable. This cleas all the bookings, all the waitinglists, placeholders and notifications
                timetable.delete()
            #Once all the classes for the selected day are processed, updates the date
            # Update the date for the current day
            day.date_today = new_date
            day.save()
        #Process every hour in the set
    for time in times_to_update:
        if time.timestamp < current_time:
            new_date = current_datetime + timedelta(days=1)
            timetables = Timetable.objects.filter(slot=time)
            #For each timetable in the timetables
            for timetable in timetables:
                #Get the list of booked users for that timetable class
                booked_users = Booking.objects.filter(class_name=timetable).values('booked_in')
                #Save the original date of the class
                original_date = timetable.day.date_today
                #For each user create a history object
                for OB_user in booked_users:
                    history = History(
                        user_id=OB_user['booked_in'],
                        club=timetable.club.name,
                        fit_class=timetable.name.title,
                        day=original_date,
                        time=timetable.slot.time
                    )
                    history.save()
                #set the timetable to inactive so we can create a new unique timetable object next
                timetable.is_active = False
                timetable.save()
                #Create the new timetable entry
                new_class = Timetable(
                    name=timetable.name,
                    slot=timetable.slot,
                    day=timetable.day,
                    club=timetable.club,
                )
                new_class.save()
                #For each class that is in a users favorites with the old timetable, change the old to the new class
                favorites = Favorites.objects.filter(class_name=timetable)
                if favorites:
                    for favor in favorites:
                        favor.class_name = new_class
                        favor.save()
                #Delete the old timetable. This cleas all the bookings, all the waitinglists, placeholders and notifications
                timetable.delete()
            #Once all the classes for the selected day are processed, updates the date
            # Update the date for the current day
            time.date = new_date
            time.save()
        print("done the day")
    return JsonResponse({'status': 'success'})

#    print(now.replace(minute=0, second=0, microsecond=0))

def WL_que(request, class_id, placeholder):
    print("Called WL_que")
    now = datetime.now(timezone.utc)
    #Check which position in the que is the created placeholder
    PH_list = Placeholder.objects.filter(tt_class=class_id).order_by('token__username')
    i = 0
    for PH in PH_list:
        print(f"Checking PH: {PH}")
        if PH != placeholder:
            i += 1
            print("not the token")
        else:
            position = i
            print(f"found the token at {position}")
            break

    #Check if there are any slots left in the placeholder
    token = PH_token(request, placeholder)

    if token:
        if position == 0:
            waiting_list = Waiting_List.objects.filter(class_name=class_id).order_by('que')
            print("normal que")
        elif position == 1:
            waiting_list = Waiting_List.objects.filter(class_name=class_id).order_by('que')[1:]
            print("que2")
            print(f"Waiting list for que2: {waiting_list}")
        elif position == 2:
            waiting_list = Waiting_List.objects.filter(class_name=class_id).order_by('que')[2:]
            print("que3")
        print("post position")
        WL_length = waiting_list.count()
        print(f"WL_length: {WL_length}")
        if WL_length < 2:
            print("less than 2 people on the WL")
            return
        if now >= token.timestamp + timedelta(seconds=10):
            print("Timestamp condition met")
            if token.user2 is None and len(waiting_list) > 1 and waiting_list[1].user:
                print("Assigning user2")
                token.user2 = waiting_list[1].user
                print("Assigned user 2")
                if not Notification.objects.filter(user=token.user2, tt_class=class_id).exists():
                    print("A")
                    notify = Notification(user=token.user2, tt_class=class_id)
                    print("B")
                    notify.save()
                    print("Set timer 2")
                    #Timers set for 30 seconds for testing
                Timer(30, WL_que, [request, class_id, placeholder]).start()
                PH_update(request, class_id)
                print("Timer 2 set")
            elif token.user3 is None and len(waiting_list) > 2 and waiting_list[2].user:
                print("Assigning user3")
                token.user3 = waiting_list[2].user
                if not Notification.objects.filter(user=token.user3, tt_class=class_id).exists():
                    notify = Notification(user=token.user3, tt_class=class_id)
                    notify.save()
                print("Set timer3")
                #Timers set for 30 seconds for testing
                Timer(30, WL_que, [request, class_id, placeholder]).start()
                PH_update(request, class_id)
            else:
                token.all = True
                for user in waiting_list:
                    if not Notification.objects.filter(user=user.user, tt_class=class_id).exists():
                        notify = Notification(user=user.user, tt_class=class_id)
                        notify.save()
                        print("all users notified")
            token.timestamp = now
            token.save()
            print("Success")
        else:
            print("Now is less than timestamp")
    else:
        print("All slots are full")


def PH_token(request, token):
    print("Called PH_token")
    if token.user1 == None or token.user2 == None or token.user3 == None or token.all == False:
        print("returning token")
        return token
        #return JsonResponse({"message": {"id": token.id, "user": token.user.id if token.user else None, "user2": token.user2.id if token.user2 else None, "user3": token.user3.id if token.user3 else None}})
    else:
        print(f"token id {token.id} is full")
        return None
    #return JsonResponse({"message": "No token"})



# WHEN A USER GRABS A SLOT, REMOVE THEM FROM THE TOKEN (FIRST TOKEN THEYRE IN)
# THEN MOVE THE REST IN THE REMAINING TOKENS

def token_check(request, user, class_obj):
    #Get the placeholder list for class and order it by token
    PH_list = Placeholder.objects.filter(tt_class=class_obj).order_by('token')
    #Check in which PH user is lowest in que position.
    i = 5
    Pholder = None
    for PH in PH_list:
        position=PH.get_user_position(user)
        if position and position < i:
            Pholder = PH
            i = position
        if i == 4:
            Pholder = PH_list.last()
    print(i)
    print(Pholder)

    #if Pholder.token.username == "token_1":
    #1) Book user instead of the token
    print("Process PH1 logic")

    book = Booking.objects.get(class_name=class_obj, booked_in=Pholder.token)
    book.booked_in = user
    book.save()

    print("#2) Update PH users order")
    PH_users_update(request, class_obj, user)

    print("#3) Delete the user from the WL and Update the que order")
    WL_que_update(request, user, class_obj)

    print("#4) Update the booking tokens")
    BK_update(request, class_obj)

    Pholder.delete()

    print("#5) Update the Placeholder tokens")
    PH_update(request, class_obj)

    #Check if there are any placeholders left
    PH_list = Placeholder.objects.filter(tt_class=class_obj).order_by('token')
    #If not clear all the notifications for this class
    if not PH_list:
        notifications = Notification.objects.filter(tt_class=class_obj)
        for note in notifications:
            note.delete()

    return None

#Update the Placeholder tokens
def PH_update (request, class_id):
    PH_list = Placeholder.objects.filter(tt_class=class_id).order_by('token')

    #Updates the remaining tokens in order
    for i, PH in enumerate(PH_list, start=1):
        PH_user = User.objects.get(username=f"token_{i}")
        PH.token = PH_user
        PH.save()

#Update the booking tokens
def BK_update (request, class_id):
    #Get all the users that start with token_
    token_users = User.objects.filter(username__startswith="token_")
    #Get a list of bookings for the specifica class based on the users from token_users
    # __in is used to check if a field's value is in a given list or queryset.
    bookings_with_tokens = Booking.objects.filter(class_name=class_id, booked_in__in=token_users)
    for i, BT in enumerate(bookings_with_tokens, start=1):
        PH_user = User.objects.get(username=f"token_{i}")
        BT.booked_in = PH_user
        BT.save()

#Removes the booked user from the que and updates the following user que order
def WL_que_update(request, user, classId):
    #Gets the WL for the class
    Class_WL = Waiting_List.objects.filter(class_name=classId).order_by('que')
    #Length of the que
    Que_length = Class_WL.count()
    #Sets que to none
    que = None
    #For each WL object in the list, looks if the user is in the list and sets the que for that users que
    for WL in Class_WL:
        if user == WL.user:
            que = WL.que
    #Get and delete the WL slot for user
    WL_slot = Waiting_List.objects.get(user=user, class_name=classId)
    WL_slot.delete()
    #Update the positions for the rest of the que
    try:
        #While que number is less than que length
        while que <= Que_length:
            print(que)
            #Gets the next user in the que using the old users position + 1
            WL_next = Waiting_List.objects.get(class_name=classId, que=que + 1)
            #Reduces the que order for that object by 1 and save it
            WL_next.que -=1
            WL_next.save()
            #Increase the que
            que +=1
        print("Que order updated")
    except Waiting_List.DoesNotExist:
        print("Nobody on the waitinglist")

#Update the PH_users (1,2,3) based on their position in the que
def PH_users_update(request, class_id, user):
    PH_list = Placeholder.objects.filter(tt_class=class_id).order_by('token')
    try:
        class_WL = Waiting_List.objects.get(class_name=class_id, user=user)
    except Waiting_List.DoesNotExist:
        print(f"Error: User {user} is not in the waiting list for class {class_id}")
        return  # Exit the function if the user is not found in the waiting list
    que = class_WL.que #Start from the users queue position

    #Iterate through placeholders for the class
    for PH in PH_list:
        que = class_WL.que #Start from the users queue position
        # For each placeholder, check the user positions (user1, user2, user3)
        for i in range(1, 4):
            user_attr = f'user{i}'
            current_user = getattr(PH, user_attr)
            if current_user == user: #Means the user is at user{i} position
                # If the user is found, save the next on the waitinglist user in its place.
                #Get the next user on the WL
                next_WL = Waiting_List.objects.filter(class_name=class_id, que=que + 1).first()
                #If the user exists, save it as the user_attr for PH
                if next_WL:
                    setattr(PH, user_attr, next_WL.user)
                    que += 1
                else:   #If there isnt' anyone next on the WL
                    #If the user_attr is the first user of the PH, then leave the loop
                    if user_attr == "user1":
                        pass
                    else: #But if it's user2 or user3
                        setattr(PH, user_attr, None)
                while i < 3:
                    user_attr = f'user{i+1}'
                    next_WL = Waiting_List.objects.filter(class_name=class_id, que=que + 1).first()
                    if next_WL:
                        setattr(PH, user_attr, next_WL.user)
                        que += 1

                    else:   #If there isnt' anyone next on the WL
                        #If the user_attr is the first user of the PH, then leave the loop
                        if user_attr == "user1":
                            pass
                        else: #But if it's user2 or user3
                            setattr(PH, user_attr, None)
                    i +=1
        PH.save()


### Test those changes
#Check if there are non values in the placeholder tokens
def PH_none_check (request, class_id):
    try:
        PH_list = Placeholder.objects.filter(tt_class=class_id)
    except Placeholder.DoesNotExist:
        print("no PH")
        return
    for PH in PH_list:
        for i in range(1, 4):
            user_attr = f'user{i}'
            current_user = getattr(PH, user_attr)
            if current_user == None:
                #Timers set for 30 seconds for testing
                Timer(30, WL_que, [request, class_id, PH]).start()



