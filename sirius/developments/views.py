import re
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.core.files.uploadedfile import UploadedFile
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.urls import reverse
from .utils import flatten_formset_file_fields, update_files_formset
from .models import Development, DevelopmentMedia
from .forms import DevelopmentForm, DevelopmentMediaFormSet
from outcomes.utils import prepare_search_term


class DevelopmentListView(ListView):
    '''
    Displays a list of developments that a user can click for a more detailed view of the development.
    '''
    model = Development
    context_object_name = 'developments'
    queryset = Development.objects.exclude(is_public=False).order_by('-modified')


class DevelopmentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    ''' Displays a form to create a new development and a separate form for uploaded attachments
        only for authenticated users '''

    template_name_suffix = '_create_form'
    model = Development
    form_class = DevelopmentForm

    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        developmentmedia_form = DevelopmentMediaFormSet()
        context = self.get_context_data(form=form, developmentmedia_form=developmentmedia_form)
        return render(request, self.get_template_names(), context)

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        developmentmedia_form = DevelopmentMediaFormSet(request.POST, request.FILES, instance=form.instance)
        context = self.get_context_data(form=form, developmentmedia_form=developmentmedia_form)
        if not all([form.is_valid(), developmentmedia_form.is_valid()]):
            return self.form_invalid(form, developmentmedia_form, context) 
        return self.form_valid(form, developmentmedia_form)

    def form_valid(self, form, developmentmedia_form):
        form.instance.author = self.request.user
        form.instance.is_public = True
        if '_save_draft' in self.request.POST:
            form.instance.is_public = False
        development = form.save()
        # for a file field to accept multiple files we save each file, creating a new DevelopmentMedia object
        developmentmedia = flatten_formset_file_fields(developmentmedia_form)
        for media in developmentmedia:
            media.author = self.request.user
            media.is_public = True
            media.save()
        return redirect(development.get_absolute_url())

    def form_invalid(self, form, developmentmedia_form, context):
        return render(self.request, self.get_template_names(), context)


class DevelopmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    ''' Displays a form to update an existing development for the user that is
        the original author of the development. Form also contains files that were uploaded
        by the author. The post and any uploaded files are publicly visible unless the
        author saves the development as a draft.'''

    model = Development
    form_class = DevelopmentForm
    template_name_suffix = '_update_form'
    
    def get_queryset(self):
        return Development.objects.exclude(Q(is_public=False))

    def test_func(self):
        return self.request.user.is_superuser and self.request.user == self.get_object().author

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        developmentmedia_form = DevelopmentMediaFormSet(
            instance=form.instance,
            queryset=DevelopmentMedia.objects.filter(author=form.instance.author))
        context = self.get_context_data(form=form, developmentmedia_form=developmentmedia_form)
        return render(request, self.get_template_names(), context) 

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        developmentmedia_form = DevelopmentMediaFormSet(request.POST, request.FILES, instance=form.instance)
        context = self.get_context_data(form=form, developmentmedia_form=developmentmedia_form)
        actual_is_public = form.instance.is_public
        if not all([form.is_valid(), developmentmedia_form.is_valid()]):
            # not using BooleanField widget in form. it's initial value is always False,
            # so is_public becomes False after calling form.is_valid()
            form.instance.is_public = actual_is_public
            return self.form_invalid(form, developmentmedia_form) 
        return self.form_valid(form, developmentmedia_form)

    def form_valid(self, form, developmentmedia_form):
        if '_save_draft' in self.request.POST:
            form.instance.is_public = False
        else:
            form.instance.is_public = True
        form.save()
        update_files_formset(developmentmedia_form)
        if self.request.FILES:
            developmentmedia = flatten_formset_file_fields(developmentmedia_form)
            for media in developmentmedia:
                media.author = self.request.user
                media.is_public = True
                media.save()
        return redirect(self.object.get_absolute_url())

    def form_invalid(self, form, developmentmedia_form):
        context = self.get_context_data(form=form, developmentmedia_form=developmentmedia_form)
        return render(self.request, self.get_template_names(), context)


class DevelopmentDetailView(DetailView):
    ''' Displays user-submitted posts for an development. Template hides form to 
        submit a post and certain types of developments from unauthenticated users.'''

    template_name = 'developments/development_detail.html'
    context_object_name = 'development'
    model = Development

    def get_queryset(self):
        return Development.objects.exclude(Q(is_public=False))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        media = DevelopmentMedia.objects.filter(development__pk=self.object.pk, is_public=True)
        context['developmentmedia_list'] = media
        types = [t['development_type'] for t in media.values('development_type')]
        context['DEVELOPMENT_TYPES'] = [t[1] for t in DevelopmentMedia.DEVELOPMENT_TYPES if t[0] in types]
        return context
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        return render(request, self.get_template_names(), context) 


class DraftListView(LoginRequiredMixin, UserPassesTestMixin, DevelopmentListView):
    ''' Displays a list of the current user's unpublished drafts.
        The drafts in this list are only available to the currently logged in user. '''

    template_name = 'developments/draft_list.html'

    def test_func(self):
        self.request.user.is_superuser

    def get_queryset(self):
            return Development.objects.filter(Q(is_public=False), Q(author=self.request.user))


class DraftDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    ''' Displays details of an development. Allows a user to hide their private developments from
        other users. Additionally, unauthenticated users may not view certain types of developments '''

    template_name = 'developments/development_detail.html'
    model = Development
    context_object_name = 'development'

    def test_func(self):
        self.request.user.is_superuser

    def get_queryset(self):
        return Development.objects.filter(Q(is_public=False), Q(author=self.request.user))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        media = DevelopmentMedia.objects.filter(development__pk=self.object.pk)
        context['developmentmedia_list'] = media
        types = [t['development_type'] for t in media.values('development_type')]
        context['DEVELOPMENT_TYPES'] = [t[1] for t in DevelopmentMedia.DEVELOPMENT_TYPES if t[0] in types]
        return context


class DraftUpdateView(DevelopmentUpdateView):

    def get_queryset(self):
        return Development.objects.filter(Q(is_public=False), Q(author=self.request.user))


class SearchResultsView(ListView):
    model = Development
    context_object_name = 'developments'
    template_name = 'developments/search_results_list.html'

    def get_queryset(self):
        queryset = Development.objects.filter(is_public=True)
        query = SearchQuery(prepare_search_term(self.request.GET.get('query', '')), search_type='raw')
        vector = SearchVector('title', weight='A') + SearchVector('description', weight='B')
        rank = SearchRank(vector, query)
        return Development.objects.annotate(rank=rank).filter(rank__gt=0.2).order_by('rank')[:20]
