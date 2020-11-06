from django import forms
from models import Tag, Requirement

def clean_char_field(cleaned_data, fieldname, sep, object_class):
    items = []
    for item in cleaned_data[fieldname].split(sep):
        item = item.rstrip().lstrip()
        if len(item) < 1:
            continue
        items.append(object_class.objects.get_or_create(text=item)[0])
    return items

