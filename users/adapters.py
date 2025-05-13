# your_app/adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken

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
        # Generate JWT token for the user
        user = request.user
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        # Redirect to frontend with JWT token
        redirect_url = f"{settings.FRONTEND_BASE_URL}?token={access_token}"
        
        return redirect_url