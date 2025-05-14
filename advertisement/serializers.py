from rest_framework import serializers
from .models import Banner

class BannerSerializer(serializers.ModelSerializer):
    ctr = serializers.SerializerMethodField()
    
    class Meta:
        model = Banner
        fields = [
            'id', 'title', 'subtitle', 'content', 'image', 
            'url', 'button_text', 'position', 'color_scheme',
            'start_date', 'end_date', 'is_active', 'priority',
            'impressions', 'clicks', 'ctr'  
        ]
        read_only_fields = ['impressions', 'clicks', 'ctr']
    
    def get_ctr(self, obj):
        if obj.impressions == 0:
            return 0
        return round((obj.clicks / obj.impressions) * 100, 2)