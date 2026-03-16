from modeltranslation.translator import register, TranslationOptions

from .models import LicenseType, License

@register(LicenseType)
class LicenseTypeTranstaionOptions(TranslationOptions):
    fields = ('license_terms','description', 'detailed_description')



@register(License)
class LicenseTranstaionOptions(TranslationOptions):
    fields = ('license_terms','volume')
