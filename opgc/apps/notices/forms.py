from django import forms

from apps.notices.models import Notice


class NoticeForm(forms.ModelForm):

    class Meta:
        model = Notice
        widgets = {
            'content': forms.Textarea(attrs={'cols': 50, 'rows': 5}),
        }
        fields = '__all__'
