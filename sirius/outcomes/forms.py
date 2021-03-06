from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.db.models.fields import BLANK_CHOICE_DASH
from django.forms import (
    BaseInlineFormSet,
    BooleanField,
    ChoiceField,
    CheckboxInput,
    ClearableFileInput,
    FileInput,
    inlineformset_factory,
    ModelChoiceField,
    ModelForm,
    Textarea,
    ValidationError,
    TextInput,
    NumberInput,
    Select,
)
from django.utils.text import get_valid_filename
from storages.backends.s3boto3 import S3Boto3StorageFile

from .models import Outcome, OutcomeMedia
from courses.models import Course
from .utils import current_year, filename


YEAR_CHOICES = [] + BLANK_CHOICE_DASH
for y in reversed(range(2000, (current_year()+1))):
        YEAR_CHOICES.append((y,y))


class OutcomeForm(ModelForm):

    semester = ChoiceField(choices=Outcome.SEMESTER_CHOICES,
        widget = Select(attrs={
            'id': 'outcome_semester',
            'class': 'form-control custom-select select-fix-height',
            'name': 'semester',
        }),
        required=False,
    )
    year = ChoiceField(choices=YEAR_CHOICES,
        widget = Select(attrs={
            'id': 'outcome_year',
            'class': 'form-control custom-select select-fix-height',
            'name': 'year',
        }),
        required=False,
    )
    section = ChoiceField(
        widget = Select(attrs={
            'id': 'outcome_course_section',
            'class': 'form-control custom-select select-fix-height',
            'name': 'section',
        }),
        required=False,
    )
    course = ModelChoiceField(queryset=None,
        widget = Select(attrs={
            'id': 'outcome_course',
            'class': 'form-control select-fix-height',
            'name': 'course',
        }),
        required=False,
        empty_label="Select a course"
    )

    class Meta:
        model = Outcome
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
        user = kwargs.pop('user')
        super(OutcomeForm, self).__init__(*args, **kwargs)
 
        if user.is_superuser:
            self.fields['course'].queryset = Course.objects.extra(
                select={'course_number': "CAST(substring(number FROM '^[0-9]+') AS INTEGER)"}
                ).order_by('subject','course_number')
        else:
            self.fields['course'].queryset = user.staffprofile.courses.all()

        self.fields['title'].widget = TextInput(attrs={
            'id': 'outcome_title',
            'class': 'form-control',
            'name': 'title',
            'maxlength': '99',
        })
        self.fields['description'].widget = Textarea(attrs={
            'id': 'outcome_description',
            'class': 'form-control',
            'name': 'description',
            'maxlength': '2000',
        })

        section_choices = []
        course_id = None
        if 'course' in self.initial:
            course_id = self.initial.get('course')
        elif 'course' in self.data and self.data['course']:
            course_id = self.data.get('course')
        elif self.instance.pk and self.instance.course:
            course_id = self.instance.course.pk

        if course_id != None:
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


class BaseOutcomeMediaFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            outcome_type = form.cleaned_data.get('outcome_type')
            media = form.cleaned_data.get('media')
            if media and not outcome_type:
                raise ValidationError("Please select a file type for file: {}.".format(filename(media)))


class BaseOutcomeSubmissionsUpdateFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(BaseOutcomeSubmissionsUpdateFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.fields['outcome_type'].choices = OutcomeMedia.UNPRIVILEGED_OUTCOME_TYPES


class BaseOutcomeMediaUpdateFormSet(BaseOutcomeMediaFormSet):
    def __init__(self, *args, **kwargs):
        super(BaseOutcomeMediaUpdateFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.fields['outcome_type'].choices = OutcomeMedia.UNPRIVILEGED_OUTCOME_TYPES


OutcomeMediaFormSet = inlineformset_factory(
    Outcome, OutcomeMedia,
    formset=BaseOutcomeMediaFormSet,
    fields=('media', 'outcome_type'),
    extra=1,
    validate_max=True,
    
    widgets={
        'media': MediaClearableFileInput(attrs={'multiple': True}),
        'outcome_type': Select(attrs={'class': 'form-control select-fix-height'}),
    }
)

OutcomeMediaDirectoryFormSet = inlineformset_factory(
    Outcome, OutcomeMedia,
    formset=BaseOutcomeMediaFormSet,
    fields=('media', 'outcome_type'),
    extra=1,
    validate_max=True,
    widgets={
        'media': MediaClearableFileInput(attrs={'webkitdirectory': True, 'mozdirectory': True}),
        'outcome_type': Select(attrs={'class': 'form-control select-fix-height'})
    }
)

OutcomeMediaUpdateFormSet = inlineformset_factory(
    Outcome, OutcomeMedia,
    formset=BaseOutcomeMediaUpdateFormSet,
    fields=('media', 'outcome_type'),
    extra=1,
    max_num=5,
    validate_max=True,
    widgets={
        'media': ClearableFileInput(attrs={'required': 'true'}),
        'outcome_type': Select(attrs={'class': 'form-control select-fix-height', 'required': 'true'})
    }
)

OutcomeSubmissionsUpdateFormSet = inlineformset_factory(
    Outcome, OutcomeMedia,
    formset=BaseOutcomeSubmissionsUpdateFormSet,
    exclude=('media', 'author', 'year', 'section',),
    extra=0,
    validate_max=True,
    widgets={'outcome_type': Select(attrs={'class': 'form-control select-fix-height'})}
)


