from django import forms

from banner.models import Banner
from common_library import generate_presigned_url, upload_file_to_presigned_url


class BannerAdminForm(forms.ModelForm):
    background_image_file = forms.ImageField(label='background_image 이미지 업로드', required=False)
    background_image = forms.CharField(label='background_image 이미지 주소', required=False)

    class Meta:
        model = Banner
        fields = '__all__'

    def save(self, commit=True):
        instance = super(BannerAdminForm, self).save(commit=False)
        if self.cleaned_data['background_image_file']:
            response = generate_presigned_url(
                self.cleaned_data['background_image_file'].name,
                _type='banner_background_image',
                unique=str(instance.id) if instance.id else '0'
            )
            upload_file_to_presigned_url(response['url'], response['fields'], self.cleaned_data['background_image_file'].file)
            instance.background_image = response['url'] + response['fields']['key']
        if commit:
            instance.save()
        return instance
