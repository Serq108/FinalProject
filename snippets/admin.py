from django.contrib import admin

# Register your models here.
from snippets.models import CourseUsers, UserProfile

@admin.register(CourseUsers)
class CourseUsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'owner')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'birthday', 'owner')
