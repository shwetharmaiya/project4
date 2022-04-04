
from django.urls import path

from .views import (
    PostListView,
    )

from . import views

urlpatterns = [
    path("", PostListView.as_view(), name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_post", views.submit_new_post, name="new_post"),
    path('post/<int:post_id>', views.get_post, name='post'),
    path('likepost', views.like_post, name='like_a_post'),
    path('u/<int:user_id>', views.get_user_profile, name='user_profile'),
    path('u/<int:user_id>/likes', views.get_user_profile_likes, name='user_profile_likes'),
    path('u/<int:user_id>/follows', views.get_user_profile_follows, name='user_profile_follows'),
    path('u/<int:user_id>/follows_posts', views.get_user_profile_follows_posts, name='user_profile_follows_posts'),
    path('make_profile', views.make_profile, name='edit_your_profile'),
    path('followuser', views.follow_user, name='follow_a_user'),
    path('u/<int:user_id>/followers', views.get_user_profile_followers, name='user_profile_followers'),
    path("listing", views.listing, name="listing"),
    path('edit_post', views.edit_post, name='edit_post'),    
    path('get_post/<int:post_id>', views.get_post, name='get_post'),
]
