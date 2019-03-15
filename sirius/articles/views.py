import re
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.postgres.search import SearchVector
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.urls import NoReverseMatch, reverse
from .models import Article, ArticleMedia
from .forms import ArticleForm, ArticleMediaFormSet
from courses.models import Course


class ArticleListView(ListView):
    ''' Displays a list of articles. Users are able to see all of their own articles, public or private,
        as well as other users' public articles. Additionally, unauthenticated users may not view 
        certain types of articles '''

    model = Article
    context_object_name = 'articles'
    queryset = Article.objects.exclude(is_public=False).order_by('-modified')
    paginate_by = 10


class ArticleDetailView(DetailView):
    ''' Displays details of an article. Allows a user to hide their private articles from
        other users. Additionally, unauthenticated users may not view certain types of articles '''

    model = Article
    context_object_name = 'article'

    def get_queryset(self):
        return Article.objects.exclude(Q(is_public=False))
            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            media = ArticleMedia.objects.filter(article__pk=self.object.pk)
        else:
            media = ArticleMedia.objects.filter(Q(article__pk=self.object.pk), ~Q(article_type='RD'))
        context['articlemedia_list'] = media
        types = [t['article_type'] for t in media.values('article_type')]
        context['ARTICLE_TYPES'] = [t[1] for t in ArticleMedia.ARTICLE_TYPES if t[0] in types]
        return context


def flatten_formset_file_fields(formset):
    media = []
    for i, file_field in enumerate(formset.files.keys()):
        for fp in formset.files.getlist(file_field):
            article_type = formset.forms[i].cleaned_data['article_type']
            article = formset.forms[i].cleaned_data['article']
            import pdb; pdb.set_trace()
            media.append(ArticleMedia(article_media=fp, article_type=article_type, article=article))
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
    else:
        return None


class ArticleCreateView(LoginRequiredMixin, CreateView):
    ''' Displays a form to create a new article and a separate form for uploaded attachments
        only for authenticated users '''

    template_name_suffix = '_create_form'
    model = Article
    form_class = ArticleForm

    def get(self, request, *args, **kwargs):
        self.object = None
        referer_page = self.request.META.get('HTTP_REFERER')
        if referer_page and reverse('courses:course-list') in referer_page:
            import pdb; pdb.set_trace()
            course = get_course_from_url(referer_page)
            self.initial = {'course': course}
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        articlemedia_form = ArticleMediaFormSet()
        context = self.get_context_data(form=form, articlemedia_form=articlemedia_form)
        return render(request, self.get_template_names(), context)

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        articlemedia_form = ArticleMediaFormSet(request.POST, request.FILES, instance=form.instance)
        context = self.get_context_data(form=form, articlemedia_form=articlemedia_form)
        if not all([form.is_valid(), articlemedia_form.is_valid()]):
            return self.form_invalid(form, articlemedia_form, context) 
        return self.form_valid(form, articlemedia_form)

    def form_valid(self, form, articlemedia_form):
        if '_save_draft' in self.request.POST:
            form.instance.is_public = False
        else:
            form.instance.is_public = True
        form.instance.author = self.request.user
        form.save()
        # for a file field to accept multiple files we save each file, creating a new ArticleMedia object
        articlemedia = flatten_formset_file_fields(articlemedia_form)
        for media in articlemedia:
            media.save()
        return redirect('articles:article-list')

    def form_invalid(self, form, articlemedia_form, context):
        return render(self.request, self.get_template_names(), context)


class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    ''' Displays a form to update an existing article only for the original author '''

    template_name_suffix = '_update_form'
    model = Article
    form_class = ArticleForm
    
    def test_func(self):
        return self.request.user == self.get_object().author

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        articlemedia_form = ArticleMediaFormSet()
        context = self.get_context_data(form=form, articlemedia_form=articlemedia_form)
        return render(request, self.get_template_names(), context) 

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        articlemedia_form = ArticleMediaFormSet(request.POST, request.FILES, instance=self.object)
        context = self.get_context_data(form=form, articlemedia_form=articlemedia_form)
        actual_is_public = form.instance.is_public
        if not all([form.is_valid(), articlemedia_form.is_valid()]):
            # not using BooleanField widget in form. it's initial value is always False,
            # so is_public becomes False after calling form.is_valid()
            form.instance.is_public = actual_is_public
            return self.form_invalid(form, articlemedia_form) 
        return self.form_valid(form, articlemedia_form)

    def form_valid(self, form, articlemedia_form):
        if '_save_draft' in self.request.POST:
            form.instance.is_public = False
        else:
            form.instance.is_public = True
        form.save()
        articlemedia = flatten_formset_file_fields(articlemedia_form)
        for media in articlemedia:
            media.save()
        if 'title' in form.changed_data:
            return redirect('articles:article-list', permanent=True)
        return redirect('articles:article-list')

    def form_invalid(self, form, articlemedia_form):
        context = self.get_context_data(form=form, articlemedia_form=articlemedia_form)
        return render(self.request, self.get_template_names(), context)

class SearchPageView(TemplateView):
	# Code that the html file was based on:
	# https://www.w3schools.com/jquery/tryit.asp?filename=tryjquery_filters_table
	# http://api.jquery.com/toggle/ uses the toggle function to hide
	# the matched search keys
	template_name = 'articles/article_search.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['articles'] = Article.objects.exclude(Q(is_public=False)).order_by('-created')
		context['subjects'] = Course.objects.order_by('subject').distinct('subject')
		context['courses'] = Course.objects.all()
		return context

class DraftListView(LoginRequiredMixin, ListView):
    ''' Displays a list of the current user's unpublished drafts.
        The drafts in this list are only available to the currently logged in user. '''

    model = Article
    context_object_name = 'articles'
    template_name = 'articles/draft_list.html'

    def get_queryset(self):
            return Article.objects.filter(Q(is_public=False), Q(author=self.request.user))


class DraftDetailView(LoginRequiredMixin, ArticleDetailView):
    ''' Displays details of an article. Allows a user to hide their private articles from
        other users. Additionally, unauthenticated users may not view certain types of articles '''

    model = Article
    context_object_name = 'article'

    def get_queryset(self):
        return Article.objects.filter(Q(is_public=False), Q(author=self.request.user))
           

class IndexView(ListView):
    model = Article
    context_object_name = 'articles'
    template_name = 'articles/index.html'


class SearchResultsView(ListView):
    model = Article
    context_object_name = 'articles'
    template_name = 'articles/search_results_list.html'

    def get_queryset(self):
        query = self.request.GET.get('query')
        return Article.objects.annotate(search=SearchVector('description', 'title')).filter(search=query, is_public=True)


def get_course_sections(request):
    course_id = request.GET.get('course')
    course = Course.objects.get(pk=course_id)
    sections = course.sections
    return render(request, 'articles/section_dropdown_list_options.html', {'sections': sections})

