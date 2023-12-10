from django.contrib.auth.decorators import login_required
from allauth.account.views import PasswordChangeView
from django.urls import reverse_lazy
from django.shortcuts import render  , redirect
from users.models import CustomUser



class LoginAfterPasswordChangeView(PasswordChangeView):
    @property
    def success_url(self):
        return reverse_lazy("dashboard")

login_after_password_change = login_required(LoginAfterPasswordChangeView.as_view())