from django import forms

from common_library import generate_presigned_url, upload_file_to_presigned_url
from story.models import Story, Sheet


class StoryAdminForm(forms.ModelForm):
    image_file = forms.ImageField(label='대표 이미지 업로드', required=False)
    image = forms.CharField(label='대표 이미지 주소', required=False)
    background_image_file = forms.ImageField(label='대표 배경 이미지 업로드', required=False)
    background_image = forms.CharField(label='대표 배경 이미지 주소', required=False)

    class Meta:
        model = Story
        fields = '__all__'

    def save(self, commit=True):
        instance = super(StoryAdminForm, self).save(commit=False)
        if self.cleaned_data['image_file']:
            response = generate_presigned_url(
                self.cleaned_data['image_file'].name,
                _type='story_image',
                unique=str(instance.id) if instance.id else '0'
            )
            upload_file_to_presigned_url(response['url'], response['fields'], self.cleaned_data['image_file'].file)
            instance.image = response['url'] + response['fields']['key']

        if self.cleaned_data['background_image_file']:
            response = generate_presigned_url(
                self.cleaned_data['background_image_file'].name,
                _type='story_background_image',
                unique=str(instance.id) if instance.id else '0'
            )
            upload_file_to_presigned_url(response['url'], response['fields'], self.cleaned_data['background_image_file'].file)
            instance.background_image = response['url'] + response['fields']['key']
        if commit:
            instance.save()
        return instance


class SheetAdminForm(forms.ModelForm):
    image_file = forms.ImageField(label='대표 이미지 업로드', required=False)
    image = forms.CharField(label='대표 이미지 주소', required=False)
    background_image_file = forms.ImageField(label='대표 배경 이미지 업로드', required=False)
    background_image = forms.CharField(label='대표 배경 이미지 주소', required=False)

    class Meta:
        model = Sheet
        fields = '__all__'

    def save(self, commit=True):
        instance = super(SheetAdminForm, self).save(commit=False)
        if self.cleaned_data['image_file']:
            response = generate_presigned_url(
                self.cleaned_data['image_file'].name,
                _type='sheet_image',
                unique=str(instance.id) if instance.id else '0'
            )
            upload_file_to_presigned_url(response['url'], response['fields'], self.cleaned_data['image_file'].file)
            instance.image = response['url'] + response['fields']['key']

        if self.cleaned_data['background_image_file']:
            response = generate_presigned_url(
                self.cleaned_data['background_image_file'].name,
                _type='sheet_background_image',
                unique=str(instance.id) if instance.id else '0'
            )
            upload_file_to_presigned_url(response['url'], response['fields'], self.cleaned_data['background_image_file'].file)
            instance.background_image = response['url'] + response['fields']['key']
        if commit:
            instance.save()
        return instance
