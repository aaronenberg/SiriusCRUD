from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.edit import CreateView
from .forms import UserCreateForm
from .models import BaseUser


class UserCreateView(UserPassesTestMixin, CreateView):

    template_name = 'users/user_create.html'
    model = BaseUser
    form_class = UserCreateForm

    def test_func(self):
        return not self.request.user.is_authenticated

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = self.get_context_data(form=form)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = self.get_context_data(form=form)
        if not form.is_valid():
            return self.form_invalid(form)
        return self.create_user_and_login(form)

    def create_user_and_login(self, form):
        user = form.save()
        email = form.cleaned_data['email']
        password = form.cleaned_data['password1']
        user = authenticate(email=email, password=password)
        login(self.request, user)
        return redirect('article-list')

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return render(self.request, self.template_name, context)
