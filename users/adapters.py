from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

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