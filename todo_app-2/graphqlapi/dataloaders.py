from typing import List, Dict, Any, Optional
from strawberry.dataloader import DataLoader
import asyncio

class UserDataLoader:
    
    def __init__(self, user_service):
        self.user_service = user_service
        self.loader = DataLoader(load_fn=self._load_users)
    
    async def _load_users(self, user_ids: List[str]) -> List[Optional[Dict[str, Any]]]:
        try:
            users = []
            for user_id in user_ids:
                user = self.user_service.get_user(user_id) if self.user_service else None
                if user:
                    users.append(user)
                else:
                    users.append({
                        'id': user_id,
                        'username': 'default_user',
                        'email': 'user@example.com',
                        'full_name': 'Default User'
                    })
            return users
        except Exception as e:
            print(f"Error loading users: {e}")
            return [None] * len(user_ids)
    
    async def load(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.loader.load(user_id)

class TagDataLoader:
    
    def __init__(self, tag_service):
        self.tag_service = tag_service
        self.loader = DataLoader(load_fn=self._load_tags_for_todos)
    
    async def _load_tags_for_todos(self, todo_ids: List[str]) -> List[List[Dict[str, Any]]]:
        try:
            tags_by_todo = []
            for todo_id in todo_ids:
                if self.tag_service:
                    tags = self.tag_service.get_tags_for_todo(todo_id)
                    tags_by_todo.append(tags)
                else:
                    tags_by_todo.append([
                        {'id': f'tag-1-{todo_id}', 'name': 'Work', 'color': '#blue'},
                        {'id': f'tag-2-{todo_id}', 'name': 'Personal', 'color': '#green'}
                    ])
            return tags_by_todo
        except Exception as e:
            print(f"Error loading tags: {e}")
            return [[] for _ in todo_ids]
    
    async def load(self, todo_id: str) -> List[Dict[str, Any]]:
        return await self.loader.load(todo_id)

class ProfileDataLoader:
    
    def __init__(self, profile_service):
        self.profile_service = profile_service
        self.loader = DataLoader(load_fn=self._load_profiles)
    
    async def _load_profiles(self, user_ids: List[str]) -> List[Optional[Dict[str, Any]]]:
        try:
            profiles = []
            for user_id in user_ids:
                if self.profile_service:
                    profile = self.profile_service.get_profile(user_id)
                    profiles.append(profile)
                else:
                    profiles.append({
                        'id': f'profile-{user_id}',
                        'bio': 'Default user bio',
                        'avatar_url': 'https://example.com/avatar.jpg',
                        'created_at': '2024-01-01T00:00:00'
                    })
            return profiles
        except Exception as e:
            print(f"Error loading profiles: {e}")
            return [None] * len(user_ids)
    
    async def load(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.loader.load(user_id)

def create_dataloaders(context):
    user_service = context.get('user_service')
    tag_service = context.get('tag_service')
    profile_service = context.get('profile_service')
    
    return {
        'user_loader': UserDataLoader(user_service),
        'tag_loader': TagDataLoader(tag_service),
        'profile_loader': ProfileDataLoader(profile_service)
    }
