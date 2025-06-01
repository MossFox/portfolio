from django.contrib import admin
from .models import Fit_Class, Club, Placeholder, History, Notification, Day, Time, Timetable, Favorites, Booking, Profile, Waiting_List

# Register your models here.

admin.site.register(Fit_Class)
admin.site.register(Club)
admin.site.register(Day)
admin.site.register(Time)
admin.site.register(Timetable)
admin.site.register(Booking)
admin.site.register(Profile)
admin.site.register(Waiting_List)
admin.site.register(Favorites)
admin.site.register(History)
admin.site.register(Notification)
admin.site.register(Placeholder)




admin.site.unregister(Timetable)

class TimetableAdmin(admin.ModelAdmin):
    list_display = ('name', 'slot', 'day', 'club', 'capacity')
    search_fields = ('name__title', 'club__name')
    list_filter = ('day', 'slot', 'club')

admin.site.register(Timetable, TimetableAdmin)
