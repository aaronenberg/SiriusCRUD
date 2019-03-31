import re
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.urls import NoReverseMatch, reverse
from .models import Outcome, OutcomeMedia
from .forms import OutcomeForm, OutcomeMediaFormSet
from courses.models import Course


class OutcomeListView(ListView):
    ''' Displays a list of outcomes. Users are able to see all of their own outcomes, public or private,
        as well as other users' public outcomes. Additionally, unauthenticated users may not view 
        certain types of outcomes '''

    model = Outcome
    context_object_name = 'outcomes'
    queryset = Outcome.objects.exclude(is_public=False).order_by('-modified')


class OutcomeDetailView(DetailView):


    def get_queryset(self):
        return Outcome.objects.exclude(Q(is_public=False))
            


def flatten_formset_file_fields(formset):
    media = []
    for i, file_field in enumerate(formset.files.keys()):
        for fp in formset.files.getlist(file_field):
            outcome_type = formset.forms[i].cleaned_data['outcome_type']
            outcome = formset.forms[i].cleaned_data['outcome']
            media.append(OutcomeMedia(media=fp, outcome_type=outcome_type, outcome=outcome))
    return media


def get_course_from_url(url):
    course_slug_pattern = re.compile('[A-Z]{2,4}\d{1,3}[A-Z]?')
    match = course_slug_pattern.search(url) 
    if match:
        slug = match.group()
        try:
            path = reverse('courses:course-detail', kwargs={'slug': slug})
        except NoReverseMatch:
            return None
        return Course.objects.get(slug=slug)
    else: return None


class OutcomeCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    ''' Displays a form to create a new outcome and a separate form for uploaded attachments
        only for authenticated users '''

    template_name_suffix = '_create_form'
    model = Outcome
    form_class = OutcomeForm

    def test_func(self):
        return self.request.user.user_type != 'ST'

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
            media.save()
        return redirect('outcomes:outcome-list')

    def form_invalid(self, form, outcomemedia_form, context):
        return render(self.request, self.get_template_names(), context)


class OutcomeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    ''' Displays a form to update an existing outcome only for the original author '''

    template_name_suffix = '_update_form'
    model = Outcome
    form_class = OutcomeForm
    
    def get_queryset(self):
        return Outcome.objects.exclude(Q(is_public=False))

    def test_func(self):
        return self.request.user == self.get_object().author

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        outcomemedia_form = OutcomeMediaFormSet()
        context = self.get_context_data(form=form, outcomemedia_form=outcomemedia_form)
        return render(request, self.get_template_names(), context) 

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        outcomemedia_form = OutcomeMediaFormSet(request.POST, request.FILES, instance=self.object)
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
        outcomemedia = flatten_formset_file_fields(outcomemedia_form)
        for media in outcomemedia:
            media.author = self.request.user
            media.save()
        return redirect('outcomes:outcome-list')

    def form_invalid(self, form, outcomemedia_form):
        context = self.get_context_data(form=form, outcomemedia_form=outcomemedia_form)
        return render(self.request, self.get_template_names(), context)


class OutcomeMediaUpdateView(UpdateView):
    ''' Displays details of an outcome. Logged in  to hide their private outcomes from
        other users. Additionally, unauthenticated users may not view certain types of outcomes '''
    ''' Displays a form to update an existing outcome only for the original author '''

    template_name = 'outcomes/outcomemedia_update_form.html'
    context_object_name = 'outcome'
    model = Outcome

    def get_queryset(self):
        return Outcome.objects.exclude(Q(is_public=False))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            media = OutcomeMedia.objects.filter(outcome__pk=self.object.pk)
        else:
            media = OutcomeMedia.objects.filter(Q(outcome__pk=self.object.pk), ~Q(outcome_type='RD'))
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
        outcomemedia = flatten_formset_file_fields(form)
        for media in outcomemedia:
            media.author = self.request.user
            media.save()
        return redirect('outcomes:outcome-list')

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return render(self.request, self.get_template_names(), context)

class SearchPageView(TemplateView):
	# Code that the html file was based on:
	# https://www.w3schools.com/jquery/tryit.asp?filename=tryjquery_filters_table
	# http://api.jquery.com/toggle/ uses the toggle function to hide
	# the matched search keys
	template_name = 'outcomes/outcome_search.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['outcomes'] = Outcome.objects.exclude(Q(is_public=False)).order_by('-created')
		context['subjects'] = Course.objects.order_by('subject').distinct('subject')
		context['courses'] = Course.objects.all()
		return context

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


#class SubmissionDetailView(LoginRequiredMixin, UserPassesTestMixin, OutcomeDetailView):
#    ''' Displays details of an outcome. Allows a user to hide their private outcomes from
#        other users. Additionally, unauthenticated users may not view certain types of outcomes '''
#
#    model = OutcomeMedia
#    context_object_name = 'outcome'
#
#    def test_func(self):
#        outcome = self.get_object()
#        return self.request.user == outcome.author or (self.request.user.user_type != 'ST' and outcome.course in self.request.user.courses)
#
#    def get_queryset(self):
#        return OutcomeMedia.objects.filter(Q(is_public=False), Q(media_outcome=self.get_object()))


#class SubmissionListView(LoginRequiredMixin, UserPassesTestMixin, OutcomeListView):
#    ''' Displays details of an outcome. Allows a user to hide their private outcomes from
#        other users. Additionally, unauthenticated users may not view certain types of outcomes '''
#
#    model = OutcomeMedia
#    template_name = 'outcomes/submission_list.html'
#
#    def test_func(self):
#        return self.request.user.user_type != 'ST'
#
#    def get_queryset(self):
#        return OutcomeMedia.objects.filter(Q(is_public=False))
           

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

