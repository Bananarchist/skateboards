from django import forms
from models import Challenge, Thread, Tag, Requirement
from fields import clean_char_field

class ChallengeForm(forms.ModelForm):
    recs = forms.CharField(widget=forms.Textarea) #needs to be textarea
    news = forms.MultipleHiddenInput()
    class Meta():
        model = Challenge
    def clean_recs(self):
        return clean_char_field(self.cleaned_data, 'recs', '\n', Requirement)

class ThreadForm(forms.ModelForm):
    tags = forms.CharField() #how do we make this not required?
    class Meta():
        model = Thread
        fields = ('title', 'tags', 'text', 'comments_enabled', 'category')
    def clean_tags(self):
        return clean_char_field(self.cleaned_data, 'tags', ',', Tag)

class NewsForm(forms.ModelForm):
    tags = forms.CharField()
    ifchallenge = forms.CheckboxInput()
    class Meta():
            model = Thread
            fields = ('title', 'tags', 'text', 'comments_enabled', 'category', 'date_published')
    def clean_tags(self):
        return clean_char_field(self.cleaned_data, 'tags', ',', Tag)
