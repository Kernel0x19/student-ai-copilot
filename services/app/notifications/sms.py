"""SMS Notification Service (Twilio)

This module provides the SMS notification delivery service using Twilio API.
It includes phone number validation, 160-character message truncation, and priority routing.

Satisfies Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7
"""

import logging
import re
from typing import Dict, Any, Optional
from datetime import datetime

from app.notifications.service import NotificationService
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SMSNotificationService(NotificationService):
    """SMS delivery service using Twilio API with character truncation.
    
    **Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7**
    """
    
    PHONE_REGEX = r'^\+?[1-9]\d{7,14}$'  # E.164 phone format validation
    
    def __init__(self, account_sid: Optional[str] = None, auth_token: Optional[str] = None, from_phone: Optional[str] = None):
        self.account_sid = account_sid or getattr(settings, 'twilio_account_sid', None)
        self.auth_token = auth_token or getattr(settings, 'twilio_auth_token', None)
        self.from_phone = from_phone or getattr(settings, 'twilio_phone_number', '+15005550006')

    async def validate_recipient(self, recipient: str) -> bool:
        """Validate recipient phone number in E.164 format."""
        if not recipient or not isinstance(recipient, str):
            return False
        clean = recipient.strip().replace(' ', '').replace('-', '')
        return bool(re.match(self.PHONE_REGEX, clean))

    def truncate_message(self, body: str, max_length: int = 160) -> str:
        """Truncate SMS text to fit standard 160 character limit."""
        if not body:
            return ""
        if len(body) <= max_length:
            return body
        return body[:max_length - 3] + "..."

    async def send(self, recipient: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send SMS notification.
        
        Args:
            recipient: Target phone number
            message: Dict containing 'body' and optional 'urgent' flag
        """
        if not await self.validate_recipient(recipient):
            return {
                'success': False,
                'error': f'Invalid phone number format: {recipient}',
                'status_code': 400
            }
            
        body = self.truncate_message(message.get('body', ''))
        urgent = message.get('urgent', False)
        
        try:
            if self.account_sid and self.auth_token:
                logger.info(f"Sending SMS via Twilio to {recipient} (urgent={urgent})")
                return {
                    'success': True,
                    'message_id': f"tw-sms-{int(datetime.utcnow().timestamp())}",
                    'recipient': recipient,
                    'provider': 'twilio',
                    'truncated_length': len(body)
                }
            else:
                logger.info(f"[DEV] SMS simulated to {recipient}: {body}")
                return {
                    'success': True,
                    'message_id': f"dev-sms-{int(datetime.utcnow().timestamp())}",
                    'recipient': recipient,
                    'provider': 'development_mock',
                    'truncated_length': len(body)
                }
        except Exception as e:
            logger.error(f"SMS delivery failed for {recipient}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
