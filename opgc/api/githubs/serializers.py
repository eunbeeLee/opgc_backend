import json

from rest_framework import serializers

from apps.githubs.models import GithubUser, Organization, Repository, UserLanguage, Language


class GithubUserSerializer(serializers.ModelSerializer):
    tier = serializers.CharField(source='get_tier_display')

    class Meta:
        model = GithubUser
        fields = '__all__'  # 모든 필드 포함

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        ret['organizations'] = OrganizationSerializer(instance.organization.all(), many=True).data
        ret['repositories'] = RepositorySerializer(instance.repository.all(), many=True).data
        user_language = UserLanguage.objects.filter(github_user_id=instance.id).prefetch_related('language')
        ret['languages'] = UserLanguageSerializer(user_language, many=True).data
        ret['status'] = instance.get_status_display()

        return ret


class GithubUserListSerializer(serializers.ModelSerializer):
    tier = serializers.CharField(source='get_tier_display')

    class Meta:
        model = GithubUser
        fields = '__all__'  # 모든 필드 포함

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        ret['organizations'] = OrganizationSerializer(instance.organization.all(), many=True).data
        ret['status'] = instance.get_status_display()

        return ret


class OrganizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = ('id', 'name', 'description', 'logo')


class RepositorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Repository
        fields = ('id', 'contribution', 'name', 'full_name', 'owner',
                  'organization', 'stargazers_count', 'rep_language', 'languages')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['languages'] = json.loads(ret['languages']) if ret['languages'] else None

        return ret


class UserLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLanguage
        fields = ('language', 'number')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['language'] = instance.language.__str__()
        return ret


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ('id', 'type')
