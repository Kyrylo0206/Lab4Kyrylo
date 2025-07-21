from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime

class UserService:
    """Mock user service for GraphQL demo"""
    
    def __init__(self):
        self.users = {
            "user-1": {
                "id": "user-1",
                "username": "john_doe",
                "email": "john@example.com",
                "full_name": "John Doe"
            },
            "user-2": {
                "id": "user-2", 
                "username": "jane_smith",
                "email": "jane@example.com",
                "full_name": "Jane Smith"
            }
        }
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def get_user_by_todo(self, todo_id: str) -> Optional[Dict[str, Any]]:
        """Get user who created a specific todo (mock implementation)"""
        # In a real app, this would query by todo ownership
        return self.users.get("user-1")  # Return default user for demo

class TagService:
    """Mock tag service for GraphQL demo"""
    
    def __init__(self):
        self.tags_by_todo = {}
        self.all_tags = [
            {"id": "tag-1", "name": "Work", "color": "#3498db"},
            {"id": "tag-2", "name": "Personal", "color": "#2ecc71"},
            {"id": "tag-3", "name": "Urgent", "color": "#e74c3c"},
            {"id": "tag-4", "name": "Shopping", "color": "#f39c12"},
            {"id": "tag-5", "name": "Health", "color": "#9b59b6"}
        ]
    
    def get_tags_for_todo(self, todo_id: str) -> List[Dict[str, Any]]:
        """Get tags for a specific todo"""
        # Return different tags based on todo_id for demo
        if todo_id.endswith('1') or todo_id.endswith('3') or todo_id.endswith('5'):
            return [self.all_tags[0], self.all_tags[2]]  # Work + Urgent
        elif todo_id.endswith('2') or todo_id.endswith('4'):
            return [self.all_tags[1], self.all_tags[3]]  # Personal + Shopping
        else:
            return [self.all_tags[0], self.all_tags[4]]  # Work + Health
    
    def get_all_tags(self) -> List[Dict[str, Any]]:
        """Get all available tags"""
        return self.all_tags

class ProfileService:
    """Mock profile service for GraphQL demo"""
    
    def __init__(self):
        self.profiles = {
            "user-1": {
                "id": "profile-user-1",
                "bio": "Software developer passionate about clean code and GraphQL",
                "avatar_url": "https://example.com/avatars/john.jpg",
                "created_at": "2023-01-15T10:30:00"
            },
            "user-2": {
                "id": "profile-user-2",
                "bio": "Product manager who loves organizing todos and getting things done",
                "avatar_url": "https://example.com/avatars/jane.jpg", 
                "created_at": "2023-02-20T14:15:00"
            }
        }
    
    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile by user ID"""
        return self.profiles.get(user_id)

class SettingsService:
    """Mock settings service for GraphQL demo"""
    
    def __init__(self):
        self.settings = {
            "profile-user-1": {
                "theme": "dark",
                "notifications_enabled": True,
                "language": "en"
            },
            "profile-user-2": {
                "theme": "light",
                "notifications_enabled": False,
                "language": "uk"
            }
        }
    
    def get_settings(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get user settings by profile ID"""
        return self.settings.get(profile_id, {
            "theme": "light",
            "notifications_enabled": True,
            "language": "en"
        })

# Factory functions for dependency injection
def get_user_service() -> UserService:
    return UserService()

def get_tag_service() -> TagService:
    return TagService()

def get_profile_service() -> ProfileService:
    return ProfileService()

def get_settings_service() -> SettingsService:
    return SettingsService()
