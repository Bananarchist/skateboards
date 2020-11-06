from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ValidationError

class ModEvent(models.Model):
    creator = models.ForeignKey(User)
    text = models.TextField(null=False, blank=False)
    date_posted = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return "Mod: %s" % (self.text[:100])
    def clean(self):
        #maybe this stuff should be in save() or in our form stuff, perhaps even in the view
       # if self.content_object.is_removed == False or self.content_object.is_public == True:
        #    raise ValidationError('Cannot save modevent for improperly configured content_object (incorrect values for is_public or is_removed).')
        super(ModEvent, self).clean()