
from rest_framework import serializers

from apps.githubs.models import GithubUser
from apps.ranks.models import UserRank


class RankSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRank
        fields = ('id', 'ranking', 'score', 'github_user')  # 모든 필드 포함

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        if instance.github_user:
            ret['github_user'] = {
                'id': instance.github_user.id,
                'username': instance.github_user.username,
                'avatar_url': instance.github_user.avatar_url,
            }
        else:
            ret['github_user'] = None

        return ret


class TierSerializer(serializers.ModelSerializer):
    tier = serializers.CharField(source='get_tier_display')

    class Meta:
        model = GithubUser
        fields = ('id', 'username', 'name', 'avatar_url', 'tier', 'user_rank', 'company', 'bio',
                  'continuous_commit_day')
