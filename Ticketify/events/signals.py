from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Booking, Ticket


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile when new user is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save user profile when user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(post_save, sender=Booking)
def create_tickets_for_booking(sender, instance, created, **kwargs):
    """Automatically create tickets when booking is confirmed"""
    # Only create tickets if booking was just created, confirmed, and has no tickets yet
    if created and instance.status == 'confirmed' and instance.tickets.count() == 0:
        for i in range(instance.quantity):
            Ticket.objects.create(
                booking=instance,
                event=instance.event,
                user=instance.user,
                attendee_name=instance.user.get_full_name() or instance.user.username,
                attendee_email=instance.email
            )

        # Update available tickets on event or show_time if present
        if instance.show_time:
            st = instance.show_time
            st.available_tickets = max(0, st.available_tickets - instance.quantity)
            st.save()
        else:
            event = instance.event
            event.available_tickets = max(0, event.available_tickets - instance.quantity)
            event.save()
