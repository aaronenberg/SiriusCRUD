import re
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector
from django.core.files.uploadedfile import UploadedFile
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.urls import reverse
from courses.models import Course
from .utils import get_course_from_url, flatten_formset_file_fields, update_files_formset
from .models import Outcome, OutcomeMedia
from .forms import OutcomeForm, OutcomeMediaFormSet, OutcomeMediaUpdateFormSet


class OutcomeListView(ListView):
    ''' Displays a list of outcomes. Users are able to see all of their own outcomes, public or private,
        as well as other users' public outcomes. Additionally, unauthenticated users may not view 
        certain types of outcomes '''

    model = Outcome
    context_object_name = 'outcomes'
    queryset = Outcome.objects.exclude(is_public=False).order_by('-modified')


class OutcomeCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    ''' Displays a form to create a new outcome and a separate form for uploaded attachments
        only for authenticated users '''

    template_name_suffix = '_create_form'
    model = Outcome
    form_class = OutcomeForm

    def test_func(self):
        return self.request.user.is_privileged

    def get(self, request, *args, **kwargs):
        self.object = None
        referer_page = self.request.META.get('HTTP_REFERER')
        if referer_page and reverse('courses:course-list') in referer_page:
            course = get_course_from_url(referer_page)
            self.initial = {'course': course.pk}
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        outcomemedia_form = OutcomeMediaFormSet()
        context = self.get_context_data(form=form, outcomemedia_form=outcomemedia_form)
        return render(request, self.get_template_names(), context)

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        outcomemedia_form = OutcomeMediaFormSet(request.POST, request.FILES, instance=form.instance)
        context = self.get_context_data(form=form, outcomemedia_form=outcomemedia_form)
        if not all([form.is_valid(), outcomemedia_form.is_valid()]):
            return self.form_invalid(form, outcomemedia_form, context) 
        return self.form_valid(form, outcomemedia_form)

    def form_valid(self, form, outcomemedia_form):
        form.instance.author = self.request.user
        form.instance.is_public = True
        if '_save_draft' in self.request.POST:
            form.instance.is_public = False
        form.save()
        # for a file field to accept multiple files we save each file, creating a new OutcomeMedia object
        outcomemedia = flatten_formset_file_fields(outcomemedia_form)
        for media in outcomemedia:
            media.author = self.request.user
            media.is_public = True
            media.save()
        return redirect('outcomes:outcome-list')

    def form_invalid(self, form, outcomemedia_form, context):
        return render(self.request, self.get_template_names(), context)


class OutcomeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    ''' Displays a form to update an existing outcome for the user that is
        the original author of the outcome. Form also contains files that were uploaded
        by the author. The post and any uploaded files are publicly visible unless the
        author saves the outcome as a draft.'''

    model = Outcome
    form_class = OutcomeForm
    template_name_suffix = '_update_form'
    
    def get_queryset(self):
        return Outcome.objects.exclude(Q(is_public=False))

    def test_func(self):
        return self.request.user == self.get_object().author

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        outcomemedia_form = OutcomeMediaFormSet(
            instance=form.instance,
            queryset=OutcomeMedia.objects.filter(author=form.instance.author))
        context = self.get_context_data(form=form, outcomemedia_form=outcomemedia_form)
        return render(request, self.get_template_names(), context) 


    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        outcomemedia_form = OutcomeMediaFormSet(request.POST, request.FILES, instance=form.instance)
        context = self.get_context_data(form=form, outcomemedia_form=outcomemedia_form)
        actual_is_public = form.instance.is_public
        if not all([form.is_valid(), outcomemedia_form.is_valid()]):
            # not using BooleanField widget in form. it's initial value is always False,
            # so is_public becomes False after calling form.is_valid()
            form.instance.is_public = actual_is_public
            return self.form_invalid(form, outcomemedia_form) 
        return self.form_valid(form, outcomemedia_form)

    def form_valid(self, form, outcomemedia_form):
        if '_save_draft' in self.request.POST:
            form.instance.is_public = False
        else:
            form.instance.is_public = True
        form.save()
        update_files_formset(outcomemedia_form)
        if self.request.FILES:
            outcomemedia = flatten_formset_file_fields(outcomemedia_form)
            for media in outcomemedia:
                media.author = self.request.user
                media.is_public = True
                media.save()
        return redirect('outcomes:outcome-list')

    def form_invalid(self, form, outcomemedia_form):
        context = self.get_context_data(form=form, outcomemedia_form=outcomemedia_form)
        return render(self.request, self.get_template_names(), context)


