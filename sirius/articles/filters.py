import django_filters
from .models import Article, ArticleMedia

class ArticleFilter(django_filters.FilterSet):
	title = django_filters.CharFilter(lookup_expr='icontains')
	class Meta:
		model = Article
		fields = ['title', 'course',]