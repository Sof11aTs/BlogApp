from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def send_email(request, subject, message, html_content, recipient_list):
    from django.core.mail import EmailMultiAlternatives
    from django.conf import settings

    msg = EmailMultiAlternatives(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        recipient_list,
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()

def activate_user(request, uid, user_token):
    from django.contrib.auth.models import User
    from .token import account_activation_token
    from django.utils.http import urlsafe_base64_decode
    from django.utils.encoding import force_str
    from django.shortcuts import get_object_or_404

    user_id = force_str(urlsafe_base64_decode(uid))
    user = get_object_or_404(User, pk=user_id)

    if user is not None and account_activation_token.check_token(user, user_token):
        user.is_active = True
        user.save()

        messages.success(request, "Your account successfully activated!")
        return redirect("login")
    else:
        messages.error(request, "Activation link is invalid")
        return redirect("registration")

def registration(request):
    from .forms import RegistrationForm
    from django.template.loader import render_to_string
    from .token import account_activation_token   
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes
    from .models import Profile

    form = RegistrationForm()

    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            profile = Profile.objects.create(user=user)
            profile.save()

            user_token = account_activation_token.make_token(user)
            print(user_token)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            print(uid)

            html_message = render_to_string(
                "emails/registration_confirm.html",
                context={"user": user, "uid": uid, "user_token": user_token},
            )

            send_email(
                request,
                "BlogApp: Registration Confirm",
                "Confirm your registration",
                html_message,
                [user.email],
            )
           
            messages.success(request, "Sucsesful registration.")
            return redirect("login")
        messages.error(request, "Invalid password or Username/Email")

    return render(request, "registration.html", {"form":form})

def login(request):
    from .forms import LoginForm
    from django.contrib.auth import login

    form = LoginForm()

    if request.method == "POST":
       form = LoginForm(request.POST)
       if form.is_valid():
           user = form.cleaned_data["user"]          

           login(request, user)

           messages.success(request, f"Welcome back, {user.username}!")
        
           return redirect("home")
       messages.error(request, "Incorrect password or Username/Email")

    return render(request, "login.html", {"form":form})


def logout(request):
    from django.contrib.auth import logout

    logout(request)

    return redirect("home")

@login_required
def profile(request, username=None):
    from .models import Profile
    from core.models import BlogEntry, SavedPosts
    from django.shortcuts import get_object_or_404
    from django.contrib.auth.models import User

    if username:
        user=get_object_or_404(User, username=username)
        profile = get_object_or_404(Profile, user=user)

    else:
        profile = request.user.profile
        user = request.user

    u_posts = BlogEntry.objects.filter(user=user).order_by("-created_at").all()
    s_posts = SavedPosts.objects.filter(user=user).order_by("-created_at").all()

    return render(request, "profile.html", context={"user": user, "profile": profile, "u_posts": u_posts, "s_posts": s_posts})

@login_required
def toggle_save_post(request, blog_id):
    from core.models import BlogEntry, SavedPosts
    from django.shortcuts import get_object_or_404
    from django.contrib import messages
    from django.http import JsonResponse
    
    if request.method == "POST":
        post = get_object_or_404(BlogEntry, id=blog_id)
        saved_posts, created = SavedPosts.objects.get_or_create(user=request.user, post=post)

        if not created:
            saved_posts.delete()
            is_saved = False
            message = "Post removed from saved"

        else:
            is_saved = True
            message = "Post added to saved"

        return JsonResponse(
            {"isSaved": is_saved, "message": message, "savedCount": post.savers.count()}
        )

    return JsonResponse({"error": "Invalid method!"}, status=405)

@login_required
def profile_update(request):
    import json
    from django.http import JsonResponse
    from django.contrib.auth.models import User
    from django.core.validators import validate_email

    if request.method == "POST":
        try:
            user = request.user
            profile = user.profile

            # get data

            data = json.loads(request.body)

            # username
            new_username = data.get("username", "").strip()

            if len(new_username) < 3:
                return JsonResponse({"sucsess":False, "error": "Username must be at least 3 characters long."}, status=400)
            
            if User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
                return JsonResponse({"sucsess":False, "error": "Username already exists."}, status=400)
            
            user.username = new_username

            # email
            new_email = data.get("email", "").strip()
            try:
                validate_email(new_email)
            except ValueError:
                return JsonResponse(
                    {
                        "success": False,
                        "error": "Invalid email adress format!",
                    },
                    status=400,
                )
            user.email = new_email

            # first name
            new_first_name = data.get("first_name", "").strip()
            user.first_name = new_first_name

            # last name
            new_last_name = data.get("last_name", "").strip()
            user.last_name = new_last_name

            # bio
            new_bio = data.get("bio", "").strip()
            user.profile.bio = new_bio

            # save
            profile.save()
            user.save()

            return JsonResponse({"sucsess":True, 
                                 "message": "Profile updated successfully!", 
                                 "user":{
                                     "username": user.username,
                                     "email": user.email,
                                     "first_name": user.first_name,
                                     "last_name": user.last_name,
                                     "bio": user.profile.bio,
                                 }})
            
        except json.JSONDecodeError:
            return JsonResponse({"sucsess":False, "error": "Invalid JSON data."}, status=400)

        except Exception as e:
            return JsonResponse(
                {
                    "success": False,
                    "error": f"An error: {str(e)}",
                },
                status=500,
            )