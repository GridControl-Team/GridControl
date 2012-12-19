# Create your views here.
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from gridcontrol.gist_retriever import GistRetriever
from pprint import pprint ##DEBUG
from gridcontrol.engine.tasks import register_login

def home(request):
	ctx = {}
	return render_to_response("frontpage.html", ctx, RequestContext(request))

@login_required
def logged_in(request):
	"""Have no idea yet how to tell django-social-auth that logged-in
	is something else. Remove this dumb redirect when this is figured out"""
	user = request.user
	register_login(user)
	return redirect(reverse('account'))

@login_required
def account_logout(request):
	logout(request)
	return redirect(reverse('home'))

@login_required
def account(request):
	user = request.user
	ctx = {}
	return render_to_response("account/home.html", ctx, RequestContext(request))

@login_required
def account_gists(request):
	user = request.user
	gist_retriever = GistRetriever(user.username)
	gists = gist_retriever.get_gist_list()
	ctx = {"gists": gists}
	request.session["gists"] = gists
	return render_to_response("account/gists.html", ctx, RequestContext(request))

@login_required
def gist_viewer(request, gist_id=0):
	print "Looking for gists with ID: %s" % unicode(gist_id)
	print "Gists" ##DEBUG
	pprint(request.session['gists']) ##DEBUG
	gist = [gist for gist in request.session['gists'] if gist['id'] == unicode(gist_id)][0]
	gist_retriever = GistRetriever(request.user.username)
	gist_texts = {}
	for gist_filename, gist_file_data in gist['files'].items():
		gist_texts[gist_filename] = gist_retriever.get_file_text(gist_file_data['raw_url'])
	ctx = {"gist_texts": gist_texts}
	return render_to_response("account/gist_viewer.html", ctx, RequestContext(request))
