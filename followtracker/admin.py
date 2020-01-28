from django.contrib import admin
from followtracker.models import User, Follower, Followee

class UserAdmin(admin.ModelAdmin):
	list_display = (
        '_username',
        'email',
    )
admin.site.register(User, UserAdmin)

class FollowerAdmin(admin.ModelAdmin):
	list_display = (
        'username',
        'user',
    )
admin.site.register(Follower, FollowerAdmin)

class FolloweeAdmin(admin.ModelAdmin):
	list_display = (
        'username',
        'user',
    )
admin.site.register(Followee, FolloweeAdmin)