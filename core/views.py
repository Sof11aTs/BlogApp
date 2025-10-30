from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def index(request):
    from .models import BlogEntry
    from django.contrib.auth.models import User

    posts = BlogEntry.objects.order_by("-created_at").all()
    r_posts = BlogEntry.objects.order_by("-rating").all()

    if request.method == "POST":
        email = request.POST.get("email")
        print(email)

        if email:
            user = User.objects.filter(email=email).first()
            if not user:
                messages.error(request, "Account with this email do not exists!")
                return redirect("registration")

            profile = user.profile
            if profile.newsletter_subscription:
                messages.error(request, "You are already subscribed to our newsletter!")

            profile.newsletter_subscription = True
            profile.save()
            messages.success(request, "You sucsesfuly subscribed to our newsletter!")
            return redirect("home")
        
        else:
            return redirect("registration")

    return render(request, "index.html", context={"posts": posts[0:4], "r_posts": r_posts[0:4]})

def all_blog_entrys(request):
    from .models import BlogEntry, Categorys

    category_name = request.GET.get("category")

    if category_name:
        posts = BlogEntry.objects.filter(category__title=category_name).order_by("-created_at").all()
    else:
        posts = BlogEntry.objects.order_by("-created_at").all()


    categorys = Categorys.objects.all()

    return render(request, "all_entrys.html", context={"posts": posts, "categorys":categorys})

@login_required
def create_blog_entry(request):
    from .models import BlogEntry, Categorys
    from .forms import BlogEntryForm
    from django.contrib.auth.models import User
    from django.template.loader import render_to_string
    from users.views import send_email

    form = BlogEntryForm()

    if request.method == "POST":
       form = BlogEntryForm(request.POST)
       if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            form = BlogEntryForm()
            messages.success(request, "Blog entry created successfully!")

            suscribers = User.objects.filter(profile__newsletter_subscription=True).all()
           
            html_message = render_to_string("emails/new_post.html", context={"entry": entry})
            send_email(
                request,
            "BlogApp: There is new post!",
            "There is new post on our website in which you might be interested!",
            html_message,
            [suscriber.email for suscriber in suscribers],
            
            )

        
    return render(request, "create_blog_entry.html", {"form": form, "title": "Create entry", "update_entry": False})

@login_required
def update_entry(request, blog_id):
    from .models import BlogEntry
    from .forms import BlogEntryForm
    from django.shortcuts import get_object_or_404
    from django.contrib import messages

    blog = get_object_or_404(BlogEntry, id=blog_id)
    form = BlogEntryForm(instance=blog)
    user = request.user

    if user != blog.user:
        messages.error(request, "You dont have permission to redacte this entry!")
        return redirect("home")


    if request.method == "POST":       
        form = BlogEntryForm(request.POST, instance=blog)
        if form.is_valid():
                form.save()
                form = BlogEntryForm()
                messages.success(request, "Blog entry updated successfully!")
                return redirect("profile")
        else:
            print("error")
            form = BlogEntryForm(instance=blog)


    return render(request, "create_blog_entry.html", {"form": form, "title": "Update entry", "update_entry": True, "blog": blog})

@login_required
def delete_blog_entry(request, blog_id):
    from django.shortcuts import get_object_or_404
    from .models import BlogEntry

    blog = get_object_or_404(BlogEntry, id=blog_id)
    user = request.user
    if user != blog.user:
        messages.error(request, "You dont have permission to delete this entry!")
        return redirect("home")
    else:
        blog.delete()  
        messages.success(request, "Blog entry deleted successfully!")
        return redirect("profile")

def blog_entry(request, blog_id):
    from django.shortcuts import get_object_or_404
    from .models import BlogEntry, Comments
    from .forms import CommentForm
    from django.db.models import Avg

    blog = get_object_or_404(BlogEntry, id = blog_id)

    recommended_posts = (
        BlogEntry.objects.filter(category=blog.category)
        .exclude(id=blog.id)
        .order_by("-created_at")[:4]
    )


    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.blog_entry = blog
            comment.save()
            messages.success(request, "Comment created successfully!")

            blog.rating=blog.comments.aggregate(Avg("stars"))["stars__avg"]
            blog.save()

            form = CommentForm()
    else:
        form = CommentForm()

    comments = Comments.objects.filter(blog_entry=blog).order_by("-created_at").all()
    if request.user.is_authenticated:
        is_post_saved =  blog.savers.filter(user=request.user).exists() 
    else: 
        is_post_saved = False

    return render(request, "blog_entry.html",
                  context={"blog": blog,
                            "recommended_posts": recommended_posts, 
                            "form":form, "comments":comments, 
                            "is_post_saved": is_post_saved, 
                            })

def about(request):
    return render(request, "about.html")

