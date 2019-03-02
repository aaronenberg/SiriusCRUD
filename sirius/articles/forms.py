from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit, Field
from django.forms import inlineformset_factory, ModelForm, FileInput
from .models import Article, ArticleMedia


ArticleMediaFormSet = inlineformset_factory(
    Article,
    ArticleMedia,
    fields=('article_media',),
    extra=1,
    widgets={'article_media': FileInput()}
)

class ArticleForm(ModelForm):

    class Meta:
        model = Article
        fields = (
            'article_type',
            'course',
            'description',
            'subject',
            'is_public',
            'title', 
        )

    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Div(
                Field('title', autocomplete="off", wrapper_class='col-md-6'),
                Field('article_type', wrapper_class='col-md-2'),
                Field('subject', wrapper_class='col-md-2'),
                Field('course', autocomplete="off", wrapper_class='col-md-6'),
                css_class='form-row'
            ),
            Div(
                Field('description', autocomplete="off", wrapper_class='col-md-12'),
            )
        )
        self.helper.form_id = 'id-article-form'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_tag = False
        self.helper.form_show_labels = True 
