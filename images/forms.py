from django import forms
from .models import Image

import urllib
from urllib import request
from django.core.files.base import ContentFile
from django.utils.text import slugify



class ImageCreateForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('title', 'url', 'description')
        widgets = {'url': forms.HiddenInput,}


    def clean_url(self):
        url = self.cleaned_data['url']
        valid_extensions = ['jpg', 'jpeg', 'png',]

        # decoded_url = unquote(url)

        extension = url.rsplit('.', 1)[1].lower()

        if extension not in valid_extensions:
            raise forms.ValidationError('The given URL does not ' \
                                        'match valid image extensions.')
        return url

    def save(self, force_insert=False, force_update=False, commit=True):

        image = super().save(commit=False)
        image_url = self.cleaned_data['url']
        name = slugify(image.title)
        extension = image_url.rsplit('.', 1)[1].lower()

        image_name = f'{name}.{extension}'

         # Add User-Agent header to avoid being blocked - 403 Forbidden
        req = urllib.request.Request(
            image_url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )

        # download image from the given URL
        try:
            response = request.urlopen(req)
            image.image.save(image_name, ContentFile(response.read()), save=False)

        except urllib.error.HTTPError as e:
            raise forms.ValidationError(f'HTTP Error: {e.code} - {e.reason}')
        
        except urllib.error.URLError as e:
            raise forms.ValidationError(f'URL Error: {e.reason}')

        if commit:
            image.save()
        return image