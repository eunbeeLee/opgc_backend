from django import forms

from apps.notices.models import Notice


class NoticeForm(forms.ModelForm):

    class Meta:
        model = Notice
        fields = '__all__'
