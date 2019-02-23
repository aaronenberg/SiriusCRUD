from django.views import View
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Article, ArticleMedia
from .forms import ArticleForm, ArticleMediaFormSet


class ArticleListView(ListView):

    model = Article
    context_object_name = 'articles'


class ArticleDetail(DetailView):

    model = Article
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articlemedia_list'] = ArticleMedia.objects.filter(article__pk=self.object.pk)
        return context


class ArticleCreateView(CreateView):

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
        form.save()
        articlemedia = articlemedia_form.save(commit=False)
        for media in articlemedia:
            media.save()
        return redirect('article-list')

    def form_invalid(self, form, articlemedia_form):
        context = self.get_context_data(form=form, articlemedia_form=articlemedia_form)
        return render(request, self.template_name, context)
