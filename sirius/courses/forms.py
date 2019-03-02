import re
from django.forms import inlineformset_factory, ModelForm, ValidationError
from django.contrib.postgres.forms import SimpleArrayField
from django.contrib.postgres.utils import prefix_validation_error
from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Div, Layout, Submit, Field
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

    class Meta:
        model = Course
        fields = ('__all__')
        field_classes = {'sections': SimpleRangeArrayField}

    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Div(
                Field('title', autocomplete="off", wrapper_class='col-md-6'),
                Field('number', wrapper_class='col-md-2'),
                Field('sections', wrapper_class='col-md-2'),
                Field('subject', wrapper_class='col-md-2'),
                Field('is_public', title="Make this course viewable to everyone.", wrapper_class='col-md-2'),
                css_class='form-row'
            ),
            Div(
                Field('description', autocomplete="off", wrapper_class='col-md-12'),
            ),
            ButtonHolder(
                Submit('submit', 'Save', css_class='button white')
            )
        )
        self.helper.form_id = 'id-article-form'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_tag = True
        self.helper.form_show_labels = True

        self.helper.add_input
