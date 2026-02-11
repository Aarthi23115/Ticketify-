from django.contrib import admin
from .models import UserProfile, Category, Event, Booking, Ticket, Review, MovieShowTime


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'is_organizer', 'created_at']
    list_filter = ['is_organizer', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'name': ()}


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'event_type', 'organizer', 'event_date', 'start_time', 'status', 'available_tickets', 'is_featured']
    list_filter = ['status', 'category', 'event_type', 'is_featured', 'event_date', 'created_at']
    search_fields = ['title', 'description', 'venue', 'city']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'event_date'
    readonly_fields = ['created_at', 'updated_at']
    
    def get_fieldsets(self, request, obj=None):
        """Return different fieldsets based on event type"""
        if obj and obj.event_type == 'movie':
            return (
                ('Basic Information', {
                    'fields': ('title', 'slug', 'description', 'category', 'organizer', 'status', 'is_featured', 'event_type')
                }),
                ('Event Details', {
                    'fields': ('venue', 'address', 'city', 'event_date', 'start_time')
                }),
                ('Pricing & Capacity', {
                    'fields': ('price', 'total_tickets', 'available_tickets')
                }),
                ('Media', {
                    'fields': ('image',)
                }),
                ('Timestamps', {
                    'fields': ('created_at', 'updated_at'),
                    'classes': ('collapse',)
                }),
            )
        else:
            return (
                ('Basic Information', {
                    'fields': ('title', 'slug', 'description', 'category', 'organizer', 'status', 'is_featured', 'event_type')
                }),
                ('Event Details', {
                    'fields': ('venue', 'address', 'city', 'event_date', 'start_time')
                }),
                ('Pricing & Capacity', {
                    'fields': ('price', 'total_tickets', 'available_tickets')
                }),
                ('Media', {
                    'fields': ('image',)
                }),
                ('Timestamps', {
                    'fields': ('created_at', 'updated_at'),
                    'classes': ('collapse',)
                }),
            )
    
    def get_fields(self, request, obj=None):
        """Show event_type in the form"""
        fields = super().get_fields(request, obj)
        if 'event_type' not in fields:
            fields = list(fields) + ['event_type']
        return fields


class MovieShowTimeInline(admin.TabularInline):
    """Inline admin for movie show times"""
    model = MovieShowTime
    extra = 1
    fields = ['show_date', 'start_time', 'end_time', 'available_tickets']


@admin.register(MovieShowTime)
class MovieShowTimeAdmin(admin.ModelAdmin):
    list_display = ['event', 'show_date', 'start_time', 'end_time', 'available_tickets']
    list_filter = ['show_date', 'event']
    search_fields = ['event__title']
    date_hierarchy = 'show_date'
    readonly_fields = []
    
    fieldsets = (
        ('Show Information', {
            'fields': ('event', 'show_date')
        }),
        ('Show Time', {
            'fields': ('start_time', 'end_time')
        }),
        ('Capacity', {
            'fields': ('available_tickets',)
        }),
    )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'event':
            kwargs['queryset'] = Event.objects.filter(event_type='movie')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'user', 'event', 'show_time', 'quantity', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'event__event_type']
    search_fields = ['booking_id', 'user__username', 'event__title', 'email']
    readonly_fields = ['booking_id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_id', 'user', 'event', 'show_time', 'status')
        }),
        ('Details', {
            'fields': ('quantity', 'total_amount', 'email', 'phone')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_id', 'event', 'user', 'status', 'validated_at', 'created_at']
    list_filter = ['status', 'created_at', 'validated_at']
    search_fields = ['ticket_id', 'verification_code', 'attendee_name', 'attendee_email']
    readonly_fields = ['ticket_id', 'verification_code', 'qr_code', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['event__title', 'user__username', 'comment']
    date_hierarchy = 'created_at'
