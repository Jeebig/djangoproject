from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('favorite-song/', views.favorite_song, name="favorite-song"),
    path('about-me/', views.about_me, name="about-me"),
    path('contact-me/', views.contact_me, name="contact-me"),
    path('my-works/', views.my_works, name="my-works"),
    path('favorite-works/', views.favorite_works, name="favorite-works"),
    path('skills/', views.skills, name="skills"),
    path('post/', views.post, name='post')

]
