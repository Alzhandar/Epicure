from rest_framework import serializers
from .models import Banner

class BannerSerializer(serializers.ModelSerializer):
    ctr = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    subtitle = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    button_text = serializers.SerializerMethodField()

    class Meta:
        model = Banner
        fields = [
            'id', 'title', 'subtitle', 'content', 'image',
            'url', 'button_text', 'position', 'color_scheme',
            'start_date', 'end_date', 'is_active', 'priority',
            'impressions', 'clicks', 'ctr'
        ]
        read_only_fields = ['impressions', 'clicks', 'ctr']

    def get_lang(self):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return getattr(request.user, 'language', 'ru') or 'ru'
        return 'ru'

    def get_title(self, obj):
        lang = self.get_lang()
        return getattr(obj, f'title_{lang}', obj.title)

    def get_subtitle(self, obj):
        lang = self.get_lang()
        return getattr(obj, f'subtitle_{lang}', obj.subtitle)

    def get_content(self, obj):
        lang = self.get_lang()
        return getattr(obj, f'content_{lang}', obj.content)

    def get_button_text(self, obj):
        lang = self.get_lang()
        return getattr(obj, f'button_text_{lang}', obj.button_text)

    def get_ctr(self, obj):
        if obj.impressions == 0:
            return 0
        return round((obj.clicks / obj.impressions) * 100, 2)
