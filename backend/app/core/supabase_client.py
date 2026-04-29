import os
import httpx
from typing import Optional, List, Any


class SupabaseClient:
    """Client Supabase minimal utilisant uniquement httpx"""
    
    def __init__(self, url: str, key: str):
        self.url = url.rstrip("/")
        self.key = key
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
    
    def table(self, table_name: str):
        return SupabaseTable(self, table_name)
    
    @property
    def storage(self):
        return SupabaseStorage(self)
    
    @property
    def auth(self):
        return SupabaseAuth(self)


class SupabaseTable:
    def __init__(self, client: SupabaseClient, table: str):
        self.client = client
        self.table = table
    
    def select(self, columns: str = "*"):
        return SupabaseQuery(self.client, self.table, columns)
    
    def insert(self, data: dict):
        return SupabaseInsert(self.client, self.table, data)
    
    def update(self, data: dict):
        return SupabaseUpdate(self.client, self.table, data)
    
    def delete(self):
        return SupabaseDelete(self.client, self.table)


class SupabaseQuery:
    def __init__(self, client: SupabaseClient, table: str, columns: str):
        self.client = client
        self.table = table
        self.columns = columns
        self._filters = []
    
    def eq(self, column: str, value: Any):
        self._filters.append(f"{column}=eq.{value}")
        return self
    
    def ilike(self, column: str, pattern: str):
        self._filters.append(f"{column}=ilike.{pattern}")
        return self
    
    def in_(self, column: str, values: List):
        values_str = ",".join(str(v) for v in values)
        self._filters.append(f"{column}=in.({values_str})")
        return self
    
    def order(self, column: str, desc: bool = False):
        order_str = f"order={column}.{'desc' if desc else 'asc'}"
        if hasattr(self, '_order'):
            self._order += "," + order_str
        else:
            self._order = order_str
        return self
    
    def limit(self, count: int):
        self._limit = count
        return self

    def range(self, start: int, end: int):
        self._range = (start, end)
        return self
    
    def execute(self) -> dict:
        url = f"{self.client.url}/rest/v1/{self.table}?select={self.columns}"
        
        if self._filters:
            url += "&" + "&".join(self._filters)
        if hasattr(self, '_order'):
            url += f"&{self._order}"
        
        headers = self.client.headers
        
        if hasattr(self, '_limit') and not hasattr(self, '_range'):
            headers = {**headers, "Range": f"0-{self._limit - 1}"}
        elif hasattr(self, '_range'):
            headers = {**headers, "Range": f"{self._range[0]}-{self._range[1]}"}
        
        resp = httpx.get(url, headers=headers, timeout=30.0)
        
        if resp.status_code == 200:
            data = resp.json()
            result = {"data": data}
            if hasattr(self, '_range') or hasattr(self, '_limit'):
                result["count"] = len(data)
            return result
        print(f"Query error: {resp.status_code} - {resp.text}")
        return {"data": []}


class SupabaseInsert:
    def __init__(self, client: SupabaseClient, table: str, data: dict):
        self.client = client
        self.table = table
        self.data = data
    
    def execute(self) -> dict:
        url = f"{self.client.url}/rest/v1/{self.table}"
        resp = httpx.post(url, json=self.data, headers=self.client.headers, timeout=30.0)
        
        if resp.status_code in [200, 201]:
            return {"data": [resp.json()]} if resp.text else {"data": [self.data]}
        return {"data": []}


class SupabaseUpdate:
    def __init__(self, client: SupabaseClient, table: str, data: dict):
        self.client = client
        self.table = table
        self.data = data
        self._filters = []
    
    def eq(self, column: str, value: Any):
        self._filters.append(f"{column}=eq.{value}")
        return self
    
    def execute(self) -> dict:
        url = f"{self.client.url}/rest/v1/{self.table}?" + "&".join(self._filters)
        resp = httpx.patch(url, json=self.data, headers=self.client.headers, timeout=30.0)
        return {"data": [resp.json()]} if resp.status_code == 200 else {"data": []}


