from django.db import models
from thumbs import ImageWithThumbsField
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django import forms
from django.contrib.comments import Comment
from django.contrib.contenttypes.generic import GenericRelation
from discuss.models import Tag, Challenge, PublicSetManager, BinaryPoll
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class Deck(models.Model):
    #information
    title = models.CharField(max_length=128)
    creator = models.ForeignKey(User)
    tags = models.ManyToManyField(Tag, blank=True, null=True)
    text = models.TextField(blank=True, null=True)

    #record
    date_posted = models.DateField(auto_now_add=True)
    challenge = models.ForeignKey(Challenge, null=True, blank=True, on_delete=models.SET_NULL) #just one
    is_public = models.BooleanField(blank=True, default=True)
    is_removed = models.BooleanField(blank=True, default=False)

    #data
    deck_image = models.ImageField(upload_to="img/%Y/%m/%d")
    comments = GenericRelation(Comment, object_id_field="object_pk")
    polls = GenericRelation(BinaryPoll, object_id_field="object_id")
    deck_length_coefficient = models.SmallIntegerField()
    deck_width_coefficient = models.SmallIntegerField()

    #managers
    objects = models.Manager()
    public = PublicSetManager()

    class Meta():
        get_latest_by = 'date_posted'

    #methods
    def clean(self):
        #needs to check that any attached challenges are not expired
        if self.is_public == True and self.is_removed == True:
            raise ValidationError('Removed entries cannot also be public.')
        super(Deck, self).clean()

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('deck:view', kwargs={'pk':str(self.pk)})

