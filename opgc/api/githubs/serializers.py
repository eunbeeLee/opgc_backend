from rest_framework import serializers

from apps.githubs.models import GithubUser, Organization, Repository


class GithubUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = GithubUser
        fields = '__all__'  # 모든 필드 포함


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'  # 모든 필드 포함


class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = '__all__'  # 모든 필드 포함
