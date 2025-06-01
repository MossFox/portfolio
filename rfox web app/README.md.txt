# The Resting Fox
#### Video Demo:  https://youtu.be/qFTo2gJUxTM
#### Description:
My final project app is a website that is used for a massage thereapy buiseness.
On this website, the users can find the basic details of  the services provided, about section about the therapist and the contact details/ working times.
The home page of the website consists of 4 key areas: the menu (on the left on computeres, or a popout on mobile devices), the treatment information, the reviews and giftcard slot.
Treatment information displays short explanation of different treatments available to users, but also if clicked on a specific treatment, user is redirected to a page with more detailed information.
The reviews, display reviews left by previous clients in a slideshow manner. All the reviews are saved in the database and the slideshow adjusts accordingly.
The giftcard area is a means to advertise the availability of giftcards for purchase. Only registered and verified users are able to request those.

The menu consists of a list of pages available on the website: Home, About, Contact, Gift, EAF schedule, Admin (available and visible to admin user only), 
if user is new - register and log in and if the user is logged in - change password, log out. 

The home, about and contact pages are available to all and don't require users to register.
Gift and EAF schedule pages are locked behind a login. 
The users can register and then receive a verify link on their email. They then have access to the Gift and EAF pages, but can't use them until they verify.
Once they are verified, the users can then book time slots (or cancel previously booked slots) in the EAF schedule page.
On the gift page, the user can request a giftcard for someone. All they have to do is write who it's from, for who, add a gift message and state the duration of the session.
The app then adds all that information onto an image Giftcard (including a unique generated code) and sends it to the users email (and also presents it on the page for user to download)

The contact page lets users contact the therapist by filling out the form and leaving a message. The message is then sent to a affixed email address for the buiseness.
Users that aren't registered/ verified can still use the form, however they have to fill out their details manually. While registered users have less fields to fill out.

Thee Eaf page is presented as a timetable, with it's availability. Available slots are presented as green and occupied time slots are red.
Once a user books a timeslot, the database is updated and the specific time slot becomes occupied. The same user can't book in again and would have to cancel their appointment, before they can book a new one.
The choices for date and time are dynamic, as different dates have different time slots. The times adapt based on the chosen date.  

The app also has Admin user functionality, that lets the admin access a special admin page. 
On the admin page you can see the database for a list of gitcodes in the system and the list of registered users and their status.
The admin can verify the giftcodes once they're confirmed(i.e. client paid for the service), mark them as used (i.e. the client used the giftcard) and delete them.
There is also a unique code searchbar associated with the giftcard, to help find specific giftcards.  

The admin can also verify users manualy, see their email address and delete the user if necessary. 
Additionaly admin can send an email to all users from the admin page.
In the EAF page, the admin can freely book users into the timetable without it locking out, see who booked the sessions and remove users from the timetable.

The users can register/ login/ change password and if they forgot their password - go through "forgot password" process. 

There is an emailing system within the app that: sends verification emails to new users, notifies the admin that a new user registered, sends the contact us email,
sends the giftcard to the user, notifies the admin that a new giftcard was requested. 


The app adjusts the screen size on mobile apps fairly well, with a popout menu, which can be hidden. 

The html aspects are all managed by a single layout template, which is used by all pages. 

The app is adjusted in order to work on the heroku cloud platform, making it available to use online. 
All of the credentials and the path to the database are hidden withing the heroku settings.
