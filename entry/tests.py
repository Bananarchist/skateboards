"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
import random, string
from discuss.models import Category, Thread, Tag, Challenge, Requirement, BinaryPoll
from entry.models import Deck
from entry import views as eviews 
from entry import forms as eforms
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


class DeckTest(unittest.TestCase):
	def setUp(self):
		self.factory = RequestFactory()

	def test_deck_list(self):
		req = self.factory.get('/')
		view = eviews.DeckList()
		view = setup_view(view, req, search=True)
		context = view.get_context_data(object_list=[])
		self.assertTrue('decks' in context)
		#search kwarg returns form
		self.assertTrue('form' in context)
		self.assertTrue(context['search'])
		
	def test_deck_detail(self):
		req = self.factory.get('/')
		req.user = AnonymousUser()
		view = eviews.DeckDetail()
		view = setup_view(view, req)
		view.object = None
		context = view.get_context_data()
		self.assertTrue('deck' in context)

	def test_deck_create_get(self):
		req = self.factory.get('/')
		req.user = AnonymousUser()
		view = eviews.DeckCreate()
		view = setup_view(view, req)
		view.object = None
		resp = view.get(req)
		self.assertEqual(resp.status_code, 302)

class DeckViewTest(TestCase):
	
	def setUp(self):
		#Groups and Permissions
		
		#Users
		self.larzipan = User.objects.create_superuser('larzipan', 'someone@gmail.com', 'password')
		self.bana = User.objects.create_user('bananarchist', 'someone.else@gmail.com', 'password')
		#Tags
		self.tags = [Tag.objects.create(text='spam'), Tag.objects.create(text='backend'), Tag.objects.create(text='robots'), Tag.objects.create(text='riviera')]
		#Categories
		self.news_cat = Category.objects.create(title="News", description="Be careful what you wish for")
		#Threads
		self.t1 = Thread.objects.create(creator=self.larzipan, title="Site Testing", text="Loreum", category=self.news_cat)
		self.t1.tags.add(self.tags[1])
		#Recs
		rec = Requirement.objects.create(text="Most contain a reference to robosexuality")
		#Challenges
		chall = Challenge.objects.create(title="Roborotica", news=self.t1, date_expires=djnow())
		chall.recs.add(rec)
		#Decks
		self.deck1 = Deck.objects.create(title='Deck 1', creator=self.larzipan, deck_length_coefficient=33, deck_width_coefficient=9, deck_image='img/2013/10/20/1_1dnrm.png')
		self.deck1.tags.add(self.tags[2])
		self.deck1.tags.add(self.tags[1])
		#BinaryPolls
		BinaryPoll.objects.create(question="Like?", poll=self.deck1)
		BinaryPoll.objects.create(question="Would you buy this?", poll=self.deck1)
		#Other
		self.factory = RequestFactory()

	def test_data_loaded(self):
		self.assertEqual(User.objects.all().count(), len([1,2]))
		self.assertEqual(Category.objects.all().count(), len([1]))
		self.assertEqual(Thread.objects.all().count(), len([1]))
		self.assertEqual(Tag.objects.all().count(), len([1,2,3,4]))
		self.assertEqual(Challenge.objects.all().count(), len([1]))
		self.assertEqual(Deck.objects.all().count(), len([1]))

	def test_deck_list(self): #should actually test that searching returns right stuff
		resp = self.client.get(reverse('deck:list'))
		self.assertEqual(resp.status_code, 200)
		self.assertTrue('decks' in resp.context)
		self.assertEqual([d.pk for d in resp.context['decks']], [d.pk for d in Deck.objects.all()])	
		
	def test_deck_detail_voting_info_exists(self):
		req = self.factory.get(reverse('deck:view', kwargs={'pk':self.deck1.pk}))
		req.user = self.larzipan
		view = setup_view(eviews.DeckDetail(), req)
		view.object = self.deck1
		context = view.get_context_data(object_pk=self.deck1.pk)
		self.assertTrue('user_voted' in context)

	def test_voting(self):
		req = self.factory.get('/', {'poll_id':self.deck1.polls.all()[0].pk}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		resp = eviews.vote(req, self.deck1.pk)
		self.assertTrue('v_up' in resp.content, resp.content)
		self.assertTrue(self.client.login(username=self.larzipan.username, password='password'))
		resp = self.client.post(reverse('vote:deck', kwargs={'pk':self.deck1.pk}), data={'poll_id':self.deck1.polls.all()[0].pk, 'vote_value': 1}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertTrue('v_up' in resp.content, resp.content)
		
	def test_deck_post_valid_data(self):	#self.assertTrue('errors' in resp.context['form'])
		with open('entry/test_image.png', 'rb') as f:
			req = self.factory.post(reverse('deck:create'), {'deck': f.read()})
			form = eforms.DeckForm({'title':'Title #A', 'tags':'spam', 'text':'Roballelujah', 'deck_length_coefficient':33, 'deck_width_coefficient':9})
			self.assertTrue(form.is_valid(), form.errors)
			req.user = self.bana
			view = setup_view(eviews.DeckCreate(success_url=reverse('deck:list')), req)
			resp = view.form_valid(form)
			self.assertEqual(resp.status_code, 302)

	def test_deck_delete(self):
		#get
		resp = self.client.get(reverse('deck:delete', kwargs={'pk':self.deck1.pk}))
		self.assertEqual(resp.status_code, 200)
		#post
		pass

