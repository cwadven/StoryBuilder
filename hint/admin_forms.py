from django import forms
from django.core.exceptions import ValidationError


class SheetHintInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        sequences = []
        for form in self.forms:
            if form.cleaned_data['is_deleted'] or form.cleaned_data['DELETE']:
                continue
            sequence = form.cleaned_data['sequence']
            if int(sequence) in sequences:
                raise ValidationError('동일한 sequence 를 가진 Sheet Hint 가 있습니다.')
            sequences.append(sequence)
