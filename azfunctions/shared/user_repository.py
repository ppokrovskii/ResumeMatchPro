from datetime import datetime, timedelta, UTC
from typing import List, Optional
from azure.cosmos import DatabaseProxy, PartitionKey, ContainerProxy
from users.models import UserDb

class UserRepository:
    def __init__(self, db_client: DatabaseProxy):
        container_id = "users"
        partition_key = PartitionKey(path="/userId")
        self.container = db_client.create_container_if_not_exists(
            id=container_id,
            partition_key=partition_key
        )
        
    def get_user(self, user_id: str) -> UserDb | None:
        """Get user by ID"""
        try:
            item = self.container.read_item(item=user_id, partition_key=user_id)
            return UserDb(**item)
        except:
            return None
            
    def create_user(self, user: dict) -> UserDb:
        """Create new user"""
        result = self.container.create_item(user)
        return UserDb(**result)
    
    def update_user(self, user: UserDb) -> UserDb:
        """Update existing user"""
        result = self.container.upsert_item(user.model_dump())
        return UserDb(**result)
    
    def increment_files_count(self, user_id: str) -> UserDb:
        """Increment user's files count"""
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        user.filesCount += 1
        return self.update_user(user)
    
    def decrement_files_count(self, user_id: str) -> UserDb:
        """Decrement user's files count"""
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        user.filesCount = max(0, user.filesCount - 1)
        return self.update_user(user)
    
    def increment_matching_count(self, user_id: str) -> UserDb:
        """Increment user's matching count, reset if 30 days passed"""
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
            
        # Reset matching count if 30 days passed
        if datetime.now(UTC) - user.lastMatchingReset > timedelta(days=30):
            user.matchingUsedCount = 0
            user.lastMatchingReset = datetime.now(UTC)
            
        user.matchingUsedCount += 1
        return self.update_user(user)
    
    def can_upload_file(self, user_id: str) -> bool:
        """Check if user can upload more files"""
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
            
        # Reset matching count if 30 days passed
        if datetime.now(UTC) - user.lastMatchingReset > timedelta(days=30):
            user.matchingUsedCount = 0
            user.lastMatchingReset = datetime.now(UTC)
            user = self.update_user(user)
            
        return user.filesCount < user.filesLimit and user.matchingUsedCount < user.matchingLimit
    
    def can_perform_matching(self, user_id: str) -> bool:
        """Check if user can perform more matchings"""
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
            
        # Reset matching count if 30 days passed
        if datetime.now(UTC) - user.lastMatchingReset > timedelta(days=30):
            return True
            
        return user.matchingUsedCount < user.matchingLimit

    def search_users(self, query: str) -> List[UserDb]:
        """Search users by name, email, or ID"""
        # Create a query that searches across multiple fields
        cosmos_query = """
        SELECT * FROM c 
        WHERE CONTAINS(LOWER(c.name), LOWER(@query)) 
           OR CONTAINS(LOWER(c.email), LOWER(@query))
           OR CONTAINS(LOWER(c.userId), LOWER(@query))
        """
        
        # Execute the query
        params = [{"name": "@query", "value": query.lower()}]
        results = list(self.container.query_items(
            query=cosmos_query,
            parameters=params,
            enable_cross_partition_query=True
        ))
        
        # Convert results to UserDb objects
        return [UserDb(**result) for result in results] 