from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Contact
from import_export.admin import ImportExportModelAdmin

class ContactAdmin(admin.ModelAdmin):
    list_display = ('name','gender','email','phone','info')
    list_editable = ('info',)
    list_per_page = 10
    search_fields =('name','gender','email','phone','info')
    list_filter = ('gender',)


admin.site.register(Contact,ContactAdmin)
admin.site.unregister(Group)
