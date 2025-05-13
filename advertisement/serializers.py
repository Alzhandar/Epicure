from rest_framework import serializers
from .models import Banner

class BannerSerializer(serializers.ModelSerializer):
    ctr = serializers.SerializerMethodField()

    class Meta:
        model = Banner
        fields = [
            'id', 'title_ru', 'title_kz',
            'subtitle_ru', 'subtitle_kz',
            'content_ru', 'content_kz',
            'image', 'url',
            'button_text_ru', 'button_text_kz',
            'position', 'color_scheme',
            'start_date', 'end_date', 'is_active',
            'priority', 'impressions', 'clicks', 'ctr'
        ]
        read_only_fields = ['impressions', 'clicks', 'ctr']

    def get_ctr(self, obj):
        if obj.impressions == 0:
            return 0
        return round((obj.clicks / obj.impressions) * 100, 2)
