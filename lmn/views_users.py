from django.shortcuts import render, redirect

from .models import Venue, Artist, Note, Show, UserInfo
from .forms import VenueSearchForm, NewNoteForm, ArtistSearchForm, UserRegistrationForm, UserEditForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse, Http404

def user_profile(request, user_pk):
    """Render a user profile page."""

    user = User.objects.get(pk=user_pk)
    
    usernotes = Note.objects.filter(user=user).order_by('posted_date').reverse()

    about_me = user.userinfo.about_me if user.userinfo else "YO"
    return render(request, 'lmn/users/user_profile.html', {'user' : user , 'notes' : usernotes, 'about_me': about_me })

def user_profile_photo(request, user_pk):
    user = User.objects.get(pk=user_pk)

    uinfo = user.userinfo
    if uinfo is None:
        return Http404("No such photo.")

    photo = uinfo.user_photo
    ctype = uinfo.user_photo_type
    return HttpResponse(photo, content_type=ctype)

@login_required
def my_user_profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES)
        if form.is_valid():
            user.username = form.cleaned_data["user_name"]
            user.first_name = form.cleaned_data["user_first"]
            user.last_name = form.cleaned_data["user_last"]
            user.email = form.cleaned_data["user_email"]
            about_me=form.cleaned_data["user_about_me"]
            photo = request.FILES["user_photo"]

            if user.userinfo is None:
                user.userinfo = UserInfo()

            user.userinfo.about_me = about_me
            user.userinfo.user_photo_type = photo.content_type
            user.userinfo.user_photo_name = photo.name
            user.userinfo.user_photo = photo.read()

            user.save()
            user.userinfo.save()
        else:
            raise RuntimeError(form.errors)

    uinfo = user.userinfo
    if uinfo:
        about_me = uinfo.about_me
        photo = uinfo.user_photo
    else:
        about_me = "The rain in Spain falls mainly in the plain."
        photo = None 

    form = UserEditForm({"user_name": user.username,
                         "user_first": user.first_name,
                         "user_last": user.last_name,
                         "user_email": user.email,
                         "user_about_me": about_me,
                         "user_photo": photo})
    return render(request, 'lmn/users/my_user_profile.html', {'form': form, 'user': user})

def register(request):

    if request.method == 'POST':

        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user = authenticate(username=request.POST['username'], password=request.POST['password1'])
            login(request, user)
            return redirect('lmn:homepage')
            
        else:
            message = 'Please check the data you entered'
            return render(request, 'registration/register.html', {'form': form, 'message': message})

    else:
        form = UserRegistrationForm()
        return render(request, 'registration/register.html', {'form': form})
