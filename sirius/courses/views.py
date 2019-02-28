from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView
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


#class SubjectCourseListView(LoginRequiredMixin, ListView):
#    ''' Displays all public courses, restricting raw data viewing to authenticated users '''
#
#    model = Course
#    context_object_name = 'subject_courses'
#    template_name = "courses/course_subject_list.html"
#
#    def get_queryset(self):
#        self.subject = self.kwargs['subject']
#        queryset = Course.objects.filter(subject=self.subject)
#        return queryset
#    
#    def get_context_data(self, **kwargs):
#        context = super().get_context_data(**kwargs)
#        context['subject'] = self.subject
#        return context


class CourseDetailView(DetailView):
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


class CourseCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    ''' Displays a form to create a new course only for faculty users '''

    template_name_suffix = '_create_form'
    model = Course
    form_class = CourseForm

    def test_func(self):
        return self.request.user.account_type == 'FA'

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



class CourseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    ''' Displays a form to update an existing course only for faculty users '''

    template_name_suffix = '_update_form'
    model = Course
    form_class = CourseForm
    
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
        context = self.get_context_data(form=form)
        if not form.is_valid():
            return self.form_invalid(form) 
        return self.form_valid(form)

    def form_valid(self, form):
        form.save()
        if 'number' or 'subject' in form.changed_data:
            return redirect(self.object, permanent=True)
        return redirect(self.object)

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return render(request, self.get_template_names(), context)

