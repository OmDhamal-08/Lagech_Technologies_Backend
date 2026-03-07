"""
WhatsApp automation module using Meta WhatsApp Cloud API.
Handles message sending and automated conversation tree logic.
"""

import logging
from django.conf import settings
import requests

logger = logging.getLogger(__name__)


def send_whatsapp_message(to_phone, body):
    """
    Send a WhatsApp message via Meta WhatsApp Cloud API.
    
    Args:
        to_phone: Recipient phone number (e.g., "+919800000000")
        body: Message text to send
    
    Returns:
        dict with 'success' bool and 'sid' or 'error' string
    """
    phone_id = getattr(settings, "META_WA_PHONE_NUMBER_ID", "")
    access_token = getattr(settings, "META_WA_ACCESS_TOKEN", "")
    api_version = getattr(settings, "META_WA_API_VERSION", "v21.0")

    # Log the message for development/debugging
    logger.info(f"[WhatsApp] To: {to_phone} | Message: {body}")

    if not phone_id or not access_token:
        logger.warning("[WhatsApp] Meta Cloud API not configured — message logged only.")
        return {"success": True, "sid": "LOG_ONLY", "message": "Logged (Meta not configured)"}

    # Cloud API expects number without leading '+'
    clean_phone = to_phone.strip()
    if clean_phone.startswith("+"):
        clean_phone = clean_phone[1:]

    url = f"https://graph.facebook.com/{api_version}/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": clean_phone,
        "type": "text",
        "text": {"body": body},
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        data = resp.json()
        if resp.status_code >= 200 and resp.status_code < 300:
            message_id = None
            try:
                message_id = data["messages"][0]["id"]
            except Exception:  # noqa: BLE001
                message_id = data
            logger.info(f"[WhatsApp] Sent via Meta. Response: {data}")
            return {"success": True, "sid": message_id}
        logger.error(f"[WhatsApp] Meta API error {resp.status_code}: {data}")
        return {"success": False, "error": str(data)}
    except Exception as e:  # noqa: BLE001
        logger.error(f"[WhatsApp] Failed to send via Meta: {e}")
        return {"success": False, "error": str(e)}


ISSUE_MENUS = {
    "Geyser": {
        "title": "Geyser issues",
        "items": {
            "1": "No hot water",
            "2": "Water leaking",
            "3": "Geyser not turning on",
            "4": "Strange noise / smell",
        },
    },
    "Bathroom": {
        "title": "Bathroom issues",
        "items": {
            "1": "Tap leaking / low pressure",
            "2": "Shower not working",
            "3": "Flush / commode issue",
            "4": "Drain blockage",
        },
    },
    "Electrical": {
        "title": "Electrical issues",
        "items": {
            "1": "Switch / socket not working",
            "2": "Short circuit / sparks",
            "3": "MCB tripping frequently",
            "4": "New wiring / point needed",
        },
    },
    "AC / Cooler": {
        "title": "AC / Cooler issues",
        "items": {
            "1": "Not cooling properly",
            "2": "Water leakage",
            "3": "Noisy unit / fan",
            "4": "Regular servicing",
        },
    },
    "Chimney": {
        "title": "Chimney issues",
        "items": {
            "1": "Low suction / smoke in kitchen",
            "2": "Filter cleaning / replacement",
            "3": "Unusual noise / vibration",
            "4": "Not turning on",
        },
    },
    "Gas Stove": {
        "title": "Gas stove issues",
        "items": {
            "1": "Burner not lighting",
            "2": "Low flame",
            "3": "Gas smell / leakage",
            "4": "Ignition not working",
        },
    },
    "Washing Machine": {
        "title": "Washing machine issues",
        "items": {
            "1": "Not spinning / agitating",
            "2": "Water not draining",
            "3": "Leaking water",
            "4": "Error code / not starting",
        },
    },
    "Plumbing": {
        "title": "Plumbing issues",
        "items": {
            "1": "Pipe leakage",
            "2": "Blockage / choke",
            "3": "New tap / fitting",
            "4": "Water tank / motor issue",
        },
    },
    "Other": {
        "title": "Other home issues",
        "items": {
            "1": "Carpentry",
            "2": "Painting",
            "3": "Appliance repair",
            "4": "Something else",
        },
    },
}


