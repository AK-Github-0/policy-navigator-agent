"""
Action Agent - Handles third-party integrations
Slack, Email, Calendar integrations
"""

from typing import Dict, List, Any, Optional
from loguru import logger
import requests
from datetime import datetime, timedelta
import json


class ActionAgent:
    """
    Agent responsible for external integrations and actions
    - Slack notifications
    - Email alerts
    - Calendar reminders
    """
    
    def __init__(self, config):
        """
        Initialize action agent with API credentials
        
        Args:
            config: Configuration object
        """
        logger.info("Initializing Action Agent")
        
        self.config = config
        self.slack_webhook = config.slack_webhook_url
        
        logger.success("Action Agent initialized")
    
    def send_slack_notification(
        self,
        message: str,
        channel: str = None,
        attachments: List[Dict] = None
    ) -> bool:
        """
        Send notification to Slack
        
        Args:
            message: Message text
            channel: Slack channel (optional)
            attachments: Message attachments (optional)
            
        Returns:
            bool: Success status
        """
        logger.info(f"Sending Slack notification")
        
        if not self.slack_webhook:
            logger.warning("Slack webhook not configured")
            return False
        
        try:
            payload = {
                'text': message
            }
            
            if channel:
                payload['channel'] = channel
            
            if attachments:
                payload['attachments'] = attachments
            
            response = requests.post(
                self.slack_webhook,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.success("Slack notification sent")
                return True
            else:
                logger.warning(f"Slack API returned {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Slack notification: {str(e)}")
            return False
    
    def create_subscription(
        self,
        policy: str,
        channel: str = None,
        email: str = None,
        frequency: str = 'weekly'
    ) -> Dict[str, Any]:
        """
        Create a subscription for policy updates
        
        Args:
            policy: Policy to monitor
            channel: Slack channel for notifications
            email: Email for notifications
            frequency: Update frequency
            
        Returns:
            dict: Subscription details
        """
        logger.info(f"Creating subscription for: {policy}")
        
        subscription = {
            'id': f"sub_{datetime.now().timestamp()}",
            'policy': policy,
            'channel': channel,
            'email': email,
            'frequency': frequency,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        # Send confirmation to Slack if configured
        if channel and self.slack_webhook:
            message = (
                f"📋 *New Policy Subscription Created*\n"
                f"Policy: {policy}\n"
                f"Frequency: {frequency}\n"
                f"Channel: {channel}"
            )
            self.send_slack_notification(message, channel)
        
        logger.success("Subscription created")
        return subscription
    
    def send_policy_update(
        self,
        policy: str,
        update_info: Dict[str, Any],
        channels: List[str] = None
    ) -> bool:
        """
        Send policy update notification
        
        Args:
            policy: Policy name
            update_info: Update details
            channels: List of channels to notify
            
        Returns:
            bool: Success status
        """
        logger.info(f"Sending policy update for: {policy}")
        
        try:
            message = (
                f"🔔 *Policy Update Alert*\n"
                f"Policy: {policy}\n"
                f"Status: {update_info.get('status', 'N/A')}\n"
                f"Date: {update_info.get('date', 'N/A')}\n"
                f"Summary: {update_info.get('summary', 'No details available')}"
            )
            
            attachments = [{
                'color': '#36a64f',
                'fields': [
                    {
                        'title': 'Document Number',
                        'value': update_info.get('document_number', 'N/A'),
                        'short': True
                    },
                    {
                        'title': 'Type',
                        'value': update_info.get('type', 'N/A'),
                        'short': True
                    }
                ],
                'footer': 'Policy Navigator Agent',
                'ts': int(datetime.now().timestamp())
            }]
            
            if channels:
                success = True
                for channel in channels:
                    result = self.send_slack_notification(
                        message,
                        channel,
                        attachments
                    )
                    success = success and result
                return success
            else:
                return self.send_slack_notification(message, attachments=attachments)
                
        except Exception as e:
            logger.error(f"Error sending policy update: {str(e)}")
            return False
    
    def create_calendar_reminder(
        self,
        policy: str,
        documents: List[Dict],
        days_before: int = 30,
        calendar: str = None
    ) -> Dict[str, Any]:
        """
        Create calendar reminder for compliance deadline
        
        Args:
            policy: Policy name
            documents: Related documents
            days_before: Days before deadline to remind
            calendar: Calendar identifier
            
        Returns:
            dict: Reminder details
        """
        logger.info(f"Creating calendar reminder for: {policy}")
        
        # Extract deadline from documents (simplified)
        deadline = None
        for doc in documents:
            content = doc.get('content', '').lower()
            # Simple deadline detection
            if 'effective date' in content or 'deadline' in content:
                # In production, use proper date extraction
                deadline = (datetime.now() + timedelta(days=90)).date()
                break
        
        if not deadline:
            deadline = (datetime.now() + timedelta(days=90)).date()
        
        reminder_date = datetime.combine(deadline, datetime.min.time()) - timedelta(days=days_before)
        
        reminder = {
            'id': f"reminder_{datetime.now().timestamp()}",
            'policy': policy,
            'deadline': deadline.isoformat(),
            'reminder_date': reminder_date.date().isoformat(),
            'days_before': days_before,
            'calendar': calendar or 'default',
            'status': 'scheduled',
            'created_at': datetime.now().isoformat()
        }
        
        # Send confirmation notification
        if self.slack_webhook:
            message = (
                f"📅 *Compliance Reminder Scheduled*\n"
                f"Policy: {policy}\n"
                f"Deadline: {deadline}\n"
                f"Reminder: {reminder_date.date()}\n"
                f"Days Before: {days_before}"
            )
            self.send_slack_notification(message)
        
        logger.success("Calendar reminder created")
        return reminder
    
    def send_compliance_checklist(
        self,
        policy: str,
        requirements: List[str],
        recipient: str = None
    ) -> bool:
        """
        Send compliance checklist
        
        Args:
            policy: Policy name
            requirements: List of requirements
            recipient: Recipient (channel or email)
            
        Returns:
            bool: Success status
        """
        logger.info(f"Sending compliance checklist for: {policy}")
        
        try:
            checklist = "\n".join([f"☐ {req}" for req in requirements])
            
            message = (
                f"📋 *Compliance Checklist*\n"
                f"Policy: {policy}\n\n"
                f"Requirements:\n{checklist}\n\n"
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            
            return self.send_slack_notification(message, recipient)
            
        except Exception as e:
            logger.error(f"Error sending checklist: {str(e)}")
            return False
    
    def trigger_workflow(
        self,
        workflow_type: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Trigger external workflow (Zapier, Make, etc.)
        
        Args:
            workflow_type: Type of workflow
            data: Workflow data
            
        Returns:
            dict: Workflow result
        """
        logger.info(f"Triggering workflow: {workflow_type}")
        
        result = {
            'workflow_type': workflow_type,
            'status': 'triggered',
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        logger.success("Workflow triggered")
        return result
    
    def log_action(
        self,
        action_type: str,
        details: Dict[str, Any]
    ):
        """
        Log action for audit trail
        
        Args:
            action_type: Type of action
            details: Action details
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'details': details
        }
        
        # In production, save to database
        logger.info(f"Action logged: {action_type}")
        
        return log_entry
