from django.contrib import admin
from models import Tag, Deck

class DeckAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'date_posted')
    field = ('title','creator')

admin.site.register(Deck)
admin.site.register(Tag)
