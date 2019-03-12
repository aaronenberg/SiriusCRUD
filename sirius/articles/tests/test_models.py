from django.contrib.auth import authenticate, login
from django.test import TestCase
from articles.models import Article, ArticleMedia
from users.models import BaseUser 


class ArticleTestCase(TestCase):

    def setUp(self):
        self.test_user = BaseUser.objects.create_user(username='testuser', email="testuser@csus.edu", password='12345')

    def test_can_create_article(self):
        article = Article.objects.create(title="title", author=self.test_user)
        self.assertIsInstance(Article.objects.get(pk=article.pk), Article)

    def test_can_update_article_title(self):
        article = Article.objects.create(title="title", author=self.test_user)
        new_title = "new title"
        article.title = new_title
        article.save()
        self.assertEqual(Article.objects.get(pk=article.pk).title, new_title)

    def test_slug_generated_from_article_title_is_unique(self):
        title = "slug test"
        article_1 = Article.objects.create(title=title, author=self.test_user)
        article_2 = Article.objects.create(title=title, author=self.test_user)
        article_1_slug = Article.objects.get(pk=article_1.pk).slug
        article_2_slug = Article.objects.get(pk=article_2.pk).slug
        self.assertNotEqual(article_1_slug, article_2_slug)

    def test_slug_generation_truncates_very_long_article(self):
        title = "veeeeeeeeeeeeeeeeeeeeeeeeerrrrrrrrrrrrrrrrrrrrrryyyyyyyyyyyyyyyyyyyyyyyy \
                loooooooooooooooooooooooooooooooooooooooooonnnnnnnnnnngggggggggggggggggg \
                aaaaarrrttttiiiiicccclllleeeeee tiiiiiiiitttttlllllllllleeeeeeeeeee"
        article = Article.objects.create(title=title, author=self.test_user)
        article_slug = Article.objects.get(pk=article.pk).slug
        self.assertGreater(len(title), Article._meta.get_field('slug').max_length)
        self.assertLessEqual(len(article_slug), Article._meta.get_field('slug').max_length)
