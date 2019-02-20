from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader


# Create your views here.
def show_menu(request):
    return render(request, 'menu.html')