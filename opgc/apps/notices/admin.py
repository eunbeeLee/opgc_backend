from django.contrib import admin

from apps.notices.forms import NoticeForm
from apps.notices.models import Notice


class NoticeAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'updated', 'title',)
    list_display_links = ('id', )
    readonly_fields = ('id', 'created', 'updated')
    fields = ('id', 'created', 'updated', 'title', 'content')
    list_per_page = 15
    form = NoticeForm


admin.site.register(Notice, NoticeAdmin)
