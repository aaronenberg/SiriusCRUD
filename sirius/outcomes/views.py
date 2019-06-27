from collections import namedtuple
import copy
import re
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Q
from django.middleware.csrf import CsrfViewMiddleware
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.datastructures import MultiValueDict
from django.views.decorators.csrf import csrf_exempt, csrf_protect, requires_csrf_token
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from courses.models import Course
from .utils import (
    get_course_from_url,
    flatten_formset_file_fields,
    update_files_formset,
    prepare_search_term,
)
from .models import Outcome, OutcomeMedia
from .forms import (
    OutcomeForm, 
    OutcomeMediaFormSet,
    OutcomeMediaDirectoryFormSet,
    OutcomeMediaUpdateFormSet,
    OutcomeSubmissionsUpdateFormSet,
)

class OutcomeCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    ''' Displays a form to create a new outcome and a separate form for uploaded attachments
        only for authenticated users '''

    template_name_suffix = '_create_form'
    model = Outcome
    form_class = OutcomeForm

    def test_func(self):
        return self.request.user.is_privileged

    def get_form_kwargs(self):
        kwargs = super(OutcomeCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = None
        referer_page = self.request.META.get('HTTP_REFERER')
        self.initial = {'course': get_course_from_url(referer_page)}
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        outcomemedia_form = OutcomeMediaFormSet()
        outcomemediadirectory_form = OutcomeMediaDirectoryFormSet(prefix='directory')
        context = self.get_context_data(
            form=form,
            outcomemedia_form=outcomemedia_form,
            outcomemediadirectory_form=outcomemediadirectory_form
        )
        return render(request, self.get_template_names(), context)

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        outcomemedia_form = OutcomeMediaFormSet(
            request.POST,
            request.FILES,
            instance=form.instance
        )
        outcomemediadirectory_form = OutcomeMediaDirectoryFormSet(
            request.POST,
            request.FILES.copy(),
            instance=form.instance,
            prefix='directory',
        )
        context = self.get_context_data(
            form=form,
            outcomemedia_form=outcomemedia_form,
            outcomemediadirectory_form=outcomemediadirectory_form
        )
        if not all([form.is_valid(),
                    outcomemedia_form.is_valid(),
                    outcomemediadirectory_form.is_valid()]):
            return self.form_invalid(form, outcomemedia_form, outcomemediadirectory_form, context)
        return self.form_valid(form, outcomemedia_form, outcomemediadirectory_form)

    def form_valid(self, form, outcomemedia_form, outcomemediadirectory_form):
        form.instance.author = self.request.user
        form.instance.is_public = True
        if '_save_draft' in self.request.POST.keys():
            form.instance.is_public = False
        outcome = form.save()
        directory_fields = [k for k in outcomemedia_form.files.keys() if k.startswith('directory')]
        file_fields = [k for k in outcomemedia_form.files.keys() if not k.startswith('directory')]
        for k in directory_fields:
            outcomemedia_form.files.pop(k)
        for k in file_fields:
            outcomemediadirectory_form.files.pop(k)
        # for a file field to accept multiple files we save each file, creating a new OutcomeMedia object
        outcomemedia = flatten_formset_file_fields(outcomemediadirectory_form)
        outcomemedia += flatten_formset_file_fields(outcomemedia_form)
        for media in outcomemedia:
            media.author = self.request.user
            media.is_public = True
            media.save()
        return redirect(outcome.get_absolute_url())

    def form_invalid(self, form, outcomemedia_form, outcomemediadirectory_form, context):
        return render(self.request, self.get_template_names(), context)


class OutcomeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    ''' Displays a form to update an existing outcome for the user that is
        the original author of the outcome. Form also contains files that were uploaded
        by the author. The post and any uploaded files are publicly visible unless the
        author saves the outcome as a draft.'''

    model = Outcome
    form_class = OutcomeForm
    template_name_suffix = '_update_form'

    def get_form_kwargs(self):
        kwargs = super(OutcomeUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_queryset(self):
        return Outcome.objects.exclude(Q(is_public=False))

    def test_func(self):
        return self.request.user == self.get_object().author or self.request.user.is_superuser

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        outcomemedia_form = OutcomeMediaFormSet(
            instance=form.instance,
            queryset=OutcomeMedia.objects.filter(
                author=form.instance.author,
                upload_directory=''
            )
        )
        outcomemediadirectory_form = OutcomeMediaDirectoryFormSet(
            prefix='directory',
            instance=form.instance,
            queryset=OutcomeMedia.objects.filter(
                author=form.instance.author).exclude(
                upload_directory=''
            )
        )
        context = self.get_context_data(
            form=form,
            outcomemedia_form=outcomemedia_form,
            outcomemediadirectory_form=outcomemediadirectory_form
        )
        return render(request, self.get_template_names(), context) 

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        outcomemedia_form = OutcomeMediaFormSet(request.POST, request.FILES, instance=form.instance)
        outcomemediadirectory_form = OutcomeMediaDirectoryFormSet(
            request.POST,
            request.FILES.copy(),
            instance=form.instance,
            prefix='directory',
        )
        context = self.get_context_data(
            form=form,
            outcomemedia_form=outcomemedia_form,
            outcomemediadirectory_form=outcomemediadirectory_form
        )
        actual_is_public = form.instance.is_public

        if not all([form.is_valid(), 
                    outcomemedia_form.is_valid(),
                    outcomemediadirectory_form.is_valid()]):
            # not using BooleanField widget in form for is_public. 
            # BooleanField default value is False if not marked in form
            form.instance.is_public = actual_is_public
            return self.form_invalid(form, outcomemedia_form, outcomemediadirectory_form, context)
        return self.form_valid(form, outcomemedia_form, outcomemediadirectory_form)

    def form_valid(self, form, outcomemedia_form, outcomemediadirectory_form):
        if '_save_draft' in self.request.POST:
            form.instance.is_public = False
        else:
            form.instance.is_public = True

        outcome = form.save()

        directory_fields = [k for k in outcomemedia_form.files.keys() if k.startswith('directory')]
        file_fields = [k for k in outcomemedia_form.files.keys() if not k.startswith('directory')]
        for k in directory_fields:
            outcomemedia_form.files.pop(k)
        for k in file_fields:
            outcomemediadirectory_form.files.pop(k)

        update_files_formset(outcomemedia_form)
        update_files_formset(outcomemediadirectory_form)
        if self.request.FILES:
            # for a file field to accept multiple files we save each file, creating a new OutcomeMedia object
            outcomemedia = flatten_formset_file_fields(outcomemediadirectory_form)
            outcomemedia += flatten_formset_file_fields(outcomemedia_form)
            for media in outcomemedia:
                media.author = self.request.user
                media.is_public = True
                media.save()
            for form in outcomemedia_form.deleted_forms + outcomemediadirectory_form.deleted_forms:
                form.instance.delete()
        return redirect(outcome.get_absolute_url())

    def form_invalid(self, form, outcomemedia_form, outcomemediadirectory_form, context):
        return render(self.request, self.get_template_names(), context)


Outcome_Media = namedtuple('Outcome_Media',
    ['outcome', 'raw_data', 'analyzed_data', 'curriculum', 'year_choices', 'semester_choices']
)

def get_outcome_media(request):
    outcome_slug = request.GET.get('outcome_slug')
    section = request.GET.get('section')
    year = request.GET.get('year')
    semester = request.GET.get('semester')

    if outcome_slug is None:
        raise ValueError("Need slug or primary key of an Outcome to get OutcomeMedia")
    outcome = Outcome.objects.get(slug=outcome_slug)
    if request.user.is_authenticated:
        raw_data = outcome.media.filter(outcome_type='RD', is_public=True)
    else:
        raw_data = None
    analyzed_data = outcome.media.filter(outcome_type='AD', is_public=True)
    curriculum = outcome.media.filter(outcome_type='CU', is_public=True)
    year_choices = outcome.media.all().distinct('year').exclude(year__isnull=True).values_list('year', flat=True)
    semester_choices = outcome.media.all().distinct('semester').exclude(semester__isnull=True).values_list('semester', flat=True)

    if section is not None:
        if raw_data:
            raw_data = raw_data.filter(section=section)
        analyzed_data = analyzed_data.filter(section=section)
        curriculum = curriculum.filter(Q(section=None) | Q(section=section))

    if year is not None:
        if raw_data:
            raw_data = raw_data.filter(year=year)
        analyzed_data = analyzed_data.filter(year=year)
        curriculum = curriculum.filter(Q(year=None) | Q(year=year))

    if semester is not None:
        if raw_data:
            raw_data = raw_data.filter(semester=semester)
        analyzed_data = analyzed_data.filter(semester=semester)
        curriculum = curriculum.filter(Q(semester=None) | Q(semester=semester))

    outcome_media = Outcome_Media(
        outcome,
        raw_data, 
        analyzed_data,
        curriculum,
        year_choices,
        semester_choices
    )
    return render(request, 'partials/outcome_media.html', {'outcome_media': outcome_media})

class OutcomeMediaUpdateView(UpdateView):
    '''
    Displays outcome details and a form for authenticated 
    users to submit files to the outcome. 
    '''

    template_name = 'outcomes/outcomemedia_update_form.html'
    context_object_name = 'outcome'
    model = Outcome

    def get_queryset(self):
        return Outcome.objects.exclude(Q(is_public=False))

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        raw_data = self.object.media.filter(outcome_type='RD', is_public=True)
        analyzed_data = self.object.media.filter(outcome_type='AD', is_public=True)
        curriculum = self.object.media.filter(outcome_type='CU', is_public=True)
        year_choices = self.object.media.all().distinct(
            'year').exclude(year__isnull=True).values_list('year', flat=True)
        semester_choices = self.object.media.all().distinct(
            'semester').exclude(semester__isnull=True).values_list('semester', flat=True)
        context['outcome_media'] = Outcome_Media(
            self.object,
            raw_data, 
            analyzed_data,
            curriculum,
            year_choices,
            semester_choices
        )
        return context
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = OutcomeMediaUpdateFormSet()
        context = self.get_context_data(form=form)
        return render(request, self.get_template_names(), context) 

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = OutcomeMediaUpdateFormSet(request.POST, request.FILES, instance=self.object)
        context = self.get_context_data(form=form)
        if not form.is_valid():
            return self.form_invalid(form) 
        messages.success(request, 'Submission complete - Your submission has been sent for review.')
        return self.form_valid(form)

    def form_valid(self, form):
        outcomemedia = flatten_formset_file_fields(form)
        for media in outcomemedia:
            media.author = self.request.user
            media.section = self.request.POST['section']
            media.save()
        return redirect(self.object.get_absolute_url())

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return render(self.request, self.get_template_names(), context)


class OutcomeSubmissionsUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):

    template_name = 'outcomes/outcome_submission_update_form.html'
    context_object_name = 'outcome'
    model = Outcome

    def test_func(self):
        return self.request.user == self.get_object().author or self.request.user.user_role == FACULTY

    def get_queryset(self):
        return Outcome.objects.filter(author=self.request.user)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = OutcomeSubmissionsUpdateFormSet(
                instance=self.object,
                queryset=OutcomeMedia.objects.filter(is_public=False)
        )
        context = self.get_context_data(form=form)
        return render(request, self.get_template_names(), context) 

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = OutcomeSubmissionsUpdateFormSet(request.POST, instance=self.object)
        context = self.get_context_data(form=form)
        if not form.is_valid():
            return self.form_invalid(form) 
        return self.form_valid(form)

    def form_valid(self, form):
        form.save()
        for outcomemedia in form.queryset:
            if outcomemedia.is_delete:
                outcomemedia.delete()
        if self.object.course:
            return redirect(self.object.course.get_absolute_url())
        return redirect(self.object.get_absolute_url())

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return render(self.request, self.get_template_names(), context)


class DraftListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    ''' Displays a list of the current user's unpublished drafts.
        The drafts in this list are only available to the currently logged in user. '''
    model = Outcome
    context_object_name = 'outcomes'

    template_name = 'outcomes/draft_list.html'

    def test_func(self):
        return self.request.user.is_privileged

    def get_queryset(self):
            return Outcome.objects.filter(Q(is_public=False), Q(author=self.request.user))


class DraftDetailView(UserPassesTestMixin, OutcomeMediaUpdateView):
    ''' Displays details of an outcome. Allows a user to hide their private outcomes from
        other users. Additionally, unauthenticated users may not view certain types of outcomes '''

    template_name = 'outcomes/outcome_detail.html'
    model = Outcome

    def test_func(self):
        return self.request.user.is_privileged and self.request.user == self.get_object().author

    def get_queryset(self):
        return Outcome.objects.filter(Q(is_public=False), Q(author=self.request.user))


class DraftUpdateView(OutcomeUpdateView):

    def get_queryset(self):
        return Outcome.objects.filter(Q(is_public=False), Q(author=self.request.user))


class IndexView(ListView):
    model = Outcome
    context_object_name = 'outcomes'
    template_name = 'outcomes/index.html'


class SearchResultsView(ListView):
    model = Outcome
    context_object_name = 'outcomes'
    template_name = 'outcomes/search_results_list.html'

    def get_queryset(self):
        queryset = Outcome.objects.filter(is_public=True)
        query = SearchQuery(prepare_search_term(self.request.GET.get('query', '')), search_type='raw')
        vector = SearchVector('title', weight='A') + SearchVector('description', weight='B')
        rank = SearchRank(vector, query)
        return Outcome.objects.annotate(rank=rank).filter(rank__gt=0.2).order_by('rank')[:20]


def get_course_sections(request):
    course_id = request.GET.get('course')
    course = Course.objects.get(pk=course_id)
    sections = course.sections
    return render(request, 'outcomes/section_dropdown_list_options.html', {'sections': sections})

