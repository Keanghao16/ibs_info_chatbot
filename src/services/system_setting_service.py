from sqlalchemy.orm import Session
from ..database.models import SystemSettings
from typing import Optional

class SystemSettingService:
    """Service for managing system settings"""
    
    @staticmethod
    def get_settings(db: Session) -> SystemSettings:
        """Get system settings, create if not exists"""
        settings = db.query(SystemSettings).first()
        if not settings:
            settings = SystemSettings()
            db.add(settings)
            db.commit()
            db.refresh(settings)
        return settings
    
    @staticmethod
    def update_general_settings(db: Session, settings_data: dict) -> dict:
        """Update general system settings"""
        try:
            settings = SystemSettingService.get_settings(db)
            
            if 'system_name' in settings_data:
                settings.system_name = settings_data['system_name']
            if 'welcome_message' in settings_data:
                settings.welcome_message = settings_data['welcome_message']
            if 'support_email' in settings_data:
                settings.support_email = settings_data['support_email']
            if 'max_chat_duration' in settings_data:
                settings.max_chat_duration = int(settings_data['max_chat_duration'])
            if 'auto_assign_chats' in settings_data:
                settings.auto_assign_chats = settings_data['auto_assign_chats']
            if 'maintenance_mode' in settings_data:
                settings.maintenance_mode = settings_data['maintenance_mode']
            
            db.commit()
            db.refresh(settings)
            return {"success": True, "message": "General settings updated successfully"}
        except Exception as e:
            db.rollback()
            return {"success": False, "message": f"Error updating settings: {str(e)}"}
    
    @staticmethod
    def update_bot_settings(db: Session, settings_data: dict) -> dict:
        """Update bot configuration settings"""
        try:
            settings = SystemSettingService.get_settings(db)
            
            if 'response_timeout' in settings_data:
                settings.response_timeout = int(settings_data['response_timeout'])
            if 'offline_message' in settings_data:
                settings.offline_message = settings_data['offline_message']
            if 'enable_file_uploads' in settings_data:
                settings.enable_file_uploads = settings_data['enable_file_uploads']
            if 'enable_typing_indicator' in settings_data:
                settings.enable_typing_indicator = settings_data['enable_typing_indicator']
            
            db.commit()
            db.refresh(settings)
            return {"success": True, "message": "Bot settings updated successfully"}
        except Exception as e:
            db.rollback()
            return {"success": False, "message": f"Error updating bot settings: {str(e)}"}
    
    @staticmethod
    def update_notification_settings(db: Session, settings_data: dict) -> dict:
        """Update notification settings"""
        try:
            settings = SystemSettingService.get_settings(db)
            
            if 'email_notifications' in settings_data:
                settings.email_notifications = settings_data['email_notifications']
            if 'notify_new_user' in settings_data:
                settings.notify_new_user = settings_data['notify_new_user']
            if 'notify_new_chat' in settings_data:
                settings.notify_new_chat = settings_data['notify_new_chat']
            if 'notify_unassigned_chat' in settings_data:
                settings.notify_unassigned_chat = settings_data['notify_unassigned_chat']
            if 'notification_email' in settings_data:
                settings.notification_email = settings_data['notification_email']
            
            db.commit()
            db.refresh(settings)
            return {"success": True, "message": "Notification settings updated successfully"}
        except Exception as e:
            db.rollback()
            return {"success": False, "message": f"Error updating notification settings: {str(e)}"}