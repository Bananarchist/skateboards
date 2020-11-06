from django import forms

class SearchForm(forms.Form):
    DATE_CHOICE = 'date_posted'
    CREATOR_CHOICE = 'creator'
    TITLE_CHOICE = 'title'
    ASC_CHOICE = 'asc'
    DESC_CHOICE = 'dsc'
    fulltext = forms.CharField(max_length="100", required=False)
    tags = forms.CharField(max_length="128", required=False)
    users = forms.CharField(max_length="128", required=False)
    date = forms.DateField(required=False)
    sort = forms.ChoiceField(((DATE_CHOICE, 'Date'), (CREATOR_CHOICE, 'Creator'), (TITLE_CHOICE, 'Title')), required=False)
    order = forms.ChoiceField(((ASC_CHOICE, 'Ascending'), (DESC_CHOICE, 'Descending')), widget=forms.RadioSelect, required=False)