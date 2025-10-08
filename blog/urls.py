from django.urls import path, re_path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name="index"),
    path('favorite-song/', views.favorite_song, name="favorite-song"),
    path('about-me/', views.about_me, name="about-me"),
    path('contact-me/', views.contact_me, name="contact-me"),
    path('my-works/', views.my_works, name="my-works"),
    path('favorite-works/', views.favorite_works, name="favorite-works"),
    path('skills/', views.skills, name="skills"),
    path('post/<int:pk>/', views.post_detail, name='post-detail'),
    re_path(r'^post/(?P<slug>[\w\-\u0100-\uFFFF]+)/$', views.post_detail_by_slug, name='post-detail-slug'),
    re_path(r'^category/(?P<slug>[\w\-\u0100-\uFFFF]+)/$', views.category_posts, name='category-posts'),
    re_path(r'^tag/(?P<tag_name>[\w\-\u0100-\uFFFF\s]+)/$', views.tag_posts, name='tag-posts'),
    path('search/', views.search_posts, name='search'),
    path('create-post/', views.PostCreateView.as_view(), name='add-post'),
]
