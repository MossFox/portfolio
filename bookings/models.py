from django.db import models
from datetime import datetime, date, time
from django.contrib.auth.models import User

def teacher(self):
    return self.profile.teacher

User.add_to_class('teacher', teacher)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    teacher = models.BooleanField(default=False) #Is the user a teacher?

    def __str__(self):
        return f"{self.user}: Teacher: {self.teacher}"

class Fit_Class(models.Model):
    title = models.CharField(max_length=32)
    description = models.CharField(max_length=128)
    capacity = models.IntegerField()
    active = models.BooleanField(default=False)
    teacher = models.ForeignKey( User, on_delete=models.PROTECT, related_name='Teacher')
    def __str__(self):
        return f"{self.title}: {self.description}. Has capacity of {self.capacity}. Taught by {self.teacher.username}. Active: {self.active}"

class Club(models.Model):
    name = models.CharField(max_length=15)
    open = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.name}: Open {self.open}"


class Day(models.Model):
    day = models.CharField(max_length=10) #day of the class
    timestampId = models.IntegerField(default=1)
    date_today = models.DateField(default=date.today)
    def __str__(self):
        return f"{self.day}"

class Time(models.Model):
    time = models.CharField(max_length=10) #time of the class
    duration = models.IntegerField(default=60)
    timestamp = models.TimeField(default=time)
    date = models.DateField(default=date.today)

    def __str__(self):
        return f"{self.time}"

class Timetable(models.Model):
    name = models.ForeignKey(
        Fit_Class, on_delete=models.PROTECT, related_name='Class_name'
    )
    slot = models.ForeignKey(
        Time, on_delete=models.PROTECT, related_name='Class_time_slot'
    )
    day = models.ForeignKey(
        Day, on_delete=models.PROTECT, related_name='Day_of_class'
    )
    club = models.ForeignKey(
        Club, on_delete=models.SET_NULL, related_name='club_name', null=True, blank=True
    )
    capacity = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['slot', 'day', 'club', 'is_active'],
                name='unique_slot_day_club'
            ),
            models.CheckConstraint(
                check=models.Q(capacity__gte=0),
                name='positive_capacity'
            )
        ]
    def __str__(self):
        return f"{self.club.name}: {self.name.title} on {self.day} at {self.slot}. Capacity: {self.capacity}. Active in timetable: {self.is_active}"

class Booking(models.Model):
    class_name = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='Class')
    booked_in = models.ForeignKey(User, on_delete=models.CASCADE, related_name='User_is_booked')
    def __str__(self):
        return f"{self.class_name.name.title} @ {self.class_name.club.name} on {self.class_name.day} {self.class_name.slot}: User {self.booked_in} is booked in"

class Waiting_List(models.Model):
    class_name = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='Waiting_List_class')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='User_on_the_list')
    que = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.class_name.club.name}: {self.class_name.name.title} on {self.class_name.day} @ {self.class_name.slot.time}: User {self.user} is number {self.que} in the que"

class Favorites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='User_favorites')
    class_name = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='Favorite_class')

    def __str__(self):
        return f"User {self.user} likes {self.class_name.name.title} on {self.class_name.day} @ {self.class_name.slot.time}"

class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='User_history')
    club = models.CharField(max_length=10, default="test")
    fit_class = models.CharField(max_length=20, default="test")
    day = models.CharField(max_length=10, default="test")
    time = models.CharField(max_length=20, default="test")

    def __str__(self):
        return f"User {self.user} did {self.fit_class} on {self.day} @ {self.time}"

class Notification(models.Model):
    #User who gets the notification
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_user')

    #timetable class the user is on the waiting list for
    tt_class = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='fitness_class')

    timestamp = models.DateTimeField(auto_now_add=True)  #what time the user got the notification
    seen = models.BooleanField(default=False)   #new notification?.
    def __str__(self):
        return f"User {self.user} notified of {self.tt_class} booking available on {self.timestamp}. Seen: {self.seen}"

class Placeholder(models.Model):
    #What class
    tt_class = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='tt_fitness_class')
    #Token number
    token = models.ForeignKey(User, on_delete=models.CASCADE, related_name='token')
    #For which user
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='WL_user1')
    #user2
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='WL_user2', null=True, blank=True, default=None)
    #user3
    user3 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='WL_user3', null=True, blank=True, default=None)
    #created at what time
    timestamp = models.DateTimeField(auto_now_add=True)
    #open to all
    all = models.BooleanField(default=False)

    def get_user_position(self, user):
        for i in range(1, 4):
            user_attr = f'user{i}'
            #getattr dynamically accesses the attribute
            #and checks for the user in that position
            #if it finds it, it returns the position number
            if getattr(self, user_attr) == user:
                return i
        if self.all:
            return 4

    def PH_check(self, user):
        if self.user1 == user:
            return True
        elif self.user2 == user:
            return True
        elif self.user3 == user:
            return True
        else:
            return False

    def __str__(self):
        return f"Class: {self.tt_class} has a Placeholder: {self.token} for {self.user1}/ {self.user2}/ {self.user3}...... Created/ Updated on: {self.timestamp.strftime("%Y-%m-%d %H:%M:%S")}........ All notified: {self.all}"

