from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.forms import inlineformset_factory
from .models import Article, ArticleMedia


ArticleMediaFormSet = inlineformset_factory(Article, ArticleMedia, extra=2, fields=('media',))

RAW_DATA = 'RD'
ANALYZED_DATA = 'AD'
REPORT = 'RE'
POSTER = 'PO'
OTHER = 'OT'
ARTICLE_TYPES = (
    (RAW_DATA, 'Raw Data'),
    (ANALYZED_DATA, 'Analyzed Data'),
    (REPORT, 'Report'),
    (POSTER, 'Poster'),
    (OTHER, 'Other'),
)

CHEMISTRY = 'CY'
BIOLOGY = 'BY'
CIVIL_ENGINEERING = 'CE'
DISCIPLINES = (
    (CHEMISTRY, 'Chemistry'),
    (BIOLOGY, 'Biology'),
    (CIVIL_ENGINEERING, 'Civil Engineering'),
)

class ArticleMediaFormHelper(FormHelper):

    def __init__(self, *args, **kwargs):
        super(ArticleMediaFormHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'

class ArticleForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = (
            'article_type','description', 'discipline',
            'title', 
        )

    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'id-article-form'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_tag = False


class ArticleMediaForm(forms.ModelForm):

    #media = forms.FileField(max_length=32) 
    class Meta:
        model = ArticleMedia
        fields = ('media',)

    def __init__(self, *args, **kwargs):
        super(ArticleMediaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'id-media-form'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_tag = False

