from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models.signals import post_delete
from django.contrib.comments import Comment
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericRelation
from django.core.exceptions import ValidationError
from django.contrib.contenttypes import generic
from datetime import datetime
from django.utils.timezone import now, make_aware, utc

class ThreadManager(models.Manager):
    def get_by_natural_key(self, title, date_posted):
        return self.get(title=title, date_posted=date_posted)

class PublicSetManager(ThreadManager):
    def get_query_set(self):
        return super(PublicSetManager, self).get_query_set().filter(is_public=True, is_removed=False)

class TagManager(models.Manager):
    def get_by_natural_key(self, text):
        return self.get(text=text)

class CategoryManager(models.Manager):
    def get_by_natural_key(self, title):
        return self.get(title=title)

class RequirementManager(models.Manager):
    def get_by_natural_key(self, text):
        return self.get(text=text)

class BinaryPollManager(models.Manager):
    def get_by_natural_key(self, question, object_id, content_type):
        return self.get(question=question, object_id=object_id, content_type=content_type)



class Tag(models.Model):
    text = models.CharField(max_length=64, unique=True)
    objects = TagManager()
    def __unicode__(self):
        return self.text
    def clean(self):
        if not self.text:
            raise forms.ValidationError('Requirement cannot have empty text')
        super(Tag, self).clean()
    def get_absolute_url(self):
        pass
    def natural_key(self):
        return self.text

class Category(models.Model):
    title = models.CharField(max_length=128, unique=True)
    description = models.TextField()
    restricted = models.CharField(max_length=128, blank=True, null=True) #permission string to restrict access
    objects = CategoryManager()
    def clean(self):
        if not self.title.lstrip():
            raise forms.ValidationError('Category must have nonempty title')
        if not self.description.lstrip():
            raise forms.ValidationError('Category must have nonempty description')
        super(Category, self).clean()
    def __unicode__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('forum_view', kwargs={'pk':str(self.pk)})
    def natural_key(self):
        return self.title

class Thread(models.Model):
    creator = models.ForeignKey(User)
    title = models.CharField(max_length=256)
    text = models.TextField()
    comments_enabled = models.BooleanField(default=True)
    tags = models.ManyToManyField(Tag, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT) #perhaps try a query with Models.SET()
    date_posted = models.DateTimeField(auto_now_add=True)
    date_published = models.DateTimeField(default=now)
    is_public = models.BooleanField(default=True, blank=True)
    is_removed = models.BooleanField(default=False, blank=True)
    comments = GenericRelation(Comment, object_id_field="object_pk")
    #needs date_modified
    #managers
    objects = ThreadManager()
    public = PublicSetManager()
    #private = PrivateThreadManager()
    #removed = RemovedThreadManager()
    def clean(self):
        if self.is_public == True and self.is_removed == True:
            raise ValidationError('Removed threads cannot also be public.')
        super(Thread, self).clean()
    def __unicode__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('thread:view', kwargs={'pk':str(self.pk)})
    def is_published(self):
        return (self.date_published.replace(tzinfo=utc) - now()).total_seconds() <= 0 #is today >= date_published


class Requirement(models.Model):
    text = models.CharField(max_length=255, unique=True)
    objects = RequirementManager()
    def clean(self):
        if not self.text:
            raise forms.ValidationError('Requirement cannot have empty text')
        super(Requirement, self).clean()
    def __unicode__(self):
        return self.text
    def get_absolute_url(self):
        pass
    def natural_key(self):
        return self.text

class Challenge(models.Model):
    title = models.CharField(max_length=255)
    date_expires = models.DateTimeField()
    news = models.ForeignKey(Thread)
    recs = models.ManyToManyField(Requirement)
    #since challenges remain in DB past expiration should note on boards if challenge is expired - perhaps even discontinue voting?
    def clean(self):
        #validating date_expires will require more knowledge of tz, dst and the datetime module
        super(Challenge, self).clean()
    def __unicode__(self):
        return self.title
    def get_absolute_url(self):
        return self.news.get_absolute_url()
    def natural_key(self):
        return (self.title,) + self.news.natural_key()
    natural_key.dependencies = ['discuss.thread']


class BinaryPoll(models.Model):
    question = models.CharField(max_length=128)
    yes = models.ManyToManyField(User, related_name='yes_votes')
    no = models.ManyToManyField(User, related_name='no_votes')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    poll = generic.GenericForeignKey('content_type', 'object_id')
    objects = BinaryPollManager()
    def __unicode__(self):
        return "%s (%i:%i)" % (self.question, self.yes.all().count(), self.no.all().count())
    def get_absolute_url(self):
        return self.poll.get_absolute_url()
    #def add_to_tes(self, user):
    #    self.yes.add(user)
    #    if self.yes.
    def yes_count(self):
        if not hasattr(self, 'yesses'):
            self.yesses = self.yes.all().count()
        return self.yesses
    def no_count(self):
        if not hasattr(self, 'nos'):
                self.nos = self.no.all().count()
        return self.nos
    def user_voted(self, user):
        if user in self.yes.all() or user in self.no.all(): return True
        else: return False
    def get_vote_for_user(self, user):
        if user in self.yes.all():
            return True
        if user in self.no.all():
            return False
    def natural_key(self):
        return (self.question, self.object_id, self.content_type.natural_key())