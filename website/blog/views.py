from django.shortcuts import render

def dummy():
    return "This is a dummy function"

def index(request):
    context = {
        'title': 'Blog Home',
        'func': dummy,
        'myList': [1, 2, 3, 4, 5],
    }
    return render(request, 'blog/index.html', context)
