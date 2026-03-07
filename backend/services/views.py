"""
API views for the services app.
Handles category listing, service request creation (with auth), and WhatsApp webhook.
"""

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Category, ServiceRequest
from .serializers import CategorySerializer, ServiceRequestCreateSerializer
from .whatsapp import send_whatsapp_message, build_welcome_message, build_reply

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def category_list(request):
    """GET /api/categories/ — returns all active categories."""
    categories = Category.objects.filter(is_active=True)
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_bookings_view(request):
    """
    GET /api/my-bookings/
    Returns the authenticated user's service request history.
    """
    bookings = ServiceRequest.objects.filter(user=request.user).order_by('-created_at')
    data = [
        {
            'id': b.id,
            'category_name': b.category.name,
            'status': b.status,
            'status_display': b.get_status_display(),
            'customer_phone': b.customer_phone,
            'customer_name': b.customer_name,
            'created_at': b.created_at.strftime('%d %b %Y, %I:%M %p'),
            'work_done': b.work_done,
        }
        for b in bookings
    ]
    return Response({'success': True, 'bookings': data, 'total': len(data)})


@api_view(['POST'])
@permission_classes([AllowAny])
def create_service_request(request):
    """
    POST /api/request/
    Creates a service request, links to logged-in user if authenticated,
    and instantly sends a WhatsApp "Hi" message followed by the conversation tree.
    
    Body: { category_id, phone, name (optional) }
    """
    serializer = ServiceRequestCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'success': False, 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    data = serializer.validated_data
    category = Category.objects.get(id=data['category_id'])

    # Link to authenticated user if available
    user = request.user if request.user.is_authenticated else None
    customer_email = ''
    customer_name = data.get('name', '')

    if user:
        customer_email = user.email
        if not customer_name:
            customer_name = user.get_full_name() or user.email

    # Create the service request
    service_request = ServiceRequest.objects.create(
        user=user,
        category=category,
        customer_phone=data['phone'],
        customer_name=customer_name,
        customer_email=customer_email,
        message=f"Help with {category.name}",
        status='pending',
        conversation_step=0,
    )

    # Step 1: Instantly send "Hi" greeting
    hi_message = (
        f"Hi {customer_name or 'there'}! 👋\n"
        f"Welcome to *Lagech – Instant Home Care*\n"
        f"We received your request for *{category.name}* service.\n\n"
        f"Let me help you right away! 🏠"
    )
    hi_result = send_whatsapp_message(data['phone'], hi_message)

    # Step 2: Send the conversation tree welcome message
    welcome_msg = build_welcome_message(category.name)
    tree_result = send_whatsapp_message(data['phone'], welcome_msg)

    if hi_result['success']:
        service_request.status = 'message_sent'
        service_request.conversation_step = 1
        service_request.save()

    logger.info(
        f"[ServiceRequest] Created #{service_request.id} for "
        f"{category.name} → {data['phone']} (user: {user}) | "
        f"Hi: {hi_result} | Tree: {tree_result}"
    )

    return Response({
        'success': True,
        'request_id': service_request.id,
        'message': 'Service request created! Check your WhatsApp for next steps.',
        'whatsapp_status': hi_result.get('sid', 'unknown'),
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def whatsapp_webhook(request):
    """
    POST /api/whatsapp/webhook/
    Handles incoming WhatsApp messages (Meta Cloud API, with basic
    backward-compatibility for Twilio-style payloads).
    """
    # Twilio-style payload
    from_number = request.data.get('From')
    body = request.data.get('Body')

    # Meta Cloud API payload
    if not from_number or not body:
        try:
            entry = request.data.get('entry', [])[0]
            change = entry.get('changes', [])[0]
            value = change.get('value', {})
            messages = value.get('messages', [])
            if messages:
                msg = messages[0]
                from_number = msg.get('from', from_number)
                if not body:
                    if msg.get("type") == "text":
                        body = msg.get("text", {}).get("body", "")
        except Exception:  # noqa: BLE001
            pass

    body = (body or "").strip()
    clean_phone = (from_number or "").replace("whatsapp:", "")
    if clean_phone and not clean_phone.startswith("+"):
        clean_phone = "+" + clean_phone

    logger.info(f"[Webhook] Incoming from {from_number}: {body}")

    try:
        service_request = ServiceRequest.objects.filter(
            customer_phone=clean_phone,
            status__in=['message_sent', 'in_conversation'],
        ).latest('created_at')
    except ServiceRequest.DoesNotExist:
        send_whatsapp_message(from_number, (
            "🏠 *Lagech – Instant Home Care*\n\n"
            "Hi! We don't have an active request for your number.\n"
            "Please visit our website to get started:\n"
            "🌐 lagech.com"
        ))
        return Response({'status': 'no_active_request'})

    reply_msg, next_step, should_end = build_reply(
        body, service_request.category.name, service_request.conversation_step
    )

    send_whatsapp_message(from_number, reply_msg)

    service_request.conversation_step = next_step
    service_request.notes += f"\nStep {next_step}: User said '{body}'"
    service_request.status = 'assigned' if should_end else 'in_conversation'
    service_request.save()

    return Response({'status': 'ok'})
