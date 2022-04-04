from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.core.paginator import Paginator

from .models import User, Post, Follow, Profile, Like
from .forms import ProfileForm

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)

import json #to use for json dumps

class PostListView(ListView):
    model = Post
    template_name = 'network/index.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-post_timestamp']
    paginate_by = 10

def index(request):
    user = User.objects.get(pk=request.user.id)
    posts = Post.objects.all().order_by('-post_timestamp')
    posts_and_likes = [(post, len(Like.objects.filter(post_id=post) )) for post in posts]
    paginator = Paginator(posts_and_likes, 10)

    user_liked_posts = set([like.post_id.id for like in Like.objects.filter(user_id=user)])

    template = loader.get_template('network/index.html')   

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'posts': posts ,  'posts_and_likes': posts_and_likes, 'user_liked_posts': user_liked_posts, 'page_obj': page_obj}
    
    return HttpResponse(template.render(context, request))
    #return render(request, "network/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return redirect(make_profile)
        #eturn HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

def make_profile(request):
    try:
        profile = Profile.objects.get(user_id=request.user.id)
    except Profile.DoesNotExist:
        profile = Profile()
        
    if request.method == 'POST':
        user = User.objects.get(pk=request.user.id)
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():  
            new_profile = form.save(commit=False)
            new_profile.user_id = user
            pic = request.FILES.get('id_profile_pic', False)
            if pic != False:
                new_profile.profile_pic = pic
            else: 
                new_profile.profile_pic = "profilepix/default_dog.jpg"
            new_profile.save()
            return redirect(index)
        else:
            return redirect(make_profile)            
    else:
        form = ProfileForm(instance=profile)
        context = { 'form' : form }
        return render(request, "network/make_profile.html", context) 


def submit_new_post(request):
    post_text = request.POST['new_post']
    # process post text 
    BLANK_LINE = '<p>&nbsp;</p>'
    broken_lines = post_text.split(BLANK_LINE)
    broken_lines = [line for line in broken_lines if not line.isspace() and line != '' ]

    post_text = BLANK_LINE.join(broken_lines)

    post_title = request.POST['new_post_title']
    
    user = User.objects.get(pk=request.user.id)

    new_post = Post(user_id=user, post_text=post_text, post_title=post_title)
    new_post.save()
   
    pk = new_post.pk

    return HttpResponse(pk)

def like_post(request):
    user_id = request.user.id
    user = None
    post = None
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return HttpResponse(status=400)
    post_id = request.POST.get('post_id', False)

    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return HttpResponse(status=400)

    if not user or not post:
        return HttpResponse(status=400)

    # check in like table if post is present
    try:
        like = Like.objects.get(user_id=user, post_id=post)
    except Like.DoesNotExist:
        # if not present, add new row with user id and post id
        new_like = Like(user_id=user, post_id=post)
        new_like.save()
        context = { 'num_likes' : len(Like.objects.filter(post_id=post_id))} 
        return HttpResponse(json.dumps(context), content_type="application/json", status=200)

    # if present, delete row
    like.delete()
    context = { 'num_likes' : len(Like.objects.filter(post_id=post_id)) } 
    return HttpResponse(json.dumps(context), content_type="application/json", status=200)

def user_context(request_obj):
    context = {}
    try:
        loggedin_obj = request_obj.user
    except User.DoesNotExist:
        loggedin_obj = None
    except AttributeError:
        loggedin_obj = None
    if loggedin_obj:
        user = User.objects.get(pk=request_obj.user.id)
        user_profile = Profile.objects.get(user_id=request_obj.user.id)
        user_followers = set([follow.followee_id.id for follow in Follow.objects.filter(follower_id=user)])
        user_liked_posts = set([like.post_id.id for like in Like.objects.filter(user_id=user)])
        profile_user_follows = [follow.followee_id for follow in Follow.objects.filter(follower_id=profile_user)]
        
        context['user_liked_posts'] = user_liked_posts
        context['user_followers'] = user_followers
        context['user_profile'] = user_profile
        context['user_follows']= profile_user_follows
    return context

def get_user_profile(request, user_id):
    try:
        profile_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        profile_user = None
    if profile_user:
        user_posts = Post.objects.filter(user_id=profile_user).order_by('-post_timestamp')
        posts_and_likes = [(post, len(Like.objects.filter(post_id=post) )) for post in user_posts]
    
        context = {'profile_user': profile_user, 'posts': user_posts,'posts_and_likes': posts_and_likes}
    else:
        context = {}

    template = loader.get_template('network/user_posts.html')
    return HttpResponse(template.render(context, request))

