# Create your views here.
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from gridcontrol.gist_retriever import GistRetriever

def home(request):
	ctx = {}
	return render_to_response("frontpage.html", ctx, RequestContext(request))

@login_required
def logged_in(request):
	"""Have no idea yet how to tell django-social-auth that logged-in
	is something else. Remove this dumb redirect when this is figured out"""
	return redirect(reverse('account'))

@login_required
def account_logout(request):
	logout(request)
	return redirect(reverse('home'))

@login_required
def account(request):
	gist_retriever = GistRetriever(request.user.username)
	gists = gist_retriever.get_gist_list()
	ctx = {"gists": gists}
	return render_to_response("account/home.html", ctx, RequestContext(request))
