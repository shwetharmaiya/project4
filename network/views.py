from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.template import loader

from .models import User, Post


def index(request):
    user = User.objects.get(pk=request.user.id)
    posts = Post.objects.filter(user_id=user).order_by('-post_timestamp')
    
    template = loader.get_template('network/index.html')
    
    context = {'posts': posts }
    
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
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

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

def get_post(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
        context = {'post': post}
    except Post.DoesNotExist:
        post = None
        context = {}

    template = loader.get_template('network/post.html')
    return HttpResponse(template.render(context, request))
