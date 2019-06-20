import re
from django.forms import (
    inlineformset_factory,
    ModelForm,
    ValidationError,
    ChoiceField, 
    Select, 
    NumberInput,
    TextInput,
    Textarea,
)
from django.contrib.postgres.forms import SimpleArrayField
from django.contrib.postgres.utils import prefix_validation_error
from .models import Course


class SimpleRangeArrayField(SimpleArrayField):
    ''' Extends SimpleArrayField to accept range of numbers as input. e.g. '1-20'
        produces the numbers 1 through 20. '''

    def expand_range(self, item):
        nums = []
        val1, val2 = int(item.split('-')[0]), int(item.split('-')[1])
        low, high = min(val1, val2), max(val1, val2)
        for m in range(low, high + 1):
            nums.append(m)
        return nums

    def to_python(self, value):
        if isinstance(value, list):
            items = value
        elif value:
            items = value.split(self.delimiter)
        else:
            items = []
        errors = []
        values = []

        range_pattern = re.compile('^(\d+)-(\d+)$')
        range_items = []
        for index, item in enumerate(items):
            is_range = range_pattern.match(item.strip())
            if is_range:
                range_items += self.expand_range(item.strip())
                # removing item decreases index used in errors, 
                # so we pop an item off range_items in its place
                items.remove(item)
                items.insert(index, range_items.pop())
                
        # extend items so the index into the original input is not disturbed.
        items.extend(range_items)

        for index, item in enumerate(items):
            try:
                values.append(self.base_field.to_python(item))
            except ValidationError as error:
                errors.append(prefix_validation_error(
                    error,
                    prefix=self.error_messages['item_invalid'],
                    code='item_invalid',
                    params={'nth': index + 1},
                ))
        if errors:
            raise ValidationError(errors)
        return values
    
    def clean(self, value):
        value = super().clean(value)
        return sorted([self.base_field.clean(val) for val in set(value)])


class CourseForm(ModelForm):

    subject = ChoiceField(choices=Course.SUBJECT_CHOICES,
        widget = Select(attrs={
            'id': 'course_subject',
            'class': 'form-control custom-select select-fix-height',
            'name': 'subject',
        }),
    )
    class Meta:
        model = Course
        fields = (
            'title',
            'subject',
            'number',
            'sections',
            'description'
        )
        field_classes = {'sections': SimpleRangeArrayField}

    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)

        self.fields['title'].widget = TextInput(attrs={
            'id': 'course_title',
            'class': 'form-control',
            'name': 'title',
            'maxlength': '99',
        })
        self.fields['number'].widget = TextInput(attrs={
            'id': 'course_number',
            'class': 'form-control',
            'name': 'number',
        })
        self.fields['sections'].widget = TextInput(attrs={
            'id': 'course_sections',
            'class': 'form-control',
            'name': 'sections',
            'data-container': "body",
            'data-toggle': "popover",
            'data-placement': "bottom",
            'data-content': "Separate sections with a comma. To specify a steady range of numbers use a dash. Ex: 1, 2, 12-15",
        })
        self.fields['description'].widget = Textarea(attrs={
            'id': 'outcome_description',
            'class': 'form-control',
            'name': 'description',
            'maxlength': '2000',
        })

    def clean_number(self):
        number = self.cleaned_data.get('number').upper()
        number_pattern = re.compile('^\d{1,3}[A-Z]?$')
        if not number_pattern.match(number):
            raise ValidationError("Course number format invalid: Course number must have atleast 1 number optionally followed by a letter.")
        return number

