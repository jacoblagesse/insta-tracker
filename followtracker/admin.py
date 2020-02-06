from django.contrib import admin
from followtracker.models import User, Follower, Followee

class InputFilter(admin.SimpleListFilter):
    template = 'admin/input_filter.html'

    def lookups(self, request, model_admin):
        return ((),)

    def choices(self, changelist):
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )        
        yield all_choice

class UserFilter(InputFilter):
    parameter_name = 'user'
    title = ('User')

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(
                user__username__icontains=self.value()
            )

class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'create_ts',
        'last_update_ts',
    )
admin.site.register(User, UserAdmin)

class FollowerAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'user',
    )
    list_filter = (
        UserFilter,
    )
admin.site.register(Follower, FollowerAdmin)

class FolloweeAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'user',
    )
    list_filter = (
        UserFilter,
    )
admin.site.register(Followee, FolloweeAdmin)