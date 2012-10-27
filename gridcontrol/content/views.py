# Create your views here.
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import Http404, HttpResponse

def home(request):
	ctx = {}
	return render_to_response("frontpage.html", ctx, RequestContext(request))
