from django.db.models.fields import BLANK_CHOICE_DASH
from django.forms import inlineformset_factory, ModelForm, FileInput, ValidationError, ModelChoiceField, ChoiceField, Textarea, FileField, BooleanField, BaseInlineFormSet
from django.forms.widgets import TextInput, Select, NumberInput
from .models import Development, DevelopmentMedia, SEMESTER_CHOICES 
from .utils import current_year, filename


class BaseDevelopmentMediaFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            development_type = form.cleaned_data.get('development_type')
            media = form.cleaned_data.get('media')
            if development_type and not media:
                raise ValidationError("File type was chosen without uploading a file.")
            if media and not development_type:
                raise ValidationError("Please select a file type for file: {}.".format(filename(media)))


DevelopmentMediaFormSet = inlineformset_factory(
    Development,
    DevelopmentMedia,
    formset=BaseDevelopmentMediaFormSet,
    fields=('media', 'development_type'),
    extra=1,
    widgets={'media': FileInput(attrs={
                'class': 'custom-file',
                'multiple': True
            }),
            'development_type': Select(attrs={
                'class': 'form-control select-fix-height'
            })
    }
)

'''
DevelopmentMediaUpdateFormSet = inlineformset_factory(
    Development,
    DevelopmentMedia,
    formset=BaseInlineFormSet,
    exclude = ('media', 'author'),
    extra=0,
    widgets={'development_type': Select(attrs={
                'class': 'form-control select-fix-height'
            })
    }
)
'''

YEAR_CHOICES = [] + BLANK_CHOICE_DASH
for y in reversed(range(2000, (current_year()+1))):
        YEAR_CHOICES.append((y,y))

class DevelopmentForm(ModelForm):

    semester = ChoiceField(choices=SEMESTER_CHOICES,
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
