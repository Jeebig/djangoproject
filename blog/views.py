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


def favorite_song(request):
    context = {
        'song_line': "You made me a, you made me a believer, believer",
        'artist': "Imagine Dragons",
        'title': "Believer"
    }
    return render(request, 'blog/favorite_song.html', context)


def about_me(request):
    context = {
        'title': "About Me",
        'name': "Your Name",
        'description': "This is about me page"
    }
    return render(request, 'blog/about.html', context)


def contact_me(request):
    if request.method == 'POST':
        # Обработка отправленной формы
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Здесь можно добавить логику отправки email или сохранения в БД
        # Пока просто покажем сообщение об успехе
        context = {
            'title': "Contact Me",
            'email': "your.email@example.com",
            'success_message': f"Thank you {name}! Your message has been received.",
            'form_submitted': True
        }
    else:
        context = {
            'title': "Contact Me",
            'email': "your.email@example.com"
        }
    return render(request, 'blog/contact.html', context)


def my_works(request):
    context = {
        'title': "My Works",
        'works': ["Project 1", "Project 2", "Project 3"]
    }
    return render(request, 'blog/my_works.html', context)


def favorite_works(request):
    context = {
        'title': "Favorite Works",
        'favorites': ["Favorite 1", "Favorite 2"]
    }
    return render(request, 'blog/favorite_works.html', context)


def skills(request):
    context = {
        'title': "My Skills",
        'programming_skills': [
            {'name': 'Python', 'level': 'Advanced', 'experience': '3+ years'},
            {'name': 'Django', 'level': 'Intermediate', 'experience': '2+ years'},
            {'name': 'JavaScript', 'level': 'Intermediate', 'experience': '2+ years'},
            {'name': 'HTML/CSS', 'level': 'Advanced', 'experience': '4+ years'},
            {'name': 'Bootstrap', 'level': 'Advanced', 'experience': '3+ years'},
        ],
        'tools': ['Git', 'VS Code', 'PostgreSQL', 'SQLite', 'Docker'],
        'soft_skills': ['Problem Solving', 'Team Work', 'Communication', 'Time Management']
    }
    return render(request, 'blog/skills.html', context)


def admin(request):
    # Note: This conflicts with Django's built-in admin
    # Better to rename this to avoid conflicts
    context = {
        'title': "Admin Panel",
        'message': "Custom admin page"
    }
    return render(request, 'blog/admin.html', context)


def page_not_found(request, exception):
    return render(request, 'blog/404.html', status=404)

def server_error(request):
    return render(request, 'blog/500.html', status=500)

def about_view(request):
    context = {
        'title': "About View",
        'info': "This is an about view page"
    }
    return render(request, 'blog/about_view.html', context)
def contact_view(request):
    context = {
        'title': "Contact View",
        'info': "This is a contact view page"
    }
    return render(request, 'blog/contact_view.html', context)
def works_view(request):
    context = {
        'title': "Works View",
        'info': "This is a works view page"
    }
    return render(request, 'blog/works_view.html', context)
def favorite_works_view(request):
    context = {
        'title': "Favorite Works View",
        'info': "This is a favorite works view page"
    }
    return render(request, 'blog/favorite_works_view.html', context)
def favorite_song_view(request):
    context = {
        'title': "Favorite Song View",
        'info': "This is a favorite song view page"
    }
    return render(request, 'blog/favorite_song_view.html', context)
def index_view(request):
    context = {
        'title': "Index View",
        'info': "This is an index view page"
    }
    return render(request, 'blog/index_view.html', context)
def admin_view(request):
    context = {
        'title': "Admin View",
        'info': "This is an admin view page"
    }
    return render(request, 'blog/admin_view.html', context)
def custom_404_view(request, exception):
    return render(request, 'blog/custom_404.html', status=404)
def custom_500_view(request):
    return render(request, 'blog/custom_500.html', status=500)
def home(request):
    context = {
        'title': "Home",
        'welcome_message': "Welcome to the Home Page"
    }
    return render(request, 'blog/home.html', context)
def post(request):
    context = {
        'title': "Post",
        'post_content': "This is a sample post content."
    }
    return render(request, 'blog/post.html', context)
