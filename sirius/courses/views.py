import os.path
import operator
from collections import namedtuple
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from .forms import CourseForm
from .models import Course
from outcomes.models import Outcome, OutcomeMedia
from users.models import FACULTY


class SubjectListView(TemplateView):

    template_name = 'courses/subject_list.html'
        
    def get_context_data(self, **kwargs):
        context = super(SubjectListView, self).get_context_data(**kwargs)
        context['subjects'] = [s for s in Course.SUBJECT_CHOICES if s[0]]
        context['courses'] = Course.objects.extra(
            select={'course_number': "CAST(substring(number FROM '^[0-9]+') AS INTEGER)"}
            ).order_by('subject','course_number').filter(subject='BIO')
        return context


class SubjectCoursesListView(ListView):
    ''' Displays all course subjects'''

    model = Course
    context_object_name = 'courses'

    def get_context_data(self, **kwargs):
        context = super(SubjectCoursesListView, self).get_context_data(**kwargs)
        context['subjects'] = [s for s in Course.SUBJECT_CHOICES if s[0]]
        return context

    def get_queryset(self):
        subject_from_path = self.request.path.split('/')[2]
        # cast course number, avoiding any possible letter, to an integer
        queryset = Course.objects.extra(
            select={'course_number': "CAST(substring(number FROM '^[0-9]+') AS INTEGER)"}
            ).order_by('subject','course_number').filter(subject=subject_from_path)
        return queryset


def get_subdirs_and_media(media, cwd):
    '''get the contents of the 'cwd' which may include files and/or subdirectories'''
    subdirs = {}
    media_in_cwd = set()
    for m in media:
        if not os.path.dirname(str(m)).startswith(cwd.rstrip('/')):
            continue
        try:
            dir_name = os.path.dirname(str(m)).split(cwd, 1)[1].split('/', 1)[0]
            subdirs[dir_name] = os.path.join(cwd, dir_name)
        except IndexError:
            media_in_cwd.add(m.pk)
    media = media.filter(pk__in=media_in_cwd)
    return subdirs, media


Outcome_Media = namedtuple('Outcome_Media', [
    'outcome', 
    'raw_data', 
    'raw_data_subdirs',
    'analyzed_data',
    'analyzed_data_subdirs',
    'curriculum',
    'curriculum_subdirs',
    'year_choices',
    'semester_choices'
])


def get_outcome_media(request):
    outcome_id = request.GET.get('outcome_id')
    section = request.GET.get('section')
    year = request.GET.get('year')
    semester = request.GET.get('semester')

    if outcome_id is None:
        raise ValueError("Need primary key of an Outcome to get OutcomeMedia")
    outcome = Outcome.objects.get(pk=outcome_id)

    cwd = request.GET.get('cwd', outcome.slug) + '/'

    raw_data = outcome.media.filter(outcome_type='RD', is_public=True)
    raw_data_subdirs, raw_data = get_subdirs_and_media(raw_data, cwd)

    analyzed_data = outcome.media.filter(outcome_type='AD', is_public=True)
    analyzed_data_subdirs, analyzed_data = get_subdirs_and_media(analyzed_data, cwd)

    curriculum = outcome.media.filter(outcome_type='CU', is_public=True)
    curriculum_subdirs, curriculum = get_subdirs_and_media(curriculum, cwd)

    year_choices = outcome.media.all().distinct('year').exclude(year__isnull=True).values_list('year', flat=True)
    semester_choices = outcome.media.all().distinct('semester').exclude(semester__isnull=True).values_list('semester', flat=True)

    if section is not None:
        raw_data = raw_data.filter(section=section)
        analyzed_data = analyzed_data.filter(section=section)
        curriculum = curriculum.filter(Q(section=None) | Q(section=section))

    if year is not None:
        raw_data = raw_data.filter(year=year)
        analyzed_data = analyzed_data.filter(year=year)
        curriculum = curriculum.filter(Q(year=None) | Q(year=year))

    if semester is not None:
        raw_data = raw_data.filter(semester=semester)
        analyzed_data = analyzed_data.filter(semester=semester)
        curriculum = curriculum.filter(Q(semester=None) | Q(semester=semester))

    outcome_media = Outcome_Media(
            outcome, 
            raw_data, 
            raw_data_subdirs,
            analyzed_data,
            analyzed_data_subdirs,
            curriculum,
            curriculum_subdirs,
            year_choices,
            semester_choices
    )
    return render(request, 'partials/outcome_media.html', {'outcome_media': outcome_media})


class CourseDetailView(DetailView):
    ''' Displays a specific course and its related, public outcomes '''

    model = Course
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course_outcomes'] = self.object.outcomes.filter(is_public=True).order_by("-modified")
        if len(context['course_outcomes']) == 0:
            context['latest_outcome'] = None
            return context
        latest_outcome = context['course_outcomes'][0]
        cwd = latest_outcome.slug + '/'

        raw_data = latest_outcome.media.filter(outcome_type='RD', is_public=True)
        raw_data_subdirs, raw_data = get_subdirs_and_media(raw_data, cwd)

        analyzed_data = latest_outcome.media.filter(outcome_type='AD', is_public=True)
        analyzed_data_subdirs, analyzed_data = get_subdirs_and_media(analyzed_data, cwd)

        curriculum = latest_outcome.media.filter(outcome_type='CU', is_public=True)
        curriculum_subdirs, curriculum = get_subdirs_and_media(curriculum, cwd)

        year_choices = latest_outcome.media.all().distinct('year').exclude(year__isnull=True).values_list('year', flat=True)
        semester_choices = latest_outcome.media.all().distinct('semester').exclude(semester__isnull=True).values_list('semester', flat=True)

        context['latest_outcome'] = Outcome_Media(
            latest_outcome, 
            raw_data, 
            raw_data_subdirs,
            analyzed_data,
            analyzed_data_subdirs,
            curriculum,
            curriculum_subdirs,
            year_choices,
            semester_choices
        )
        return context


class CourseCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    ''' Displays a form to create a new course only for faculty users '''

    template_name_suffix = '_create_form'
    model = Course
    form_class = CourseForm

    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = self.get_context_data(form=form)
        return render(request, self.get_template_names(), context)

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = self.get_context_data(form=form)
        if not form.is_valid():
            return self.form_invalid(form) 
        return self.form_valid(form)

    def form_valid(self, form):
        form.save()
        return redirect('courses:subject-list')

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return render(self.request, self.get_template_names(), context)


class CourseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    ''' Displays a form to update an existing course only for faculty users '''

    template_name_suffix = '_update_form'
    model = Course
    form_class = CourseForm
    
    def test_func(self):
        return self.request.user.user_role == FACULTY

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
        context = self.get_context_data(form=form)
        if not form.is_valid():
            return self.form_invalid(form) 
        return self.form_valid(form)

    def form_valid(self, form):
        form.save()
        return redirect(self.object)

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return render(self.request, self.get_template_names(), context)


class CourseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):

    model = Course

    def test_func(self):
        return self.request.user.is_superuser

    def get_success_url(self):
        return reverse('courses:subject-courses-list', kwargs={'subject':self.object.subject})
