from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from network.models import User, Post
from django import forms
from django.db.models import Count




import time

MAX_POSTS_PER_PAGE = 10

#create a new post form class
class NewPostForm(forms.Form):
    
    post_text = forms.Field(widget=forms.Textarea(
        {'rows': '3', 'maxlength': 160, 'class': 'form-control', 'placeholder': "What's the latest?"}),
        label="New Post", required=True)


def index(request):

    # check for authentication 
    if request.user.is_authenticated:
        user = request.session['_auth_user_id']
        posts = Post.objects.filter().order_by('_post_date').annotate(current_like=Count(likes.vales('id')))
    else:
        posts = Post.objects.order_by('-post_date').all()

    return render(request, "network/index.html", {
        'posts': page_obj,
        'form': NewPostForm(),
        'form_edit': NewEditPostForm()
    })

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

def postmessage(request):
    if request.method == "POST":
        form = NewPostForm(request.POST)
        if form.is_valid(): 
            user = User.objects.get(id=request.session['_auth_user_id'])
            text = form.cleaned_data["post_text"]
            post = Post(user=user, text=text)
            post.save() 
            return HttpResponseRedirect(reverse("index"))
    else: 
        return HttpResponseRedirect(reverse("index"))