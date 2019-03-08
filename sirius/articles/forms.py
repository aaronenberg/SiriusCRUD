from django.forms import inlineformset_factory, ModelForm, FileInput, ValidationError, ModelChoiceField, ChoiceField, Textarea, FileField, BooleanField, BaseFormSet
from django.forms.widgets import TextInput, Select, NumberInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit, Field, HTML, BaseInput
from .models import Article, ArticleMedia
from courses.models import Course


#class BaseArticleMediaFormSet(BaseFormSet):
#    def clean_article_type(self):
#        for form in self.forms:
#            article_type = form.cleaned_data['article_type']
#            media = form.cleaned_data['article_media']
#            if article_type and not media:
#                raise forms.ValidationError("File type was chosen without uploading a file.")
#        return article_type

ArticleMediaFormSet = inlineformset_factory(
    Article,
    ArticleMedia,
    fields=('article_media', 'article_type'),
    extra=1,
    widgets={'article_media': FileInput(attrs={
                'class': 'custom-file',
            }),
            'article_type': Select(attrs={
                'class': 'form-control select-fix-height'
            })
    }
)

class ArticleForm(ModelForm):

    semester = ChoiceField(choices=Article.SEMESTER_CHOICES,
        widget = Select(attrs={
            'id': 'article_semester',
            'class': 'form-control custom-select select-fix-height',
            'name': 'semester',
        }),
        required=False,
    )
    year = ChoiceField(choices=Article.YEAR_CHOICES,
        widget = Select(attrs={
            'id': 'article_year',
            'class': 'form-control custom-select select-fix-height',
            'name': 'year',
        }),
        required=False,
        initial=Article.current_year
    )
    course = ModelChoiceField(queryset=Course.objects.all(),
        widget = Select(attrs={
            'id': 'article_course',
            'class': 'form-control select-fix-height',
            'name': 'course',
        }),
        required=False,
        empty_label="Select a course"
    )
    class Meta:
        model = Article
        fields = (
            'course',
            'section',
            'description',
            'subject',
            'semester',
            'year',
            'is_public',
            'title', 
        )

    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget = TextInput(attrs={
            'id': 'article_title',
            'class': 'form-control',
            'name': 'title',
        })
        self.fields['section'].widget = TextInput(attrs={
            'id': 'article_course_section',
            'class': 'form-control',
            'name': 'course_section',
        })
        self.fields['description'].widget = Textarea(attrs={
            'id': 'article_description',
            'class': 'form-control',
            'name': 'description',
        })

    def clean(self):
        cleaned_data = super().clean()
        section = cleaned_data.get('section')
        course = cleaned_data.get('course')
        if section:
            if not course:
                raise ValidationError("You must also select a course with section {:02d}.".format(section))
            if section not in course.sections:
                raise ValidationError("Section {0} does not exist for course {1}".format(section, course))

    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year:
            return year
        return None



