from django import forms
from django.core.exceptions import ValidationError

from hint.models import SheetHint

from common_library import generate_presigned_url, upload_file_to_presigned_url


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


class SheetHintAdminForm(forms.ModelForm):
    image_file = forms.ImageField(label='이미지 업로드', required=False)
    image = forms.CharField(label='이미지 주소', required=False)

    class Meta:
        model = SheetHint
        fields = '__all__'

    def save(self, commit=True):
        instance = super(SheetHintAdminForm, self).save(commit=False)
        if self.cleaned_data['image_file']:
            response = generate_presigned_url(
                self.cleaned_data['image_file'].name,
                _type='sheet_hint_image',
                unique=str(instance.id) if instance.id else '0'
            )
            upload_file_to_presigned_url(response['url'], response['fields'], self.cleaned_data['image_file'].file)
            instance.image = response['url'] + response['fields']['key']
        if commit:
            instance.save()
        return instance
