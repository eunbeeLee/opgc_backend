from rest_framework import serializers

from apps.githubs.models import GithubUser, Organization, Repository


class GithubUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = GithubUser
        fields = '__all__'  # 모든 필드 포함

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        org_qs = Organization.objects.filter(org__github_user_id=instance.id)
        ret['organizations'] = OrganizationSerializer(org_qs, many=True).data

        repo_qs = Repository.objects.filter(github_user_id=instance.id)
        ret['repositories'] = RepositorySerializer(repo_qs, many=True).data

        return ret


class OrganizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = '__all__'  # 모든 필드 포함


class RepositorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Repository
        fields = '__all__'  # 모든 필드 포함
