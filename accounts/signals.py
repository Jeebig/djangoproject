from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from .models import Follow, Notification

@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance: Follow, created: bool, **kwargs):
    """Создаём уведомление при новой подписке"""
    if not created:
        return
    follower = instance.follower
    following = instance.following
    # Для получателя (на кого подписались)
    Notification.objects.create(
        recipient=following,
        message=f"{follower.username} подписался на вас",
        link=reverse('accounts:profile-user', kwargs={'username': follower.username}),
    )
