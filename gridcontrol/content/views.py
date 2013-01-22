# Create your views here.
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django import forms
from gridcontrol.gist_retriever import GistRetriever
from pprint import pprint ##DEBUG
from gridcontrol.engine.tasks import get_client, register_code
from gridcontrol.engine.engine import GridControlEngine
from django.conf import settings
import simplejson as json

def home(request):
	user = request.user
	ctx = {'user':user}
	return render_to_response("frontpage.html", ctx, RequestContext(request))

@login_required
def logged_in(request):
	"""Have no idea yet how to tell django-social-auth that logged-in
	is something else. Remove this dumb redirect when this is figured out"""
	user = request.user
	#register_login(user)
	return redirect(reverse('account'))

@login_required
def account_logout(request):
	logout(request)
	return redirect(reverse('home'))

@login_required
def account(request):
	user = request.user
	gce = GridControlEngine(get_client())
	ctx = {
		'is_active': gce.is_user_active(user.id),
	}
	return render_to_response("account/home.html", ctx, RequestContext(request))

@login_required
def view_code(request, userid):
	gce = GridControlEngine(get_client())
	user = get_object_or_404(User, id=userid)
	ctx = {
		'code': gce.get_user_code(userid),
		'botowner': user,
	}
	return render_to_response("view_code.html", ctx, RequestContext(request))

@login_required
def bot_debug(request):
	user = request.user
	gce = GridControlEngine(get_client())
	ctx = {
		'code': gce.get_user_code(user.id),
		'stack': gce.get_user_vm(user.id),
	}
	ctx['json'] = json.dumps(ctx, use_decimal=True)
	return render_to_response("account/bot_debug.html", ctx, RequestContext(request))

def _valid_ext(filename):
	fname = filename.upper()
	return fname.endswith('.GRIDLANG') or fname.endswith('.GRIDC')

@login_required
def account_gists(request):
	user = request.user
	gist_retriever = GistRetriever(user.username)
	gists = gist_retriever.get_gist_list()
	gists = [g for g in gists if [f for f in g['files'] if _valid_ext(f)]]
	ctx = {"gists": gists}
	request.session["gists"] = gists
	return render_to_response("account/gists.html", ctx, RequestContext(request))

@login_required
def use_gist(request, gist_id=0):
	gist = (g for g in request.session['gists'] if g['id'] == unicode(gist_id)).next()
	code = None
	success = False
	msg = ""
	ctx = {}
	gist_retriever = GistRetriever(request.user.username)

	computed_max_size = settings.GRIDCONTROL_GIST_MAX_SIZE

	for gist_fname, gist_fdata in gist['files'].items():
		if _valid_ext(gist_fname):
			ctx['filename'] = gist_fname
			if gist_fdata['size'] < computed_max_size:
				success, msg = register_code(request.user, gist_fdata['raw_url'])
			else:
				success, msg = False, 'file {} too large.  less coad pls'.format(gist_fdata['raw_url'])
			break

	ctx['success'] = success
	ctx['message'] = msg

	user = request.user
	gce = GridControlEngine(get_client())
	gce.activate_user(user.id, user.username)

	return render_to_response("account/use_gist.html", ctx, RequestContext(request))

@login_required
def gist_viewer(request, gist_id=0, gist_revision=""):
	gist_retriever = GistRetriever(request.user.username)
	gist_revisions = gist_retriever.get_gist_history(gist_id)
	gist_texts = {}
	if not gist_revision:
		#Gist revision not specified, so get the latest gist
		gist = [gist for gist in request.session['gists'] if gist['id'] == unicode(gist_id)][0]
		for gist_fname, gist_fdata in gist['files'].items():
			gist_texts[gist_fname] = gist_retriever.get_file_text(gist_fdata['raw_url'])
	else:
		gist_info = gist_retriever.get_gist_version(gist_id, gist_revision)
		for file_dict in gist_info:
			gist_texts[file_dict["filename"]] = gist_retriever.get_file_text(file_dict["text_url"])
	ctx = {	"gist_id": gist_id,
			"gist_texts": gist_texts,
			"gist_revisions": gist_revisions}
	return render_to_response("account/gist_viewer.html", ctx, RequestContext(request))
		

