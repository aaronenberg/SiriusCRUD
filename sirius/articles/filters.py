import django_filters
from .models import Article, ArticleMedia

class ArticleFilter(django_filters.FilterSet):
	class Meta:
		model = Article
		
		fields = {
			'course': ['exact',],
			'title': ['icontains',],
		}