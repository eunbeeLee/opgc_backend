from rest_framework import serializers

from apps.notices.models import Notice


class NoticeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notice
        fields = '__all__'


class NoticeListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notice
        fields = ['id', 'created', 'updated', 'title']
