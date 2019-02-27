from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .forms import CourseForm
from .models import Course


class CourseListView(LoginRequiredMixin, ListView):
    ''' Displays all public courses, restricting raw data viewing to authenticated users '''

    model = Course
    context_object_name = 'courses'

    def get_queryset(self):
        queryset = Course.objects.filter(is_public=True)
        return queryset


class CourseSubjectListView(LoginRequiredMixin, ListView):
    ''' Displays all public courses, restricting raw data viewing to authenticated users '''

    model = Course
    context_object_name = 'subject_courses'
    template_name = "courses/course_subject_list.html"

    def get_queryset(self):
        queryset = Course.objects.filter(is_public=True)
        queryset = queryset.filter(subject=self.request.course.subject)
        return queryset


#class CourseDetailSectionListView(LoginRequiredMixin, ListView):
#    ''' Displays all public courses, restricting raw data viewing to authenticated users '''
#
#    model = Course
#    context_object_name = 'subject_course_sections'
#    template_name = "courses/section_list.html"
#
#    def get_queryset(self):
#        queryset = Course.objects.filter(is_public=True)
#        queryset = queryset.filter(subject=self.request.course.subject)
#        queryset = queryset.filter(number=self.request.course.number)
#        return queryset


class CourseDetailSectionListView(DetailView):
    ''' Displays a specific, public article and it's uploaded attachments '''

    model = Course
    context_object_name = 'course'
    queryset = Course.objects.filter(is_public=True)

    def get_context_data(self, **kwargs):
        queryset = Course.objects.filter(subject=self.object.subject
                                ).filter(number=self.object.number)
        context = super().get_context_data(**kwargs)
        context['courses'] = queryset
        return context


class CourseCreateView(LoginRequiredMixin, CreateView):
    ''' Displays a form to create a new course only for authenticated users '''

    template_name_suffix = '_create_form'
    model = Course
    form_class = CourseForm

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
        return redirect('course-list')

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return render(self.request, self.get_template_names(), context)
