from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from .models import Article, ArticleMedia
from .forms import ArticleForm, ArticleMediaFormSet
from django.views.generic.base import TemplateView
from courses.models import Course


class ArticleListView(ListView):
    ''' Displays a list of articles. Users are able to see all of their own articles, public or private,
        as well as other users' public articles. Additionally, unauthenticated users may not view 
        certain types of articles '''

    model = Article
    context_object_name = 'articles'
    queryset = Article.objects.exclude(is_public=False)


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
        return context


class ArticleCreateView(LoginRequiredMixin, CreateView):
    ''' Displays a form to create a new article and a separate form for uploaded attachments
        only for authenticated users '''

    template_name_suffix = '_create_form'
    model = Article
    form_class = ArticleForm

    def get(self, request, *args, **kwargs):
        self.object = None
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
        articlemedia = articlemedia_form.save(commit=False)
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
        articlemedia = articlemedia_form.save(commit=False)
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
		context['subjects'] = Article.objects.order_by('subject').distinct('subject')
		context['courses'] = Course.objects.all()
		return context

class DraftListView(LoginRequiredMixin, ListView):
    ''' Displays a list of the current user's unpublished drafts.
        The drafts in this list are only available to the currently logged in user. '''

    model = Article
    context_object_name = 'drafts'
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
           
