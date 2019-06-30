from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.db.models.fields import BLANK_CHOICE_DASH
from django.forms import (
    inlineformset_factory,
    ModelForm,
    FileInput,
    ValidationError,
    ModelChoiceField,
    ChoiceField,
    Textarea,
    FileField,
    BooleanField,
    BaseInlineFormSet,
    NumberInput,
    TextInput,
    Select,
    ClearableFileInput
)
from django.utils.text import get_valid_filename
from storages.backends.s3boto3 import S3Boto3StorageFile

from .models import Development, DevelopmentMedia
from .utils import current_year, filename


YEAR_CHOICES = [] + BLANK_CHOICE_DASH
for y in reversed(range(2000, (current_year()+1))):
        YEAR_CHOICES.append((y,y))


class DevelopmentForm(ModelForm):

    semester = ChoiceField(choices=Development.SEMESTER_CHOICES,
        widget = Select(attrs={
            'id': 'development_semester',
            'class': 'form-control custom-select select-fix-height',
            'name': 'semester',
        }),
        required=False,
    )
    year = ChoiceField(choices=YEAR_CHOICES,
        widget = Select(attrs={
            'id': 'development_year',
            'class': 'form-control custom-select select-fix-height',
            'name': 'year',
        }),
        required=False,
        initial=current_year
    )
    class Meta:
        model = Development
        fields = (
            'description',
            'semester',
            'year',
            'is_public',
            'title', 
        )

    def __init__(self, *args, **kwargs):
        super(DevelopmentForm, self).__init__(*args, **kwargs)
 
        self.fields['title'].widget = TextInput(attrs={
            'id': 'development_title',
            'class': 'form-control',
            'name': 'title',
            'maxlength': '99',
        })
        self.fields['description'].widget = Textarea(attrs={
            'id': 'development_description',
            'class': 'form-control',
            'name': 'description',
            'maxlength': '2000',
        })

    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year:
            return year
        return None


class MediaClearableFileInput(ClearableFileInput):
    initial_text = ''
    input_text = ''
    template_name = 'partials/clearable_file_input.html'
    filename = ''

    def filename(self, value):
        if value is not None:
            return value.name.split('/')[-1]
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget'].update({
            'filename': self.filename(value),
        })
        return context


class BaseDevelopmentMediaFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            development_type = form.cleaned_data.get('development_type')
            media = form.cleaned_data.get('media')
            if media and not development_type:
                raise ValidationError("Please select a file type for file: {}.".format(filename(media)))
            if isinstance(media, (UploadedFile, S3Boto3StorageFile)) \
                and default_storage.exists(
                    'uploads/' + self.instance.slug + '/' + get_valid_filename(form.cleaned_data.get('media').name)):
                form.cleaned_data['DELETE'] = True


DevelopmentMediaFormSet = inlineformset_factory(
    Development, DevelopmentMedia,
    formset=BaseDevelopmentMediaFormSet,
    fields=('media', 'development_type'),
    extra=1,
    validate_max=True,
    widgets={
        'media': MediaClearableFileInput(attrs={'multiple': True}),
        'development_type': Select(attrs={'class': 'form-control select-fix-height'}),
    }
)


DevelopmentMediaDirectoryFormSet = inlineformset_factory(
    Development, DevelopmentMedia,
    formset=BaseDevelopmentMediaFormSet,
    fields=('media', 'development_type'),
    extra=1,
    validate_max=True,
    widgets={
        'media': MediaClearableFileInput(attrs={'webkitdirectory': True, 'mozdirectory': True}),
        'development_type': Select(attrs={'class': 'form-control select-fix-height'})
    }
)

