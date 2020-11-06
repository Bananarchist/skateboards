from django import forms
from models import ModEvent

class ModEventForm(forms.ModelForm):
    class Meta():
        model = ModEvent
        exclude = ('date_posted', 'creator') 