def get_user_profile_likes(request, user_id):
    try:
        profile_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        profile_user = None
    if profile_user:
        profile_user_profile = Profile.objects.get(user_id=profile_user)
        profile_user_likes = [like.post_id for like in Like.objects.filter(user_id=profile_user)]
        profile_user_posts_and_likes = [(post, len(Like.objects.filter(post_id=post))) for post in profile_user_likes]


        profile_context = {'profile_user': profile_user, 
                   'profile_user_profile': profile_user_profile,
                   'profile_user_likes': profile_user_likes,
                   'profile_user_posts_and_likes': profile_user_posts_and_likes,
                    }
    else:
        profile_context = {}

    #loggedin_user_context = user_context(request)

    #context = {**profile_context, **loggedin_user_context}

    context = profile_context

    template = loader.get_template('network/user_likes.html')
    return HttpResponse(template.render(context, request))


def get_user_profile_follows(request, user_id):
    try:
        profile_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        profile_user = None
    if profile_user:
        profile_user_follows = [follow.followee_id for follow in Follow.objects.filter(follower_id=profile_user)]
        follows_profiles = Profile.objects.all().filter(user_id__in=profile_user_follows)
        profile_user_profile = Profile.objects.get(user_id=profile_user)
        
        profile_context = {'profile_user': profile_user,
                   'profile_user_profile': profile_user_profile,
                   'follows_profiles': follows_profiles,
                    }
    else:
        profile_context = {}

    #loggedin_user_context = user_context(request)

    #context = {**profile_context, **loggedin_user_context}

    context = profile_context

    template = loader.get_template('network/user_follows.html')
    return HttpResponse(template.render(context, request))

def get_user_profile_follows_posts(request, user_id):
    try:
        profile_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        profile_user = None
    if profile_user:
        profile_user_follows = [follow.followee_id for follow in Follow.objects.filter(follower_id=profile_user)]
        #follows_profiles = Profile.objects.all().filter(user_id__in=profile_user_follows)
        #follows_profiles_posts = [post for post in Post.objects.all().filter(user_id__in=profile_user_follows)]
        profile_user_profile = Profile.objects.get(user_id=profile_user)
        posts = Post.objects.all().filter(user_id__in=profile_user_follows).order_by('-post_timestamp')
        posts_and_likes = [(post, len(Like.objects.filter(post_id=post) )) for post in posts]
    
        profile_context = {'profile_user': profile_user,
                   'profile_user_profile': profile_user_profile,
                   'posts_and_likes': posts_and_likes,
                    }
    else:
        profile_context = {}

    #loggedin_user_context = user_context(request)

    #context = {**profile_context, **loggedin_user_context}

    context = profile_context

    template = loader.get_template('network/user_follows_posts.html')
    return HttpResponse(template.render(context, request))


def get_user_profile_followers(request, user_id):
    try:
        profile_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        profile_user = None
    if profile_user:
        profile_user_followers = [follow.follower_id for follow in Follow.objects.filter(followee_id=profile_user)]
        followers_profiles = Profile.objects.all().filter(user_id__in=profile_user_followers)
        profile_user_profile = Profile.objects.get(user_id=profile_user)

        print("num followers", len(profile_user_followers))
        print("num follower profiles", len(followers_profiles))

        profile_context = {'profile_user': profile_user,
                   'profile_user_profile': profile_user_profile,
                   'followers_profiles': followers_profiles,
                    }
    else:
        profile_context = {}

    #loggedin_user_context = user_context(request)

    #context = {**profile_context, **loggedin_user_context}

    context = profile_context

    template = loader.get_template('network/user_followers.html')
    return HttpResponse(template.render(context, request))

@login_required
def follow_user(request):
    follower_id = request.user.id
    followee_id = request.POST.get('user_id', False)
    print("Followee:")
    print(followee_id)

    if follower_id == followee_id:
        return HttpResponse(status=400)

    try:
        follower = User.objects.get(pk=follower_id)
        followee = User.objects.get(pk=followee_id)
    except User.DoesNotExist:
        return HttpResponse(status=400)
    # check in followers table if the following relationship exists.
    try:
        followship = Follow.objects.get(follower_id=follower, followee_id=followee)
    except:
        # if it does, delete record.
        new_followship = Follow(follower_id=follower, followee_id=followee)
        new_followship.save()
        return HttpResponse(status=204)
    # If not, add relationship.
    followship.delete()
    return HttpResponse(204)

@login_required
def listing(request):
    posts = Post.objects.all().order_by('-post_timestamp')
    paginator = Paginator(posts, 10) 

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'network/list.html', {'page_obj': page_obj})

@login_required
def edit_post(request):
    post_id = request.POST.get('post_id')
    if post_id is 0:  
        context = { }
    else: 
        context = {'post_id': post_id}
    return render(request, "network/edit_post.html", context)

def get_post(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
        context = {}
        context['text'] = post.post_text 
        context['title'] = post.post_title        
    except Post.DoesNotExist:
        post = None
        context = {}
    return HttpResponse(json.dumps(context), content_type="application/json")
