from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe
from django.urls import path
from django.contrib import messages
from django.shortcuts import render, redirect

from apps.application.models import Application

from apps.license_template.models import LicenseType, LicenseTemplate, LicenseTemplateField, LicenseTemplateFieldValue, \
    LicenseTemplateFieldOrder, License, LicenseDefaults, Activity, LicenseAction

from .forms import ExcelImportForm
from .models import ExcelImport
from .parsers import parse_excel_and_create_models


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text')
    

@admin.register(LicenseDefaults)
class LicenseDefaultsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not LicenseDefaults.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ('pk', 'registration_number')

class LicenseTemplateFieldValueInline(admin.TabularInline):
    model = LicenseTemplateFieldValue
    extra = 1


class LicenseTemplateFieldOrderInline(admin.TabularInline):
    model = LicenseTemplateFieldOrder
    extra = 1
    fields = (
        'field',
        'order',
        "is_required",
        "min_length",
        "max_length",
        'is_static',
        'description'
    )
    sortable_field_name = 'order'


admin.site.register(LicenseAction)

@admin.register(LicenseType)
class LicenseTypeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title')
    search_fields = ('title', )
    exclude = ('license_terms', 'description', 'detailed_description')



@admin.register(LicenseTemplate)
class LisenseTemplateAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'license_type')
    list_filter = ('license_type', )
    search_fields = ('name', )
    inlines = [LicenseTemplateFieldOrderInline]

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'fields':
            kwargs["queryset"] = LicenseTemplateField.objects.all().order_by('field_order')
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(LicenseTemplateFieldValue)
class LicenseTemplateFieldValueAdmin(admin.ModelAdmin):
    list_display = ('application', 'field')
    list_filter = ('field__field_type', )
    search_fields = ('application__id', 'field__field_name')



@admin.register(LicenseTemplateField)
class LicenseTemplateFieldAdmin(admin.ModelAdmin):
    list_display = ('pk', 'field_name', 'field_type')



# --- Кастомная страница импорта ---
# @admin.register(ExcelImport)  # фиктивная модель
# class ExcelImportAdmin(admin.ModelAdmin):
#     change_list_template = "admin/excel_import.html"

#     def get_urls(self):
#         urls = super().get_urls()
#         my_urls = [
#             path('import-excel/', self.import_excel),
#         ]
#         return my_urls + urls

#     def import_excel(self, request):
#         if request.method == "POST":
#             form = ExcelImportForm(request.POST, request.FILES)
#             if form.is_valid():
#                 file = request.FILES["file"]
#                 try:
#                     parse_excel_and_create_models(file)
#                     self.message_user(request, "Данные успешно импортированы!", messages.SUCCESS)
#                 except Exception as e:
#                     self.message_user(request, f"Ошибка импорта: {e}", messages.ERROR)
#                 return redirect("..")
#         else:
#             form = ExcelImportForm()

#         context = dict(
#             self.admin_site.each_context(request),
#             form=form,
#         )
#         return render(request, "admin/excel_import_form.html", context)


def import_excel_view(request):
    if request.method == "POST":
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            try:
                parse_excel_and_create_models(file)
                messages.success(request, "Данные успешно импортированы!")
            except Exception as e:
                messages.error(request, f"Ошибка импорта: {e}")
            return redirect(request.path)
    else:
        form = ExcelImportForm()

    context = dict(
        admin.site.each_context(request),
        form=form,
    )
    return render(request, "admin/excel_import_form.html", context)

# Сохраняем оригинальный get_urls
original_get_urls = admin.site.get_urls

def custom_get_urls():
    return [
        path("license_template/import-excel/", admin.site.admin_view(import_excel_view), name="import-excel"),
    ] + original_get_urls()

admin.site.get_urls = custom_get_urls