class SupabaseDelete:
    def __init__(self, client: SupabaseClient, table: str):
        self.client = client
        self.table = table
        self._filters = []
    
    def eq(self, column: str, value: Any):
        self._filters.append(f"{column}=eq.{value}")
        return self
    
    def execute(self) -> dict:
        url = f"{self.client.url}/rest/v1/{self.table}?" + "&".join(self._filters)
        resp = httpx.delete(url, headers=self.client.headers, timeout=30.0)
        return {"data": []}


class SupabaseAuth:
    def __init__(self, client: SupabaseClient):
        self.client = client
    
    def sign_in_with_password(self, credentials: dict) -> dict:
        url = f"{self.client.url}/auth/v1/token?grant_type=password"
        resp = httpx.post(url, json=credentials, headers=self.client.headers, timeout=30.0)
        
        if resp.status_code == 200:
            data = resp.json()
            user_data = data.get("user", {})
            return type('obj', (), {
                'session': type('obj', (), {
                    'access_token': data.get("access_token"),
                    'expires_in': data.get("expires_in"),
                    'refresh_token': data.get("refresh_token")
                })(),
                'user': type('obj', (), {
                    'id': user_data.get("id"),
                    'email': user_data.get("email"),
                    'email_confirmed_at': user_data.get("email_confirmed_at")
                })()
            })()
        raise Exception("Auth failed")
    
    def sign_up(self, credentials: dict) -> dict:
        url = f"{self.client.url}/auth/v1/signup"
        resp = httpx.post(url, json=credentials, headers=self.client.headers, timeout=30.0)
        
        if resp.status_code in [200, 201]:
            data = resp.json()
            return type('obj', (), {
                'session': type('obj', (), {
                    'access_token': data.get("access_token", "dummy"),
                    'expires_in': 3600
                })(),
                'user': type('obj', (), {
                    'id': data.get("id", "dummy"),
                    'email': data.get("email")
                })()
            })()
        raise Exception("Signup failed")
    
    def sign_out(self):
        pass
    
    def get_user(self, token: str) -> dict:
        url = f"{self.client.url}/auth/v1/user"
        headers = {**self.client.headers, "Authorization": f"Bearer {token}"}
        resp = httpx.get(url, headers=headers, timeout=30.0)
        
        if resp.status_code == 200:
            return {"user": resp.json()}
        return {"user": None}


class SupabaseStorage:
    def __init__(self, client: SupabaseClient):
        self.client = client
    
    def from_(self, bucket: str):
        return SupabaseBucket(self.client, bucket)


class SupabaseBucket:
    def __init__(self, client: SupabaseClient, bucket: str):
        self.client = client
        self.bucket = bucket
    
    def upload(self, path: str, file_content: bytes, file_options: dict = None) -> Optional[str]:
        url = f"{self.client.url}/storage/v1/object/{self.bucket}/{path}"
        headers = {**self.client.headers, "Content-Type": "application/octet-stream"}
        resp = httpx.post(url, content=file_content, headers=headers, timeout=60.0)
        
        if resp.status_code in [200, 201]:
            return path
        return None
    
    def download(self, path: str) -> Optional[bytes]:
        url = f"{self.client.url}/storage/v1/object/{self.bucket}/{path}"
        resp = httpx.get(url, headers=self.client.headers, timeout=30.0)
        
        if resp.status_code == 200:
            return resp.content
        return None
    
    def remove(self, paths: List[str]) -> bool:
        url = f"{self.client.url}/storage/v1/object/{self.bucket}"
        resp = httpx.delete(url, json={"paths": paths}, headers=self.client.headers, timeout=30.0)
        return resp.status_code in [200, 204]
    
    def get_public_url(self, path: str) -> str:
        return f"{self.client.url}/storage/v1/object/public/{self.bucket}/{path}"


def create_client(url: str, key: str) -> SupabaseClient:
    return SupabaseClient(url, key)


# Alias pour compatibilité
Client = SupabaseClient