import logging
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q, F
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import Banner

logger = logging.getLogger(__name__)

def get_current_banners(position='hero', limit=1):
    now = timezone.now()
    banners = Banner.objects.filter(
        is_active=True,
        position=position,
        start_date__lte=now
    ).filter(
        Q(end_date__gte=now) | Q(end_date__isnull=True)
    ).order_by('-priority', '-start_date')[:limit]
    
    return banners

@require_GET
def banner_click(request, banner_id):
    try:
        banner = get_object_or_404(Banner, pk=banner_id)
        banner.record_click()
        
        if not banner.url:
            return redirect(request.META.get('HTTP_REFERER', '/'))
            
        return redirect(banner.url)
    except Exception as e:
        logger.error(f"Error processing banner click: {e}")
        return redirect('/')

@csrf_exempt
@require_POST
def banner_impression(request, banner_id):
    try:
        banner = get_object_or_404(Banner, pk=banner_id)
        banner.record_impression()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f"Error recording banner impression: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def get_banners_for_homepage(request):
    context = {
        'hero_banners': get_current_banners(position='hero', limit=1),
        'restaurant_banners': get_current_banners(position='above_restaurants', limit=1),
        'dish_banners': get_current_banners(position='above_dishes', limit=1),
    }
    
    return context

