from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="shortener/login.html"),
        name="login",
    ),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("create/", views.create_url, name="create_url"),
    path("edit/<str:short_code>/", views.edit_url, name="edit_url"),
    path("delete/<str:short_code>/", views.delete_url, name="delete_url"),
    path("analytics/", views.analytics, name="analytics"),
    path(
        "url/<str:short_code>/analytics/",
        views.url_detail_analytics,
        name="url_detail_analytics",
    ),
    path("<str:short_code>/", views.redirect_url, name="redirect"),
]
