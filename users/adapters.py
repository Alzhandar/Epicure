from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        
        if sociallogin.account.provider == 'google':
            # Set username from Google name
            if data.get('name'):
                user.username = data.get('name')
            
            # Set email from Google
            if data.get('email'):
                user.email = data.get('email')
        
        return user
    
    def get_login_redirect_url(self, request):
        # Always redirect to Vue.js frontend after social login
        return settings.FRONTEND_BASE_URL