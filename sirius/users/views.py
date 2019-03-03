from django.conf import settings
from django.contrib.auth import login, authenticate, get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from .forms import AccountTypeUpdateForm, AccountUpdateForm, UserCreateForm
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

    def send_activation_email(self, request, user, form, token):
        current_site = get_current_site(request)
        uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
        activation_link = "{0}/activate/?uid={1}&token={2}".format(current_site, uid, token)
        subject = 'Activate your account'
        message = "Hello {0}, \n {1}".format(user.first_name, activation_link)
        to_email = form.cleaned_data.get('email')
        user.email_user(subject, message)

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = self.get_context_data(form=form)
        if not form.is_valid():
            return self.form_invalid(form)
        user = form.save()
        token = account_activation_token.make_token(user)
        self.send_activation_email(request, user, form, token)
        return HttpResponse('Please Confirm your email address to complete the registration')

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return render(self.request, self.get_template_names(), context)


class AccountUpdateView(LoginRequiredMixin, UpdateView):

    model = BaseUser
    form_class = AccountUpdateForm
    template_name = 'users/account_update_form.html'

    def get_object(self):
        return self.request.user

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
        return redirect("users:account-detail")

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return render(self.request, self.get_template_names(), context)


class AccountTypeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):

    model = BaseUser
    form_class = AccountTypeUpdateForm
    template_name = 'users/account_type_update_form.html'

    def test_func(self):
        return self.request.user.account_type == 'FA'

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
        if request.user == user:
            return redirect("users:account-detail")
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
        return self.request.user.account_type == 'FA'


class UserDetailView(LoginRequiredMixin, DetailView):
    ''' Displays details of an article. Allows a user to hide their private articles from
        other users. Additionally, unauthenticated users may not view certain types of articles '''

    model = BaseUser
    context_object_name = 'user'
    template_name = 'users/user_detail.html'



class AccountDetailView(LoginRequiredMixin, DetailView):
    ''' Displays details of an article. Allows a user to hide their private articles from
        other users. Additionally, unauthenticated users may not view certain types of articles '''

    model = BaseUser
    context_object_name = 'user'
    template_name = 'users/account_detail.html'
    
    def get_object(self):
        return self.request.user
            
User = get_user_model()


class UserActivateView(View):

    template_name = 'users/user_activate_form.html'

    def get(self, request):
        uidb64 = request.GET.get('uid')
        token = request.GET.get('token')
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        print(uid, user, token)
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
        return redirect('articles:article-list')
            

