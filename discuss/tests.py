"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
import random, string
from discuss.models import Category, Thread, Tag, Challenge, Requirement
from discuss import views as dviews
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, AnonymousUser
import datetime
from django.utils.timezone import utc
from django.utils.timezone import now as djnow
from django.test.client import RequestFactory
import unittest

def setup_view(view, request, *args, **kwargs):
	view.request = request
	view.args = args
	view.kwargs = kwargs
	return view


class ThreadViewTests(TestCase):
	def setUp(self):
		#Groups and Permissions

		#Users
		self.larzipan = User.objects.create_superuser('larzipan', 'someone@gmail.com', 'password')
		self.bana = User.objects.create_user('bananarchist', 'someone.else@gmail.com', 'password')
		#Categories
		self.news_cat = Category.objects.create(title="News", description="Be careful what you wish for")
		self.gen_cat = Category.objects.create(title="General", description="Samesies")
		#Tags
		self.tags = [Tag.objects.create(text='spam'), Tag.objects.create(text='backend'), Tag.objects.create(text='robots'), Tag.objects.create(text='riviera')]
		#Threads
		self.t1 = Thread.objects.create(creator=self.larzipan, title="Site Testing", text="Loreum", category=self.news_cat)
		self.t1.tags.add(self.tags[1])
		self.t2 = Thread.objects.create(creator=self.bana, title="The Longest Thread Ever", text="MAKE IT LONG", category=self.gen_cat)
		self.t2.tags.add(self.tags[0])
		self.t3 = Thread.objects.create(creator = self.larzipan, title="Unpublished", text='Roborotiiiiii', category=self.gen_cat,
								date_published=datetime.datetime(datetime.datetime.now().year + 1, 1, 1))
		self.t3.tags.add(self.tags[1])
		#Recs
		rec = Requirement.objects.create(text="Most contain a reference to robosexuality")
		#Challenges
		chall = Challenge.objects.create(title="Roborotica", news=self.t1, date_expires=djnow())
		chall.recs.add(rec)
		#Other
		self.factory = RequestFactory()

	#self
	def test_data_loaded(self):
		self.assertEqual(User.objects.all().count(), len([1,2]))
		self.assertEqual(Category.objects.all().count(), len([1,2]))
		self.assertEqual(Thread.objects.all().count(), len([1,2,3]))
		self.assertEqual(Tag.objects.all().count(), len([1,2,3,4]))
		self.assertEqual(Challenge.objects.all().count(), len([1]))

	#model
	def test_published_thread(self):
		self.assertFalse(self.t3.is_published())

	#views
	def test_thread_detail(self):
		req = self.factory.get('/')
		req.user = AnonymousUser()
		view = setup_view(dviews.ThreadDetail(), req)
		view.object = Thread(title='Robot Rockerz', text='None', creator=self.larzipan)
		context = view.get_context_data()
		self.assertTrue('thread' in context)

	def test_valid_thread_detail(self):
		#valid
		self.assertTrue(self.client.login(username=self.bana.username, password='secret'))
		resp = self.client.get(reverse('thread:view', kwargs={'pk':self.t1.pk}))
		self.assertEqual(resp.status_code, 200)
		self.assertFalse('edit_button' in resp.context)
		resp = self.client.get(reverse('thread:view', kwargs={'pk':self.t2.pk}))
		self.assertTrue('edit_button' in resp.context)
		self.assertTrue(self.client.logout())
		resp = self.client.get(reverse('thread:view', kwargs={'pk':self.t2.pk}))
		self.assertTrue(self.client.login(username=self.larzipan.username, password='secret'))

	def test_false_is_public_thread_detail(self):#valid is_public = False
		self.t2.is_public = False
		self.t2.save()
		resp = self.client.get('thread:view', kwargs={'pk':self.t2.pk})
		self.assertEqual(resp.status_code, 305)

	def test_false_is_removed_thread_detail(self):	#valid is_removed = True
		self.t2.is_removed = True
		self.t2.save()
		resp = self.client.get('thread:view', kwargs={'pk': self.t2.pk})
		self.assertEqual(resp.status_code, 305)

	def test_unpublished_thread_detail(self):	#valid is_published = False
		resp = self.client.get('thread:view', kwargs={'pk': self.t3.pk})
		self.assertEqual(resp.status_code, 405)

	def test_thread_create_get(self):
		resp = self.client.get(reverse('thread:create'))
		self.assertEqual(resp.status_code, 200)
		self.assertTrue('form' in resp.context, 'No form object in context')

	def test_thread_create_post_invalid(self):	#post invalid
		resp = self.client.post(reverse('thread:create'))
		self.assertEqual(resp.status_code, 200)
		self.assertTrue('form' in resp.context, 'No form object in context')

	def test_thread_create_post_valid(self):	#post valid
		req = self.factory.post(reverse('thread:create'), {'title':'Title #A', 'tags':'spam', 'text':'Roballelujah', 'comments_enabled':'checked', 'category':str(self.gen_cat.pk)})
		req.user = self.bana
		resp = dviews.ThreadDetail.as_view()(req)
		#check resp status code
		self.assertEqual(resp.status_code, 200) #might be redirect
		self.assertTrue('thread' in resp.context)

	def test_thread_list(self):
		req = self.factory.get('/')
		req.user = AnonymousUser()
		view = setup_view(dviews.ThreadList(), req)
		context = view.get_context_data(object_list=[])
		self.assertTrue('threads' in context)
		self.assertFalse('form' in context)
		view = setup_view(dviews.ThreadList(), req, search=True)
		context = view.get_context_data(object_list=[])
		self.assertTrue('form' in context)
