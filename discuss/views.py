from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, ModelFormMixin
from django.core.urlresolvers import reverse, reverse_lazy, resolve
from django.shortcuts import render_to_response, get_object_or_404, redirect
from models import Challenge, Category, Thread, Tag
from forms import ThreadForm, ChallengeForm, NewsForm
from discuss.utils import searchQuerySet
from lars.forms import SearchForm
from moderation.forms import ModEventForm
from django.contrib.contenttypes.models import ContentType
from lars import settings

class ThreadDetail(DetailView):
    """Provides thread title, OP and responses.
    """
    model = Thread
    context_object_name = 'thread'
    #two modes - threaded and flat, may come later
    def get_context_data(self, **kwargs):
        context = super(ThreadDetail, self).get_context_data(**kwargs)
        if not self.object.is_public: #perhaps this stuff should go in get or get_object
            if not self.request.user.has_perm('view_private'):
                context['status_code'] = 305 #return 404
        if self.object.is_removed:
            context['status_code'] = 404 #return 404
        if self.object.creator == self.request.user:
            context['edit_button'] = True
            context['delete_button'] = True
        if self.request.user.has_perm('modevent.add_modevent'):
            context['edit_button'] = True
            context['delete_button'] = True
            context['content_type'] = ContentType.objects.get_for_model(Thread).pk
        return context

class ThreadList(ListView):
    """List of threads, for search results.
    """
    model = Thread
    context_object_name = 'thread_list'
    queryset = Thread.public.all()

    def get_queryset(self):
        if self.request.GET.get("filter", False):
            self.queryset = searchQuerySet(self.queryset,
                                       self.request.GET.get('tags', False),
                                       self.request.GET.get('users', False),
                                       self.request.GET.get('fulltext', False),
                                       self.request.GET.get('date', False),
                                       self.request.GET.get('sort', SearchForm.DATE_CHOICE),
                                       self.request.GET.get('order', SearchForm.ASC_CHOICE))
        elif self.kwargs.get('search', False):
            self.queryset = self.queryset.none()
        return self.queryset

    def get_context_data(self, **kwargs):
        context = super(ThreadList, self).get_context_data(**kwargs)
        if self.kwargs.get('search', False):
            context['search'] = True
            if self.request.GET.get('filter', False):
                context['form'] = SearchForm(self.request.GET)
            else:
                context['form'] = SearchForm()

        return context

class ThreadCreate(CreateView): #this may turn out to need to be a function
    """How one creates a thread, and for that matter a news post and challenge.
    """
    model = Thread
    form_class = ThreadForm

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super(ThreadCreate, self).form_valid(form)

    def get_success_url(self):
        if self.request.POST.get('ifchallenge', False) and self.request.user.has_perm('challenge.add_challenge'):
            return reverse('thread:attach_challenge', kwargs={'thread_pk':self.object.pk}) #how do we pass the thread id?
        else:
            return super(ThreadCreate, self).get_success_url()

    def get_context_data(self, **kwargs):
        context = super(ThreadCreate, self).get_context_data(**kwargs)
        if self.request.GET.get('ref_forum', None):
            context['referer'] = int(self.request.GET.get('ref_forum'))
        if self.form_class != ThreadForm:
            context['isnews'] = settings.NEWS_CATEGORY_PK
        return context
        #perhaps this should merely do the thread, and then redirect to challenge_create if challenge is marked


class ThreadUpdate(UpdateView):
    model = Thread
    form_class = ThreadForm

    def get_context_data(self, **kwargs):
        context = super(ThreadUpdate, self).get_context_data(**kwargs)
        context['update'] = True
        return context

    def get_initial(self):
        return {'tags': ', '.join([tag.text for tag in self.object.tags.all()])}


class ThreadDelete(DeleteView):
    model = Thread
    success_url = reverse_lazy('forum:list')
    context_object_name = 'thread'

#    def get_context_data(self, **kwargs):
#        context = super(ThreadDelete, self).get_context_data(**kwargs)
#        if self.request.method == 'GET': context['form'] =

class CategoryDetail(DetailView):
    """Returns Category, description, and list of recent threads.
    """
    model = Category
    context_object_name = 'forum'

    def get_context_data(self, **kwargs):
        context = super(CategoryDetail, self).get_context_data(**kwargs)
        context['thread_list'] = Thread.public.filter(category=self.object) #sort by date
        context['news'] = True if self.object.pk == settings.NEWS_CATEGORY_PK else False
        return context

    def get_object(self, *args, **kwargs):
        object = super(CategoryDetail, self).get_object(*args, **kwargs)
        if object.restricted:
            if not self.request.user.has_perm('discuss.' + object.restricted):
                return Http404
        return object

class CategoryList(ListView):
    """Lists all categories (or a slice, possibly), with descriptions.
    """
    model = Category
    context_object_name = 'forum_list'
    query_set = Category.objects.all()
    template_name = 'discuss/forum_list.html'

class CategoryCreate(CreateView):
    model = Category

class CategoryUpdate(UpdateView):
    model = Category

class CategoryDelete(DeleteView):
    model = Category

class TagDetail(DetailView):
    model = Tag

class TagList(ListView):
    model = Tag

class ChallengeDetail(DetailView):
    model = Challenge

class ChallengeList(ListView):
    model = Challenge

class ChallengeCreate(CreateView): #here next!
    model = Challenge
    form_class = ChallengeForm

    def post(self, request, *args, **kwargs):
        self.news = get_object_or_404(Thread, pk=request.POST.get('news', None))
        return super(ChallengeCreate, self).post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.news = get_object_or_404(Thread, pk=kwargs.get('thread_pk', None))
        return super(ChallengeCreate, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ChallengeCreate, self).get_context_data(**kwargs)
        context['thread_pk'] = self.news.pk
        return context

    def get_success_url(self):
        return reverse('thread:view', kwargs={'pk':self.object.news.pk}) #how do we pass the thread id?

class ChallengeDelete(DeleteView):
    model = Challenge

class ChallengeUpdate(UpdateView):
    model = Challenge
    form_class = ChallengeForm

    def get_initial(self):
        return {'recs': '\n'.join([rec.text for rec in self.object.recs.all()])}

    def get_context_data(self, **kwargs):
        context = super(ChallengeUpdate, self).get_context_data(**kwargs)
        context['thread_pk'] = self.object.news.pk
        return context

    def get_success_url(self):
        return reverse('thread:view', kwargs={'pk':self.object.news.pk})



def thread_challenge_view(request, thread_pk):
    thread = Thread.public.get(pk=thread_pk)
    challenges = thread.challenge_set.all()
    if len(challenges) > 0:
        return ChallengeUpdate.as_view()(request, pk=challenges[0].pk)
    else:
        return ChallengeCreate.as_view()(request, thread_pk=thread_pk)
