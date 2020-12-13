from rest_framework import serializers

from apps.githubs.models import GithubUser, Organization


class GithubUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = GithubUser
        fields = '__all__'  # 모든 필드 포함


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'  # 모든 필드 포함
