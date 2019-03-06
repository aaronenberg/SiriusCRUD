from django.forms import inlineformset_factory, ModelForm, FileInput, ValidationError, ModelChoiceField, ChoiceField, Textarea, FileField
from django.forms.widgets import TextInput, Select, NumberInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit, Field, HTML, BaseInput
from .models import Article, ArticleMedia
from courses.models import Course



ArticleMediaFormSet = inlineformset_factory(
    Article,
    ArticleMedia,
    fields=('article_media', 'article_type'),
    extra=1,
    widgets={'article_media': FileInput(attrs={
                'class': 'custom-file'
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
            'name': 'course_description',
        })

    def clean_section(self):
        section = self.cleaned_data.get('section')
        if not section:
            return
        course = self.cleaned_data.get('course')
        if section and not course:
            raise ValidationError("You must also select a course with section {:02d}.".format(section))
        course_obj = Course.objects.get(pk=course.pk)
        if section not in course_obj.sections:
           raise ValidationError("That section does not exist for this course")
        return section


