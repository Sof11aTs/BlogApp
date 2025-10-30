from django.urls import path
from .views import index, create_blog_entry, all_blog_entrys, blog_entry, about, delete_blog_entry, update_entry

urlpatterns = [
    path('', index, name="home"),
    path('entrys/create_entrys/', create_blog_entry , name="create_blog_entry"),
    path('all_entrys/', all_blog_entrys, name="all_blog_entrys"),
    path('entrys/<int:blog_id>/', blog_entry, name="blog_entry"),
    path('about/', about, name="about"),
    path('entrys/<int:blog_id>/delete/', delete_blog_entry, name="delete_blog_entry"),
    path('entry/<int:blog_id>/update/', update_entry, name="update_entry"),
    
]