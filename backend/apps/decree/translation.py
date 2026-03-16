from modeltranslation.translator import register, TranslationOptions
# from market.models import (Category, Brand, Product,
#                            Color, Characteristic, Value, VideoLessonCategory, VideoLesson)

from .models import Decree

@register(Decree)
class DecreeTranstaionOptions(TranslationOptions):
    fields = ('scan',)
