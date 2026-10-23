from django.urls import path
from django.contrib.auth import views as auth_views
from .views import ProfileView, profile_edit, signup
app_name = "accounts"

urlpatterns = [
    path('profile/', ProfileView.as_view(), name="profile"),
    path('profile/edit/', profile_edit, name="profile_edit"),
    path('login/', auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path('signup/', signup, name="signup"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    
]
