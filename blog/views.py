from django.shortcuts import render


def dummy():
    return "Dummy"


def index(request):
    context = {
        'title': "Python DTL working!",
        'func': dummy,
        'myList': ['one', 'two', 'three']
    }
    return render(request, "blog/index.html", context=context)
