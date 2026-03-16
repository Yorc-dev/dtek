from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import  Decree


@admin.register(Decree)
class DecreeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'number', 'applicant_name', 'date_of_issue')
    exclude = ('scan',)
    
    def applicant_name(self, obj):
        return obj.aplication.applicants_full_name 
    
    applicant_name.short_description = _('ФИО заявителя')
