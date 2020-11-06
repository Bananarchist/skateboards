from django.template import RequestContext
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from models import Deck
from forms import DeckForm
from django.contrib.auth.models import User
from django.contrib.auth.views import redirect_to_login
from django.core.files.uploadedfile import SimpleUploadedFile
from django.views.generic import DetailView, ListView
import base64, datetime
from django.db.models import Q
from discuss.utils import searchQuerySet
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy
from lars.forms import SearchForm
from django.contrib.contenttypes.models import ContentType
from discuss.models import BinaryPoll

class DeckDetail(DetailView):
    model = Deck
    context_object_name = 'deck'

    def get_context_data(self, **kwargs):
        context = super(DeckDetail, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            context['user_voted'] = {poll:poll.user_voted(self.request.user) for poll in self.object.polls.all()}
            if self.object.creator == self.request.user:
                context['edit_button'] = True
                context['delete_button'] = True
            if self.request.user.has_perm('modevent.add_modevent'):
                context['edit_button'] = True
                context['delete_button'] = True
                context['content_type'] = ContentType.objects.get_for_model(Deck).pk
        return context

class DeckList(ListView):
    """List of entries, for search results.
    """
    model = Deck
    queryset = Deck.public.all()
    context_object_name = 'decks'

    def get_queryset(self):
        if self.request.GET.get('filter', False):
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
        context = super(DeckList, self).get_context_data(**kwargs)
        if self.kwargs.get('search', False):
            context['search'] = True
            context['form'] = SearchForm()
        return context


class DeckCreate(CreateView):
    model = Deck
    form_class = DeckForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return super(DeckCreate, self).get(request, *args, **kwargs)
        else:
            return redirect_to_login(reverse('deck:create'))

    def form_valid(self, form):
        form.instance.creator = self.request.user
        form.instance.save()
        #image_data
        imagedata = self.request.POST.get('deck', '').partition('data:image/png;base64,') #need to test
        if imagedata[1] == 'data:image/png;base64,':
            fnm = '%i_%i%s.png' % (form.instance.pk, self.request.user.pk, self.request.user.username)
            fc = SimpleUploadedFile(fnm, base64.standard_b64decode(imagedata[2]))
            try:
                form.instance.deck_image.save(fnm, fc, True)
            except: #perhaps we should instead return a self.form_invalid with proper error text in the form
                return HttpResponse(content='<reason>Upload error, could not save image.</reason>', content_type='application/xml', status=400)
        else:
            return HttpResponse(content='<reason>Upload error, could not decode image (possibly corrupted in transmission). Type=%s</reason>' % imagedata[1], content_type='application/xml', status=400)
        #this should be in this view because this is the only time we will KNOW that we need to attach these polls
        BinaryPoll.objects.create(question="Like?", poll=form.instance)
        BinaryPoll.objects.create(question="Would you buy this?", poll=form.instance)
        return super(DeckCreate, self).form_valid(form)

class DeckUpdate(UpdateView):
    model = Deck
    form_class = DeckForm

    def get_context_data(self, **kwargs):
        context = super(DeckUpdate, self).get_context_data(**kwargs)
        context['update'] = True
        return context

    def get_initial(self):
        return {'tags': ', '.join([tag.text for tag in self.object.tags.all()])}


class DeckDelete(DeleteView):
    model = Deck
    context_object_name="deck"
    success_url = reverse_lazy('deck:list')


@csrf_protect
def vote(request, pk):
    if request.is_ajax(): #should always be ajax, but we might change our minds in the future
        if request.method == 'POST':
            if request.user.is_authenticated(): #shouldn't happen, but best to check
                try:
                    poll_id = int(request.POST.get('poll_id'))
                    vote_sign = int(request.POST.get('vote_value'))
                    poll = BinaryPoll.objects.get(pk=poll_id)
                except ValueError as e:
                    return HttpResponse(content='<?xml version="1.0" encoding="UTF-8" ?>\n<root><error>Invalid voting data: %s</error></root>' % e, content_type='application/xml', status=400)
                if vote_sign > 0:
                    poll.yes.add(request.user)
                else:
                    poll.no.add(request.user)
                return HttpResponse(content='<?xml version="1.0" encoding="UTF-8" ?>\n<root><v_up>%i</v_up><v_down>%i</v_down></root>' % (poll.yes_count(), poll.no_count()), content_type='application/xml', status=200)
            else:
                return HttpResponse(content='<?xml version="1.0" encoding="UTF-8" ?>\n<root><error>Unauthorized</error></root>', content_type='application/xml', status=401)
        elif request.method == 'GET':
                try:
                    poll_id = int(request.GET.get('poll_id', None))
                    poll = BinaryPoll.objects.get(pk=poll_id)
                    return HttpResponse(content='<?xml version="1.0" encoding="UTF-8" ?>\n<root><v_up>%i</v_up><v_down>%i</v_down></root>' % (poll.yes_count(), poll.no_count()), content_type='application/xml', status=200)
                except ValueError as e:
                    return HttpResponse(content='<?xml version="1.0" encoding="UTF-8" ?>\n<root><error>Invalid voting data: %s</error></root>' % e, content_type='application/xml', status=400)
        else:
            return HttpResponse(content='<?xml version="1.0" encoding="UTF-8" ?>\n<root><error>Invalid voting data</error></root>', content_type='application/xml', status=405)
    else:
        pass #can't happen?


def searchView(request):
    return render_to_response('search.html')
