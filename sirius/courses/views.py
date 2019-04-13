from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from .forms import CourseForm
from .models import Course
from users.models import FACULTY


class SubjectListView(LoginRequiredMixin, TemplateView):

    template_name = 'courses/subject_list.html'
        
    def get_context_data(self, **kwargs):
        context = super(SubjectListView, self).get_context_data(**kwargs)
        context['subjects'] = [s for s in Course.SUBJECT_CHOICES if s[0]]
        return context


class SubjectCoursesListView(LoginRequiredMixin, ListView):
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


class CourseDetailView(DetailView):
    ''' Displays a specific course and its related, public outcomes '''

    model = Course
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        queryset = Course.objects.filter(subject=self.object.subject
                                ).filter(number=self.object.number)
        context = super().get_context_data(**kwargs)
        context['courses'] = queryset
        context['outcomes'] = self.object.outcomes.filter(is_public=True)
        context['referer_page'] = self.request.META.get('HTTP_REFERER')
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
        import pdb; pdb.set_trace()
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
        import pdb; pdb.set_trace()
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
