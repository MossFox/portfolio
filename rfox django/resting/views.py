from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.db import IntegrityError
import uuid  
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from PIL import Image, ImageDraw, ImageFont
from email.mime.image import MIMEImage
from django.core.mail import EmailMessage
import json



from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail


from .models import User, Schedule, Reviews, User_plus, Gift

# Create your views here.

def index(request):

    reviews = Reviews.objects.filter()
    total = Reviews.objects.count()
    return render(request, "index.html", {
        "reviews": reviews,
        "total": total
    })


def about(request):
    return render(request, "about.html")

def contact(request):
    #WORK ON THIS NEXT
    if request.method == "POST":
        name = request.POST.get("name")
        if not name:
            messages.success(request, "Please enter your name/ username")
            return redirect("/contact")
        if request.user.is_authenticated:
            user = request.user
            user_email = user.email
            if not user_email:
                messages.success(request, "Please enter your email you wish to be contacted on")
                return redirect("/contact")
        else:
            user_email = request.POST.get("user_email")
            if not user_email: 
                messages.success(request, "Please enter your email you wish to be contacted on")
                return redirect("/contact")
        subject = request.POST.get("subject")
        if not subject:
            messages.success(request,"Please enter subject")
            return redirect("/contact")                
        message = f"You have a message from {name}: '{request.POST.get('message')}'"

        if not message:
            messages.success(request,"Please enter a message")
            return redirect("/contact")
        admin_email = settings.EMAIL_HOST_USER
        a_email = EmailMessage(
                subject,
                (message),
                settings.EMAIL_HOST_USER,
                [admin_email]
            )
        a_email.send(fail_silently=False)
        return render(request, "sent.html")
    else:
        return render(request, "contact.html")

