from discuss.fields import clean_char_field
from django import forms
from models import Deck
from discuss.models import Tag

class DeckForm(forms.ModelForm):
    tags = forms.CharField(required=False)
    deck_length_coefficient = forms.IntegerField(label="Length", initial='33')
    deck_width_coefficient = forms.IntegerField(label="Width", initial='9')
    class Meta():
        model = Deck
        fields = ('title', 'text', 'tags', 'challenge', 'deck_length_coefficient', 'deck_width_coefficient')
    def clean_tags(self):
        return clean_char_field(self.cleaned_data, 'tags', ',', Tag)
