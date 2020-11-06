from django.template import RequestContext
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
#from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from entry.models import Deck
from discuss.models import Thread, Category

def viewHome(request):
    d = {'newboards':[], 'thread_list':[]}
    d['newboards'] = Deck.public.all().order_by('-date_posted')[0:5]
    d['thread_list'] = Thread.public.filter(category__title='News')
    return render_to_response('home.html', context_instance=RequestContext(request, d))


def viewUser(request, pk):
    u = get_object_or_404(User, pk=pk)
    d = {'submissions': Deck.public.filter(creator=u), 'activity':[], 'user':u}
    #act = get recent submissions, get recent comments, perhaps other stuff and combine and order based on date
    return render_to_response('user_profile.html', context_instance=RequestContext(request, d))


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        referer = request.POST.get('referer', 'view_all_announcements')
        if not username or not password:
            raise Http404 #maybe there's a prettier way to fail
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(referer)
            else:
                return redirect('account_disabled_page')
        else:
            return render_to_response('login_page.html', context_instance=RequestContext(request, {'referer':referer, 'status':'Login Failed! Wrong username/password combination.'}))
    elif request.method == 'GET':
        if request.user.is_authenticated(): raise Http404 #better error message needed
        else: return render_to_response('login_page.html', context_instance=RequestContext(request, {'referer':request.META.get('HTTP_REFERER', 'view_all_announcements')}))
    else: #shouldn't ever happen, but you never know when someone's gonna try a DELETE or PUT request
        raise Http404


def logout_view(request):
    if request.user.is_authenticated():
        logout(request)
        return redirect('view_home')
    else:
        raise Http404


def preferences_view(request):
    if request.user.is_authenticated():
        if request.method == 'POST': #update settings
            pass
        elif request.method == 'GET':
            return render_to_response('user_settings.html', context_instance=RequestContext(request, {}))
        else:
            raise Http404
    else:
        return redirect('login_page')
    pass


def registration_view(request):
    if request.user.is_authenticated():
        raise Http404 #return error of some sort
    if request.method == 'POST': #registering right now
        sn = request.POST.get('username')
        pw = request.POST.get('password')
        email_addi = request.POST.get('email') #do it right now lars! you know you want to!
        if User.objects.filter(email=email_addi).count() == 0:
            if User.objects.filter(username=sn).count() == 0:
                user = User.objects.create_user(sn, email_addi, pw)
                user.save()
                return redirect('registration_successful_page')
            else:
                raise Http404 #see comment for else: below this
        else: 
            raise Http404 #actually redirect with proper error of matching emails
        pass
    elif request.method == 'GET':
        return render_to_response('new_user_registration.html', context_instance=RequestContext(request, {}))
    else:
        raise Http404
    

def accountDisabled_view(request):
    pass

def flaggedComments_view(request):
    pass

