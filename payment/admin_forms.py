from django import forms

from common_library import generate_presigned_url, upload_file_to_presigned_url
from payment.models import PointProduct


class PointProductAdminForm(forms.ModelForm):
    image_file = forms.ImageField(label='상품 이미지 업로드', required=False)
    image = forms.CharField(label='상품 이미지 주소', required=False)

    class Meta:
        model = PointProduct
        fields = '__all__'

    def save(self, commit=True):
        instance = super(PointProductAdminForm, self).save(commit=False)
        if self.cleaned_data['image_file']:
            response = generate_presigned_url(
                self.cleaned_data['image_file'].name,
                _type='point_product_image',
                unique=str(instance.id) if instance.id else '0'
            )
            upload_file_to_presigned_url(response['url'], response['fields'], self.cleaned_data['image_file'].file)
            instance.image = response['url'] + response['fields']['key']
        if commit:
            instance.save()
        return instance
