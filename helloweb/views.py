from django.shortcuts import render
from django.http import HttpResponse
import datetime

# Create your views here.
from django.views import View


def index(request):
    return HttpResponse("""
    <h1> Hello from Django ! </h1>
    <p> Some text </p>
    <a href="datetime/">datetime</a>
    """)


def current_datetime(request):
    now = datetime.datetime.now()
    return HttpResponse(f"<h1> current_datetime: {now} </h1>")


class CurrentDateTimeView(View):
    def get(self, request):
        now = datetime.datetime.now()
        return HttpResponse(f"<h1> current_datetime (class): {now} </h1>")