def forgot(request):
    if request.method == "POST":
        email = request.POST["email"]
        if not email:
            messages.success(request, "Enter a valid email")
            return render(request, "forgot.html")
        if User.objects.filter(email=email).exists():
            token = str(uuid.uuid4())[:8]
            ver_link = f"https://www.therestingfox.com/reset?token={token}"
            send_mail(
                'Password Reset',
                f'To reset your password - follow this link: {ver_link}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            try:
                user_plus = User_plus.objects.get(username=User.objects.get(email=email))
            except IntegrityError:
                messages.success(request, "User doesn't exist")
                return render(request, "index.html")
            user_plus.reset = token
            user_plus.save()
            messages.success(request, f"Reset email sent")
            return render(request, "forgot.html")
        else:
            return render(request, "forgot.html")
    else: 
        return render(request, "forgot.html")

@csrf_protect
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            user_plus = User_plus.objects.get(username=user)
            if user_plus.validation == "Valid":
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
            else:
                messages.success(request, "Validate your account")
                return render(request, "login.html")

        else:
            messages.success(request, "Invalid username and/or password.")
            return render(request, "login.html")
    else:
        return render(request, "login.html")
    
def logout_view(request):
    logout(request)
    messages.success(request, "You are logged out")

    return HttpResponseRedirect(reverse("index"))

@csrf_protect
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        if not username:
            messages.success(request, "Enter a username")
            return render(request, "register.html")
        if not email:
            messages.success(request, "Enter an email")
            return render(request, "register.html")


        # Ensure password matches confirmation
        password = request.POST["password"]
        if not password:
            messages.success(request, "Enter a password")
            return render(request, "register.html")    
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            messages.success(request, "Passwords must match.")
            return render(request, "register.html")

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            messages.success(request, "Username already taken")
            return render(request, "register.html")
        token = str(uuid.uuid4())[:8]
        ver_link = f"https://www.therestingfox.com/verify?token={token}"
        user_plus = User_plus.objects.create(username=user, validation=token)
        user_plus.save()
        send_mail(
            'Verify email',
            f'To verify and activate your account - follow this link: {ver_link}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        #login(request, user)
        messages.success(request, f"Verification email sent. Please activate your account to proceed")
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "register.html")

def reset(request):
    if request.method == "POST":
        token = request.POST.get('token')
        try:
            user_token = User_plus.objects.get(reset=token)
        except IntegrityError:
            messages.success(request, "Invalid token")
            return render(request, "index.html")
        # Ensure password matches confirmation
        password = request.POST["newpass"]
        if not password:
            messages.success(request, "Enter a password")
            return render(request, "register.html")    
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            messages.success(request, "Passwords must match.")
            return render(request, "register.html")

        user_token.reset = "none"
        user_token.save()
        user = user_token.username
        user.set_password(password)
        user.save()
        messages.success(request, "Password reset")
        login(request, user)
        return render(request, "index.html")
    else:
        token = request.GET.get('token')
        return render(request, "reset.html", {"token": token})

def pass_change(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            user = request.user
            username = request.POST["username"]
            if username != user.username:
                messages.success(request, f"Incorrect username")
                return render(request, "pass_change.html")
            old_pass = request.POST["password"]                
            old_check = user.check_password(old_pass)
            if not old_check:
                messages.success(request, "Incorrect password")
                return render(request, "pass_change.html")
            new_pass1 = request.POST["newpass"]
            new_pass2 = request.POST["confirmation"]
            if not new_pass1:
                messages.success(request, "Enter a new password")
                return render(request, "pass_change.html")
            if new_pass1 != new_pass2:
                messages.success(request, "Passwords didn't match")
                return render(request, "pass_change.html")
            if new_pass1 == old_pass:
                messages.success(request, "Password is the same as the old password")
                return render(request, "pass_change.html")                
            user.set_password(new_pass1)
            user.save()
            messages.success(request, "Password changed succesfully")
        return render(request, "pass_change.html")
    else:
        return render(request, "pass_change.html")

def admin_page(request):
    return render(request, "admin_page.html")

def schedule(request):
    day1 = Schedule.objects.filter(date=26).order_by("time")
    day2 = Schedule.objects.filter(date=27).order_by("time")
    day3 = Schedule.objects.filter(date=28).order_by("time")
    date = Schedule.objects.values('date').distinct().order_by('date')


    time_req = request.POST.get('time')
    date_req = request.POST.get('date')

    if request.method == "GET":
        if request.user.is_authenticated:
            user = request.user
            booking = Schedule.objects.filter(booked=user).order_by("id")
            if not booking:
                return render(request, "schedule.html", {
                    "day1": day1,
                    "day2": day2,
                    "day3": day3,
                    "date": date,
                    "user": user
                })
            else:
                booked = Schedule.objects.filter(booked=user).values('date', 'time', 'id')                
                return render(request, "schedule.html", {
                    "day1": day1,
                    "day2": day2,
                    "day3": day3,
                    "date": date,
                    "booking": booking,
                    "booked": booked,
                    "user": user
                })
        else:
            return render(request, "schedule.html", {
                    "day1": day1,
                    "day2": day2,
                    "day3": day3,
                    "date": date
            })
    else:
        if request.user.is_authenticated:
            user = request.user
            booking = Schedule.objects.filter(user=user).order_by("id")
            result = User_plus.objects.filter(username=user).values('validation').first()
            print(result)
            if not result or result['validation'] !='Valid':
                messages.success(request, "In order to book a time slot, please verify your email")
                return redirect ("/verify")
            name = request.POST.get("name")
            if name == "" or time_req == "Time" or date_req == "Date":
                if name == "":
                    messages.success(request, "Please enter your name.")
                if time_req == "Time":
                    messages.success(request, "Please choose a time slot.")
                if date_req == "Date":
                    messages.success(request, "Please choose the date.")
                return redirect ("/schedule")
            if not booking or request.user.is_staff:
                schedule_entry = Schedule.objects.get(date=date_req, time=time_req)
                if schedule_entry:
                    schedule_entry.availability = "Occupied"
                    schedule_entry.booked = name
                    schedule_entry.user = user.username
                    schedule_entry.save()
                
                return redirect ("/schedule")
            else:
                return render("schedule.html", {
                    "day1": day1,
                    "day2": day2,
                    "day3": day3
                })
        else:
            messages.success(request, "Please login to book a slot")
            return render(request, "login.html")
        
def get_times(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        selected_date = data.get('date')

        times_qs = Schedule.objects.filter(
         availability='Available',
            date=selected_date
        ).values_list('time', flat=True).order_by('time')

        # Convert QuerySet to a list
        times_list = list(times_qs)

        return JsonResponse(times_list, safe=False)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
def actions(request):
    if request.method == 'POST':
        action = request.POST.get("action")
        if action == "clear" or action == "cancel_app":
            booking_id = request.POST.get("id")
            if action == "cancel_app" and not booking_id:
                messages.success(request, "No booking found")
                return redirect ("/schedule")
            entry = Schedule.objects.get(id=booking_id)
            if entry:
                entry.availability = "Available"
                entry.booked = "False"
                entry.user = "none"
                entry.save()
            if action == "cancel_app":
                messages.success(request, "Booking cancelled successfully.")
            return redirect ("/schedule")
        elif action == "email_all":
            email_list = User.objects.filter().values('username','email')
            subject = request.POST.get("subject")
            message_template = request.POST.get("message")
            for user in email_list:
                email = EmailMessage(
                    subject,
                    (f"Hello {user['username']},\n\n{message_template}"),
                    settings.EMAIL_HOST_USER,
                    [user['email']],
                )
                email.send()
            messages.success(request, "Emails Sent to all")
            return redirect ("/admin_page")
        else:
            messages.success(request, "No action detected")
            return redirect ("/")


def verify(request):
    token = request.GET.get('token')
    user_token = User_plus.objects.get(validation=token)
    if token != user_token.validation:
        messages.success(request, "Incorrect token")
    else:
        user_token.validation = "Valid"
        user_token.save()
        user = user_token.username
        messages.success(request, "User validated succesfully")
        login(request, user)
        return render(request, "index.html")

    return render(request, "verify.html")

def gift(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        messages.success(request, "Please login to request a gift")
        return render(request, "login.html")
    if request.method == "GET":
        try:
            giftcode = Gift.objects.filter(username=user)
        except ObjectDoesNotExist:
            giftcode = None
        return render(request, "gift.html", {
            "giftcode": giftcode
        })
    else:
        try:
            is_valid = User_plus.objects.get(username=user)
        except ObjectDoesNotExist:
            is_valid = None
        if is_valid == None:
            messages.success(request, "Only logged in users can request a giftcard")
            return redirect("/login_view")
        elif is_valid.validation != "Valid":
            messages.success(request, "In order to request a giftcard, please verify your email")
            return redirect("/verify")
        else:
            giftcode = str(uuid.uuid4())[:8]
            to = request.POST.get('to')
            if to == "":
                messages.success(request,"Please enter a name")
                return redirect("/gift")
            gifter = request.POST.get("from")
            if gifter == "":
                messages.success(request,"Please enter who the gift is from")
                return redirect("/gift")
            duration = request.POST.get("duration")
            message = request.POST.get("message")
            if not message.strip():
                gift_message = f"This card grants you one session ({duration})."
            elif message:
                gift_message = message + ". " + f"This card grants you one session ({duration})."
        
            card(giftcode, gifter, to, gift_message)                        

            image_path3 = os.path.join('resting', 'static', 'images', 'giftcard.jpg')
            with open(image_path3, 'rb') as file:    
                img = MIMEImage(file.read())
            try:
                user_email = User.objects.get(username=user).email
            except ObjectDoesNotExist:
                user_email = None
                messages.success(request,"User has no email")
                return redirect("/gift")
            if user_email:
                email = EmailMessage(
                    'Copy of the giftcard',
                    (f"Hello {user},\n\n"
                        "Here is your requested giftcard. In order for the system to validate it, "
                        "contact us to discuss payment. For security reasons, we choose not to process "
                        "payments on this website. Once payment is received, we'll validate the giftcard "
                        "and notify you. If you have any questions, feel free to contact us at "
                        "restingfoxmassage@gmail.com.\n\nSincerely,\nDaniel"),
                    settings.EMAIL_HOST_USER,
                    [user_email],
                )
                # Attach the image
                with open(image_path3, 'rb') as file:
                    img = MIMEImage(file.read())
                    email.attach(img)

                # Send the email
                email.send(fail_silently=False)

                # Notify admin
                admin_email = settings.EMAIL_HOST_USER
                a_email = EmailMessage(
                    'New giftcard request',
                    (f"{user} has requested a giftcard: {giftcode} with the duration {duration}. "
                    f"They can be contacted at {user_email}"),
                    settings.EMAIL_HOST_USER,
                    [admin_email]
                )
                a_email.send(fail_silently=False)

                new_gift = Gift(
                    username=user,
                    code=giftcode,
                    status='Not Claimed',
                    validation='Not Valid',
                    duration=duration
                )
                new_gift.save()
                return render(request, "gift.html", {
                    "is_post": True,
                    "img_path": image_path3
                })
            


def card(giftcode, gifter, to, gift_message):
    image_path = os.path.join('resting', 'static', 'images', 'foxfox.jpg')
    img = Image.open(image_path)
    d = ImageDraw.Draw(img)
    
    giftcode_font = ImageFont.load_default(50)
    gifter_font = ImageFont.load_default(20)
    to_font = ImageFont.load_default(20)
    message_font = ImageFont.load_default(20)

    max_width = 600
    wrapped_text = wrap_text(gift_message, message_font, max_width, d)
    y_position = 430
    for line in wrapped_text:
        d.text((50, y_position), line, fill=(0, 0, 0), font=message_font)
        y_position += d.textbbox((0, 0), line, font=message_font)[3]

    d.text((385,275), f"{giftcode}", fill=(0, 0, 0), font=giftcode_font)
    d.text((97,373), f"{gifter}", fill=(0, 0, 0), font=gifter_font)
    d.text((70,347), f"{to}", fill=(0, 0, 0), font=to_font)

    image_path2 = os.path.join('resting', 'static', 'images', 'giftcard.jpg')
    img = img.save(image_path2)

def wrap_text(text, font, max_width, draw):
    lines = []
    words = text.split()
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    return lines

def massage(request):
    if request.method == "POST":
        massage = request.POST.get('massage')
        templates = {
            "swedish": "swedish.html",
            "specialist": "specialist.html",
            "iastm": "iastm.html"
        }
        
        if massage in templates:
            return render(request, templates[massage])