class OutcomeMediaUpdateView(UpdateView):
    ''' Displays user-submitted posts for an outcome. Template hides form to 
        submit a post and certain types of outcomes from unauthenticated users.'''

    template_name = 'outcomes/outcomemedia_update_form.html'
    context_object_name = 'outcome'
    model = Outcome

    def get_queryset(self):
        return Outcome.objects.exclude(Q(is_public=False))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = OutcomeMedia.objects.filter(Q(outcome__pk=self.object.pk), Q(is_public=True))
        if self.request.user.is_authenticated:
            media = queryset
        else:
            media = queryset.filter(~Q(outcome_type=OutcomeMedia.RAW_DATA))
        context['outcomemedia_list'] = media
        types = [t['outcome_type'] for t in media.values('outcome_type')]
        context['OUTCOME_TYPES'] = [t[1] for t in OutcomeMedia.OUTCOME_TYPES if t[0] in types]
        return context
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = OutcomeMediaFormSet()
        context = self.get_context_data(form=form)
        return render(request, self.get_template_names(), context) 

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = OutcomeMediaFormSet(request.POST, request.FILES, instance=self.object)
        context = self.get_context_data(form=form)
        if not form.is_valid():
            return self.form_invalid(form) 
        return self.form_valid(form)

    def form_valid(self, form):
        import pdb; pdb.set_trace()
        outcomemedia = flatten_formset_file_fields(form)
        for media in outcomemedia:
            media.author = self.request.user
            media.save()
        return redirect('outcomes:outcome-list')

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        media = OutcomeMedia.objects.filter(outcome__pk=self.object.pk)
        context['outcomemedia_list'] = media
        types = [t['outcome_type'] for t in media.values('outcome_type')]
        context['OUTCOME_TYPES'] = [t[1] for t in OutcomeMedia.OUTCOME_TYPES if t[0] in types]
        return context
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = OutcomeMediaUpdateFormSet(
                instance=self.object,
                queryset=OutcomeMedia.objects.filter(is_public=False)
        )
        context = self.get_context_data(form=form)
        return render(request, self.get_template_names(), context) 

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = OutcomeMediaUpdateFormSet(request.POST, instance=self.object)
        context = self.get_context_data(form=form)
        if not form.is_valid():
            return self.form_invalid(form) 
        return self.form_valid(form)

    def form_valid(self, form):
        form.save()
        return redirect(self.object.get_absolute_url())

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return render(self.request, self.get_template_names(), context)


class DraftListView(LoginRequiredMixin, OutcomeListView):
    ''' Displays a list of the current user's unpublished drafts.
        The drafts in this list are only available to the currently logged in user. '''

    template_name = 'outcomes/draft_list.html'

    def get_queryset(self):
            return Outcome.objects.filter(Q(is_public=False), Q(author=self.request.user))


class DraftDetailView(LoginRequiredMixin, DetailView):
    ''' Displays details of an outcome. Allows a user to hide their private outcomes from
        other users. Additionally, unauthenticated users may not view certain types of outcomes '''

    template_name = 'outcomes/outcome_detail.html'
    model = Outcome
    context_object_name = 'outcome'

    def get_queryset(self):
        return Outcome.objects.filter(Q(is_public=False), Q(author=self.request.user))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        media = OutcomeMedia.objects.filter(outcome__pk=self.object.pk)
        context['outcomemedia_list'] = media
        types = [t['outcome_type'] for t in media.values('outcome_type')]
        context['OUTCOME_TYPES'] = [t[1] for t in OutcomeMedia.OUTCOME_TYPES if t[0] in types]
        return context


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
        query = self.request.GET.get('query')
        return Outcome.objects.annotate(search=SearchVector('description', 'title')).filter(search=query, is_public=True)


def get_course_sections(request):
    course_id = request.GET.get('course')
    course = Course.objects.get(pk=course_id)
    sections = course.sections
    return render(request, 'outcomes/section_dropdown_list_options.html', {'sections': sections})
