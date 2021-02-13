
from rest_framework import serializers

from apps.ranks.models import UserRank


class RankSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRank
        fields = ('id', 'ranking', 'score', 'github_user')  # 모든 필드 포함

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['github_user'] = instance.github_user.username if instance.github_user else None

        return ret