def build_welcome_message(category_name):
    """
    Build the initial WhatsApp message when a user requests help.
    This starts the conversation tree.
    """
    menu = ISSUE_MENUS.get(category_name)
    if not menu:
        # Generic fallback
        return (
            f"🏠 *Lagech – Instant Home Care*\n\n"
            f"Hi! You've requested help with *{category_name}*.\n\n"
            f"To help you better, please tell us more:\n\n"
            f"1️⃣ Repair / Fix existing issue\n"
            f"2️⃣ New installation\n"
            f"3️⃣ Annual servicing / maintenance\n"
            f"4️⃣ Emergency (urgent, need help ASAP)\n\n"
            f"Reply with the number (1-4) to continue."
        )

    lines = [
        "🏠 *Lagech – Instant Home Care*",
        "",
        f"You've requested help with *{category_name}*.",
        f"Please pick the issue:",
        "",
    ]
    for key, label in menu["items"].items():
        lines.append(f"{key}️⃣ {label}")
    lines.append("")
    lines.append("Reply with the number (e.g. 3).")
    return "\n".join(lines)


def build_reply(user_input, category_name, conversation_step):
    """
    Conversation tree logic — processes user's reply and returns next message.
    
    Args:
        user_input: The text the user sent (e.g., "1", "2")
        category_name: The service category name
        conversation_step: Current step in the conversation (0=welcome sent, 1=type selected, etc.)
    
    Returns:
        tuple: (reply_message, next_step, should_end_conversation)
    """
    user_input = user_input.strip()

    # Step 1: User selects specific issue for the chosen category
    if conversation_step == 1:
        menu = ISSUE_MENUS.get(category_name)
        if not menu:
            # Fallback to old generic flow
            service_types = {
                "1": "Repair / Fix",
                "2": "New Installation",
                "3": "Annual Servicing",
                "4": "Emergency",
            }
            service_type = service_types.get(user_input)
            if not service_type:
                return (
                    "❌ Please reply with a valid number (1-4).\n\n"
                    "1️⃣ Repair / Fix\n2️⃣ New Installation\n3️⃣ Annual Servicing\n4️⃣ Emergency",
                    1,
                    False,
                )
            return (
                f"✅ Got it! *{service_type}* for *{category_name}*.\n\n"
                f"Our team will now review your request and contact you shortly on WhatsApp.\n"
                f"You can also reply in this chat with more details or photos.",
                99,
                True,
            )

        issue_label = menu["items"].get(user_input)
        if not issue_label:
            # Re-send the menu if invalid input
            welcome_again = build_welcome_message(category_name)
            return (
                "❌ Please reply with one of the numbers shown.\n\n" + welcome_again,
                1,
                False,
            )

        return (
            f"✅ Got it! *{issue_label}* for *{category_name}*.\n\n"
            f"Our team will now review your request and contact you shortly on WhatsApp.\n"
            f"You can also reply in this chat with more details, photos, or preferred time.",
            99,
            True,
        )

    # Step 2: User selects timing
    elif conversation_step == 2:
        timing_options = {
            '1': 'Today (2-4 hours)',
            '2': 'Tomorrow',
            '3': 'This week',
            '4': 'Quote only',
        }
        timing = timing_options.get(user_input)
        if not timing:
            return (
                "❌ Please reply with a valid number (1-4).",
                2,
                False
            )
        
        return (
            f"🎉 *Booking Confirmed!*\n\n"
            f"📋 *Summary:*\n"
            f"• Service: {category_name}\n"
            f"• Timing: {timing}\n\n"
            f"A verified expert will be assigned shortly. "
            f"You'll receive their details within 30 minutes.\n\n"
            f"💰 Estimated cost: Shared after assessment\n"
            f"✅ 30-day service warranty\n\n"
            f"Thank you for choosing *Lagech*! 🏠",
            99,  # End conversation
            True
        )

    # Default / unknown step
    else:
        return (
            "🏠 *Lagech – Instant Home Care*\n\n"
            "Sorry, I didn't understand that. "
            "Please start a new request from our website:\n"
            "🌐 lagech.com",
            0,
            True
        )
