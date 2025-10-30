from django.urls import path
from .views import registration, login, logout, activate_user, profile, toggle_save_post, profile_update

urlpatterns = [
    path('registration/', registration, name="registration"),
    path('login/', login, name="login"),
    path('logout/', logout, name="logout"), 
    path('activate/<uid>/<user_token>/', activate_user, name="activate"),
    path('profile/me/', profile, name="profile"),
    path('profile/<username>/', profile, name="profile_user"),
    path('entry/<int:blog_id>/toggle_save/', toggle_save_post, name="toggle_save_post"),
    path('profile/user/update/', profile_update, name="profile_update"),

]