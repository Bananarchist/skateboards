# Create your views here.
import os
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView
from django.contrib.contenttypes.models import ContentType
from forms import ModEventForm
from models import ModEvent
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect

class ModEventDetail(DetailView):
    model = ModEvent
    
    def get_context_data(self, **kwargs):
        context = super(ModEventDetail, self).get_context_data(**kwargs)
        context['object_template'] = '%s%s%s_full_view.html' % (self.object.content_type.app_label, os.sep, self.object.content_type.model)
        context[self.object.content_type.model] = self.object.content_object
        return context
    
class ModEventList(ListView):
    model = ModEvent
    context_object_name = "modevent_list"

class ModEventCreate(CreateView):
    model = ModEvent
    form_class = ModEventForm

    def form_valid(self, form):
        form.instance.creator = self.request.user
        #form.instance.content_type = ContentType.objects.get_for_id(self.request.POST.get('content_type'))
        #form.instance.object_id = self.request.POST.get('object_id')
        #content_object = content_object
        #content_object = form.instance.content_type.get_object_for_this_type(pk=form.instance.object_id)
        #if content_object == None:
        #    raise ValueError
        form.instance.content_object.is_public = False
        form.instance.content_object.is_removed = True
        form.instance.content_object.save()
        return super(ModEventCreate, self).form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['content_type'] = self.request.GET.get('content_type')
        context['object_id'] = self.request.GET.get('object_id')
        return context
        
    def get_success_url(self):
        return reverse('%s:list' % self.object.content_type.model) #we should edit this
        # we can easily access self.object.app_label and such to go to the list, but since entry uses "deck" for its urls, this will not work yet

class ModEventDelete(DeleteView):      
    model = ModEvent
    context_object_name = 'modevent'
    success_url = reverse_lazy('view_home')
    # this will check if the related object should be delteted as well, and respond accordingly
    # generally the corresponding object will be deleted too, but ocassionaly, for example when there are 
    # a ton of copies of the ModEvent object for a single action, that will not be the case (and could
    # cause errors if the model attempted such a thing)
    
    def get_context_object(self, **kwargs):
        context = super(ModEventDelete, self).get_context_object(**kwargs)
        return context

    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        if self.request.POST.get('delete_associated_object', False):
            self.object.content_object.delete()
        else:
            self.object.content_object.is_public = True
            self.object.content_object.is_removed = False
            self.object.content_object.save()
        return HttpResponseRedirect(success_url)
