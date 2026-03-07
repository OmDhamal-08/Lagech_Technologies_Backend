from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    """Service category (e.g., Chimney, Gas Stove, Geyser)."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, help_text="Lucide React icon name")
    description = models.TextField(blank=True)
    price_min = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    price_max = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class ServiceRequest(models.Model):
    """
    Logs each user request. Linked to authenticated user when available.
    Tracks WhatsApp message delivery and conversation state.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('message_sent', 'WhatsApp Message Sent'),
        ('in_conversation', 'In Conversation'),
        ('assigned', 'Expert Assigned'),
        ('in_progress', 'Work In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='service_requests',
        help_text="Logged-in user who made the request"
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='requests')
    customer_phone = models.CharField(max_length=20)
    customer_name = models.CharField(max_length=100, blank=True)
    customer_email = models.EmailField(blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    conversation_step = models.PositiveIntegerField(default=0)
    work_done = models.BooleanField(default=False, help_text="Has the work been completed?")
    work_notes = models.TextField(blank=True, help_text="Details about work done / pending")
    assigned_expert = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} {self.customer_phone} - {self.category.name} ({self.status})"
