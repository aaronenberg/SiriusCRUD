from django.db.models.fields import BLANK_CHOICE_DASH
from django.forms import inlineformset_factory, ModelForm, FileInput, ValidationError, ModelChoiceField, ChoiceField, Textarea, FileField, BooleanField, BaseInlineFormSet
from django.forms.widgets import TextInput, Select, NumberInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit, Field, HTML, BaseInput
from .models import Article, ArticleMedia
from courses.models import Course


class BaseArticleMediaFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            article_type = form.cleaned_data.get('article_type')
            media = form.cleaned_data.get('article_media')
            if article_type and not media:
                raise ValidationError("File type was chosen without uploading a file.")
            if media and not article_type:
                raise ValidationError("No file type selected for the chosen file(s). Please reupload the file(s) and select a file type.")


ArticleMediaFormSet = inlineformset_factory(
    Article,
    ArticleMedia,
    formset=BaseArticleMediaFormSet,
    fields=('article_media', 'article_type'),
    extra=1,
    widgets={'article_media': FileInput(attrs={
                'class': 'custom-file',
                'multiple': True
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
    section = ChoiceField(
        widget = Select(attrs={
            'id': 'article_course_section',
            'class': 'form-control custom-select select-fix-height',
            'name': 'section',
        }),
        required=False,
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
        self.fields['description'].widget = Textarea(attrs={
            'id': 'article_description',
            'class': 'form-control',
            'name': 'description',
        })

        section_choices = []
        course_id = None
        if 'course' in self.initial:
            course_id = self.initial.get('course')
        elif 'course' in self.data and self.data['course']:
            course_id = self.data.get('course')
        elif self.instance.pk and self.instance.course:
            course_id = self.instance.course.pk

        if course_id:
            course = Course.objects.get(pk=course_id)
            section_choices += BLANK_CHOICE_DASH
            for section in course.sections:
                section_choices.append((section, "{:02d}".format(section)))
            self.fields['section'].choices = section_choices
        else:
            self.fields['section'].disabled = True


    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year:
            return year
        return None

    def clean_section(self):
        section = self.cleaned_data.get('section')
        if section:
            return section
        return None
