from django.urls import path
from accounts import views as av

app_name = "accounts"

urlpatterns = [
    # Auth
    path("login/", av.login_view, name="login"),
    path("logout/", av.logout_view, name="logout"),
    # Branch management
    path("accounts/branches/", av.branch_list, name="branch_list"),
    path("accounts/branches/new/", av.branch_create, name="branch_create"),
    path("accounts/branches/<int:pk>/edit/", av.branch_edit, name="branch_edit"),
    # User management
    path("accounts/users/", av.user_list, name="user_list"),
    path("accounts/users/new/", av.user_create, name="user_create"),
    path("accounts/users/<int:pk>/edit/", av.user_edit, name="user_edit"),
    path("accounts/users/<int:pk>/delete/", av.user_delete, name="user_delete"),
    path("accounts/branches/<int:pk>/delete/", av.branch_delete, name="branch_delete"),
]
