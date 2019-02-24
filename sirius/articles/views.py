from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, render
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from .models import Article, ArticleMedia
from .forms import ArticleForm, ArticleMediaFormSet


class ArticleListView(ListView):
    ''' Displays all public articles '''

    model = Article
    context_object_name = 'articles'
    queryset = Article.objects.filter(is_public=True)


class ArticleDetail(DetailView):
    ''' Displays a specific, public article and it's uploaded attachments '''

    model = Article
    context_object_name = 'article'
    queryset = Article.objects.filter(is_public=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articlemedia_list'] = ArticleMedia.objects.filter(article__pk=self.object.pk)
        return context


class ArticleCreateView(LoginRequiredMixin, CreateView):
    ''' Displays a form to create a new article and a separate form for uploaded attachments
        only for authenticated users '''

    template_name = 'articles/article_create.html'
    model = Article
    form_class = ArticleForm

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        articlemedia_form = ArticleMediaFormSet()
        context = self.get_context_data(form=form, articlemedia_form=articlemedia_form)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        articlemedia_form = ArticleMediaFormSet(self.request.POST, self.request.FILES, instance=form.instance)
        context = self.get_context_data(form=form, articlemedia_form=articlemedia_form)
        if not all([form.is_valid(), articlemedia_form.is_valid()]):
            return self.form_invalid(form, articlemedia_form) 
        return self.form_valid(form, articlemedia_form)

    def form_valid(self, form, articlemedia_form):
        form.instance.author = self.request.user
        form.save()
        articlemedia = articlemedia_form.save(commit=False)
        for media in articlemedia:
            media.save()
        return redirect('article-list')

    def form_invalid(self, form, articlemedia_form):
        context = self.get_context_data(form=form, articlemedia_form=articlemedia_form)
        return render(self.request, self.template_name, context)


class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    ''' Displays a form to update an existing article only for the original author '''

    template_name = 'articles/article_update_form.html'
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
        return render(request, self.template_name, context) 

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        articlemedia_form = ArticleMediaFormSet(self.request.POST, self.request.FILES, instance=self.object)
        context = self.get_context_data(form=form, articlemedia_form=articlemedia_form)
        if not all([form.is_valid(), articlemedia_form.is_valid()]):
            return self.form_invalid(form, articlemedia_form) 
        return self.form_valid(form, articlemedia_form)

    def form_valid(self, form, articlemedia_form):
        form.save()
        articlemedia = articlemedia_form.save(commit=False)
        for media in articlemedia:
            media.save()
        if 'title' in form.changed_data:
            return redirect(self.object, permanent=True)
        return redirect(self.object)

    def form_invalid(self, form, articlemedia_form):
        context = self.get_context_data(form=form, articlemedia_form=articlemedia_form)
        return render(request, self.template_name, context)
