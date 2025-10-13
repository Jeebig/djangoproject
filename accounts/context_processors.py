from typing import Dict, Any
from .models import Notification

def notifications_context(request) -> Dict[str, Any]:
    if request.user.is_authenticated:
        unread = Notification.objects.filter(recipient=request.user, is_read=False).count()
    else:
        unread = 0
    return {
        'notifications_unread_count': unread,
    }
