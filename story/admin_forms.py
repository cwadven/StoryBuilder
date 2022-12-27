from django import forms

from common_library import generate_presigned_url, upload_file_to_presigned_url
from story.models import Story


class StoryAdminForm(forms.ModelForm):
    image_file = forms.ImageField(label='이미지 업로드', required=False)
    image = forms.CharField(label='이미지 주소', required=False)

    class Meta:
        model = Story
        fields = '__all__'

    def save(self, commit=True):
        instance = super(StoryAdminForm, self).save(commit=False)
        if self.cleaned_data['image_file']:
            response = generate_presigned_url(
                self.cleaned_data['image_file'].name,
                _type='topicitem',
                unique=str(instance.id) if instance.id else '0'
            )
            upload_file_to_presigned_url(response['url'], response['fields'], self.cleaned_data['image_file'].file)
            instance.image = response['url'] + response['fields']['key']
        if commit:
            instance.save()
        return instance
