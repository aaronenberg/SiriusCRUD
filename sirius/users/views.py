from django.conf import settings
from django.contrib.auth import (
    login,
    authenticate,
    get_user_model,
    update_session_auth_hash,
    views as auth_views,
)
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from .forms import (
    AccountUpdateForm,
    AccountUpdateFormPrivileged,
    AuthenticationForm,
    UserCreateForm,
    PasswordChangeForm,
    AuthenticationForm,
)
from .models import BaseUser
from .tokens import account_activation_token


class UserCreateView(UserPassesTestMixin, CreateView):

    model = BaseUser
    form_class = UserCreateForm
    template_name = 'users/user_create_form.html'

    def test_func(self):
        return not self.request.user.is_authenticated

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = self.get_context_data(form=form)
        return render(request, self.get_template_names(), context)

    def send_activation_email(self, request, user, token):
        current_site = get_current_site(request)
        uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
        activation_link = "{0}/activate/?uid={1}&token={2}".format(current_site, uid, token)
        subject = 'Activate your account'
        html_message = render_to_string(
            'registration/activation_mail.html',
            {'activation_link': activation_link, 'user': user}
        )
        message = strip_tags(html_message)
        user.email_user(subject, message, html_message=html_message)

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = self.get_context_data(form=form)
        if not form.is_valid():
            return self.form_invalid(form)
        user = form.save()
        token = account_activation_token.make_token(user)
        self.send_activation_email(request, user, token)
        return HttpResponse('A confirmation email has been sent to your email address. Please confirm your email to activate your account.')

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return render(self.request, self.get_template_names(), context)


class AccountUpdateView(LoginRequiredMixin, UpdateView):

    model = BaseUser
    form_class = AccountUpdateForm
    template_name = 'users/account_update_form.html'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users_courses'] = self.request.user.courses.all().order_by('subject', 'number')
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = self.get_context_data(form=form)
        return render(request, self.get_template_names(), context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if not form.is_valid():
            return self.form_invalid(form)
        user = form.save()
        messages.success(request, 'Account changes saved')
        return redirect("users:account-update")

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return render(self.request, self.get_template_names(), context)


class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):

    model = BaseUser
    form_class = AccountUpdateFormPrivileged
    template_name = 'users/account_update_form.html'

    def test_func(self):
        return self.request.user.user_type == 'FA'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user == self.object:
            return redirect("users:account-update")
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = self.get_context_data(form=form)
        return render(request, self.get_template_names(), context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if not form.is_valid():
            return self.form_invalid(form)
        user = form.save()
        return redirect("users:user-detail", pk=user.pk)

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return render(self.request, self.get_template_names(), context)


class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):

    model = BaseUser
    context_object_name = 'users'
    queryset = BaseUser.objects.filter(is_active=True)
    template_name = 'users/user_list.html'

    def test_func(self):
        return self.request.user.user_type == 'FA'


class UserDetailView(LoginRequiredMixin, DetailView):
    ''' Displays details of a user. '''

    model = BaseUser
    context_object_name = 'user_object'
    template_name = 'users/user_detail.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user == self.object:
            return redirect("users:account-update")
        return super().get(request, *args, **kwargs)


User = get_user_model()

class UserActivateView(View):

    template_name = 'users/user_activate_form.html'

    def get(self, request):
        uidb64 = request.GET.get('uid')
        token = request.GET.get('token')
        user = self.get_user(uidb64)
        if not user or not token:
            raise Http404()
        if not account_activation_token.check_token(user, token):
            return HttpResponse('Activation link is invalid!')
        user.is_active = True
        user.save()
        login(request, user, backend='users.auth.EmailBackend')
        form = SetPasswordForm(request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = SetPasswordForm(request.user, request.POST)
        if not form.is_valid():
            pass
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect('courses:course-list')

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        return user
            

class PasswordChangeView(auth_views.PasswordChangeView):
    form_class = PasswordChangeForm


class LoginView(auth_views.LoginView):
    form_class = AuthenticationForm
