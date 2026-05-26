"""
Mashov API Client
Wrapper for interacting with the Mashov API
"""

import asyncio
import aiohttp
import json
import logging
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, List, Union
from urllib.parse import urljoin


# Configure logging
logger = logging.getLogger(__name__)


# Custom Exceptions
class MashovError(Exception):
    """Base exception for Mashov client errors"""
    pass


class MashovAuthError(MashovError):
    """Authentication failed"""
    pass


class MashovGuidNotFoundError(MashovError):
    """Student GUID not found in response"""
    pass


class MashovChildNotFoundError(MashovError):
    """Child not found (for parent accounts)"""
    pass


class MashovClient:
    """Client for interacting with Mashov API"""
    
    # Constants
    BASE_URL = "https://web.mashov.info/api/"
    LOGIN_ENDPOINT = "login"
    CSRF_HEADER = "x-csrf-token"
    CSRF_HEADER_ALT = "X-CSRF-Token"
    NULL_GUID = "00000000-0000-0000-0000-000000000000"
    GUID_KEYS = ["guid", "studentGuid", "userGuid", "id", "studentId", "userId"]
    GUID_MIN_LENGTH = 30
    GUID_MIN_DASHES = 4
    
    _instance: Optional['MashovClient'] = None
    
    def __init__(self):
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        self.semel: Optional[str] = None
        self.year: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.csrf_token: Optional[str] = None
        self.student_guid: Optional[str] = None
        self.children: List[Dict[str, Any]] = []
        self.authenticated = False
    
    @classmethod
    def get_instance(cls) -> 'MashovClient':
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def configure(self, username: str, password: str, semel: str, year: str):
        """Configure client credentials"""
        self.username = username
        self.password = password
        self.semel = semel
        self.year = year
    
    def is_authenticated(self) -> bool:
        """Check if client is authenticated"""
        return self.authenticated and self.session is not None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    def _is_valid_guid(self, value: Any) -> bool:
        """Check if value looks like a valid GUID"""
        return (isinstance(value, str) and 
                len(value) > self.GUID_MIN_LENGTH and 
                value.count('-') >= self.GUID_MIN_DASHES and
                value != self.NULL_GUID)
    
    def _extract_csrf_token(self, response: aiohttp.ClientResponse) -> Optional[str]:
        """Extract CSRF token from response headers"""
        csrf_token = response.headers.get(self.CSRF_HEADER) or response.headers.get(self.CSRF_HEADER_ALT)
        if csrf_token:
            logger.debug("CSRF token extracted from response (length: %d)", len(csrf_token))
        return csrf_token
    
    def _extract_children_from_response(self, data: Dict[str, Any]) -> bool:
        """Extract children list from login response (for parent accounts)
        
        Returns:
            True if children were found, False otherwise
        """
        if not isinstance(data, dict):
            return False
            
        # Parent accounts have children in accessToken
        if "accessToken" in data and isinstance(data["accessToken"], dict):
            access_token = data["accessToken"]
            if "children" in access_token and isinstance(access_token["children"], list):
                self.children = access_token["children"]
                if len(self.children) > 0:
                    first_child = self.children[0]
                    if "childGuid" in first_child:
                        self.student_guid = first_child["childGuid"]
                        child_name = f"{first_child.get('privateName', '')} {first_child.get('familyName', '')}"
                        logger.info("Found %d children. Using first child: %s", len(self.children), child_name)
                        return True
        return False
    
    def _extract_student_guid_from_response(self, data: Dict[str, Any]) -> bool:
        """Extract student GUID from login response (for student accounts)
        
        Returns:
            True if GUID was found, False otherwise
        """
        if not isinstance(data, dict):
            return False
        
        # Try common GUID keys at top level
        for key in self.GUID_KEYS:
            if key in data:
                value = data[key]
                if self._is_valid_guid(value):
                    self.student_guid = value
                    logger.info("Found student GUID in '%s' field", key)
                    return True
        
        return False
    
    def _is_successful_login(self, data: Dict[str, Any], status: int) -> bool:
        """Check if login response indicates success"""
        if status != 200:
            return False
        
        # Success indicators
        return (data.get("success", False) or 
                data.get("authenticated", False) or 
                "token" in data or 
                "accessToken" in data or
                "userSettings" in data or
                "schoolSettings" in data)
    
    def _get_error_message(self, data: Dict[str, Any], default: str = "Unknown error") -> str:
        """Extract error message from response"""
        return data.get('message', data.get('error', default))
    
    async def login(self) -> bool:
        """Login to Mashov API
        
        Raises:
            MashovAuthError: If authentication fails
        """
        if not all([self.username, self.password, self.semel, self.year]):
            raise MashovAuthError("Missing required credentials. Please configure username, password, semel, and year.")
        
        session = await self._get_session()
        login_url = urljoin(self.BASE_URL, self.LOGIN_ENDPOINT)
        
        login_data = {
            "username": self.username,
            "password": self.password,
            "semel": self.semel,
            "year": self.year
        }
        
        headers = {"Content-Type": "application/json"}
        logger.info("Attempting login for user: %s", self.username)
        
        try:
            async with session.post(login_url, json=login_data, headers=headers) as resp:
                logger.debug("Login response status: %d", resp.status)
                
                # Extract CSRF token
                csrf_token = self._extract_csrf_token(resp)
                if csrf_token:
                    self.csrf_token = csrf_token
                
                # Parse response
                try:
                    data = await resp.json()
                except Exception:
                    error_text = await resp.text()
                    logger.error("Login response is not JSON: %s", error_text[:200])
                    raise MashovAuthError(f"Login failed: Response is not JSON (status {resp.status})")
                
                # Check if login was successful
                if not self._is_successful_login(data, resp.status):
                    error_msg = self._get_error_message(data)
                    logger.error("Login failed: %s", error_msg)
                    raise MashovAuthError(f"Login failed: {error_msg}")
                
                # Login successful
                self.authenticated = True
                logger.info("Login successful")
                
                # Extract student GUID(s)
                guid_found = self._extract_children_from_response(data)
                
                if not guid_found:
                    guid_found = self._extract_student_guid_from_response(data)
                
                if not guid_found:
                    logger.warning("Student GUID not found in login response")
                    logger.debug("Response keys: %s", list(data.keys())[:20])
                
                return True
        
        except aiohttp.ClientError as e:
            self.authenticated = False
            logger.error("Network error during login: %s", str(e))
            raise MashovAuthError(f"Network error: {str(e)}")
        except Exception as e:
            self.authenticated = False
            if isinstance(e, MashovAuthError):
                raise
            logger.error("Authentication error: %s", str(e))
            raise MashovAuthError(f"Authentication error: {str(e)}")
    
    async def _ensure_authenticated(self):
        """Ensure client is authenticated"""
        if not self.is_authenticated():
            await self.login()
    
    def _construct_url(self, endpoint: str) -> str:
        """Construct full URL for endpoint
        
        Args:
            endpoint: API endpoint (e.g., "schools" or "students/homework")
            
        Returns:
            Full URL for the endpoint
            
        Raises:
            MashovGuidNotFoundError: If student endpoint requires GUID but none is available
        """
        if endpoint.startswith("students/"):
            if not self.student_guid:
                raise MashovGuidNotFoundError(
                    "Student GUID not found. Please check login credentials or use set_active_child()."
                )
            
            # Replace students/ with students/{guid}/
            endpoint_path = endpoint.replace("students/", "", 1)
            endpoint = f"students/{self.student_guid}/{endpoint_path}"
            logger.debug("Constructed student endpoint: %s", endpoint)
        
        return urljoin(self.BASE_URL, endpoint)
    
    def _prepare_headers(self, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Prepare request headers with CSRF token and defaults"""
        headers = dict(custom_headers) if custom_headers else {}
        
        if self.csrf_token:
            headers[self.CSRF_HEADER] = str(self.csrf_token)
        
        headers.setdefault("accept", "application/json, text/plain, */*")
        headers.setdefault("referer", "https://web.mashov.info/students/main/")
        
        return headers
    
    async def _parse_response(self, response: aiohttp.ClientResponse) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Parse response and return data"""
        content_type = response.headers.get("Content-Type", "")
        
        if "application/json" in content_type:
            return await response.json()
        else:
            return {"data": await response.text()}
    
    async def _handle_error_response(self, response: aiohttp.ClientResponse):
        """Handle error response and log details"""
        content_type = response.headers.get("Content-Type", "")
        
        try:
            if "application/json" in content_type:
                error_data = await response.json()
                error_text = json.dumps(error_data, indent=2)
            else:
                error_text = await response.text()
        except Exception:
            error_text = "Could not read error response"
        
        logger.error("Error response (%d): %s", response.status, error_text[:500])
        response.raise_for_status()
    
    async def _request(self, endpoint: str, method: str = "GET", **kwargs) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Make authenticated API request
        
        Args:
            endpoint: API endpoint
            method: HTTP method (GET, POST, etc.)
            **kwargs: Additional arguments for request (params, headers, etc.)
            
        Returns:
            Response data (dict or list)
            
        Raises:
            MashovGuidNotFoundError: If student GUID is required but not found
            aiohttp.ClientError: For HTTP errors
        """
        await self._ensure_authenticated()
        session = await self._get_session()
        
        # Construct URL
        url = self._construct_url(endpoint)
        
        # Prepare headers
        custom_headers = kwargs.pop("headers", None)
        headers = self._prepare_headers(custom_headers)
        
        # Prepare request kwargs
        request_kwargs = dict(kwargs)
        request_kwargs["headers"] = headers
        
        logger.debug("Request: %s %s", method, url)
        
        # Make request
        async with session.request(method, url, **request_kwargs) as resp:
            # Handle 401 - retry after re-authentication
            if resp.status == 401:
                logger.warning("Received 401, attempting to re-authenticate")
                await self.login()
                headers = self._prepare_headers(custom_headers)
                request_kwargs["headers"] = headers
                
                async with session.request(method, url, **request_kwargs) as retry_resp:
                    if retry_resp.status >= 400:
                        await self._handle_error_response(retry_resp)
                    return await self._parse_response(retry_resp)
            
            # Handle other errors
            elif resp.status >= 400:
                await self._handle_error_response(resp)
            
            # Success
            return await self._parse_response(resp)
    
    @asynccontextmanager
    async def _with_child_context(self, child_guid: Optional[str] = None, child_name: Optional[str] = None):
        """Context manager for temporarily switching to a different child

        Args:
            child_guid: Optional child GUID to switch to
            child_name: Optional child name to switch to

        Yields:
            None

        Example:
            async with client._with_child_context(child_name="John"):
                homework = await client._request("students/homework")
        """
        await self._ensure_authenticated()
        guid_to_use = self._resolve_child_guid(child_guid, child_name)
        original_guid = self.student_guid
        self.student_guid = guid_to_use
        
        try:
            yield
        finally:
            if original_guid:
                self.student_guid = original_guid
    
    def _resolve_child_guid(self, child_guid: Optional[str] = None, child_name: Optional[str] = None) -> str:
        """Resolve child GUID from parameters or use current active child
        
        Args:
            child_guid: Optional child GUID
            child_name: Optional child name to search for
            
        Returns:
            The resolved child GUID
            
        Raises:
            MashovChildNotFoundError: If child not found or no active child
        """
        # If child_guid is provided, validate it exists
        if child_guid:
            for child in self.children:
                if child.get("childGuid") == child_guid:
                    return child_guid
            raise MashovChildNotFoundError(f"Child with GUID {child_guid} not found")
        
        # If child_name is provided, find the child by name
        if child_name:
            name_lower = child_name.lower()
            for child in self.children:
                if child.get("privateName", "").lower() == name_lower:
                    guid = child.get("childGuid")
                    if guid:
                        return guid
            raise MashovChildNotFoundError(f"Child with name '{child_name}' not found")
        
        # Use current active child (student_guid)
        if not self.student_guid:
            raise MashovChildNotFoundError("No active child set and no child specified. Please specify child_guid or child_name.")
        
        return self.student_guid
    
    def get_children(self) -> List[Dict[str, Any]]:
        """Get list of all children (for parent accounts)
        
        Returns:
            List of children with fields: childGuid, familyName, privateName, classCode, classNum, gender, groups
            
        Note:
            This information is available after login.
        """
        return self.children
    
    def set_active_child(self, child_guid: Optional[str] = None, index: Optional[int] = None) -> bool:
        """Set the active child for API requests
        
        Args:
            child_guid: The GUID of the child to set as active (takes precedence over index)
            index: Index of child in children list (0-based)
            
        Returns:
            True if successful
            
        Raises:
            MashovChildNotFoundError: If child not found or index out of range
            
        Example:
            # Set by GUID
            client.set_active_child(child_guid="abc-123")
            
            # Set by index
            client.set_active_child(index=0)
        """
        if child_guid:
            # Find child by GUID
            for child in self.children:
                if child.get("childGuid") == child_guid:
                    self.student_guid = child_guid
                    child_name = f"{child.get('privateName', '')} {child.get('familyName', '')}"
                    logger.info("Active child set to: %s", child_name)
                    return True
            raise MashovChildNotFoundError(f"Child with GUID {child_guid} not found")
        elif index is not None:
            # Use index
            if index < 0 or index >= len(self.children):
                raise MashovChildNotFoundError(f"Child index {index} out of range (0-{len(self.children)-1})")
            child = self.children[index]
            self.student_guid = child["childGuid"]
            child_name = f"{child.get('privateName', '')} {child.get('familyName', '')}"
            logger.info("Active child set to (index %d): %s", index, child_name)
            return True
        else:
            raise ValueError("Either child_guid or index must be provided")
    
    def set_active_child_by_name(self, name: str) -> bool:
        """Set the active child by name (searches privateName)
        
        Args:
            name: The first name of the child
            
        Returns:
            True if successful
            
        Raises:
            MashovChildNotFoundError: If child not found
        """
        name_lower = name.lower()
        for child in self.children:
            if child.get("privateName", "").lower() == name_lower:
                self.student_guid = child.get("childGuid")
                child_name = f"{child.get('privateName', '')} {child.get('familyName', '')}"
                logger.info("Active child set to: %s", child_name)
                return True
        raise MashovChildNotFoundError(f"Child with name '{name}' not found")
    
    def get_active_child(self) -> Optional[Dict[str, Any]]:
        """Get the currently active child information
        
        Returns:
            Dictionary with child information, or None if no active child
        """
        if not self.student_guid:
            return None
        for child in self.children:
            if child.get("childGuid") == self.student_guid:
                return child
        return None
    
    # API Methods - with child context support
    
    async def get_all_grades(self, subject: Optional[str] = None, child_guid: Optional[str] = None, child_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all grades, optionally filtered by subject
        
        Args:
            subject: Optional subject name to filter grades
            child_guid: Optional child GUID to query. If not provided, uses current active child.
            child_name: Optional child name to query. If not provided, uses current active child.
        """
        async with self._with_child_context(child_guid, child_name):
            params = {"subject": subject} if subject else {}
            return await self._request("students/grades", params=params)
    
    async def get_schools(self) -> List[Dict[str, Any]]:
        """Get list of all schools"""
        return await self._request("schools")
    
    async def get_homework(self, child_guid: Optional[str] = None, child_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get homework assignments for the student
        
        Args:
            child_guid: Optional child GUID to query. If not provided, uses current active child.
            child_name: Optional child name to query. If not provided, uses current active child.
        
        Returns:
            List of homework items with: lessonId, lessonDate, lesson, homework, groupId, remark, studentGuid, subjectName
        """
        async with self._with_child_context(child_guid, child_name):
            return await self._request("students/homework")
    
    async def get_alfon(self, child_guid: Optional[str] = None, child_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get the class directory (alfon) with classmates' contact information
        
        Args:
            child_guid: Optional child GUID to query. If not provided, uses current active child.
            child_name: Optional child name to query. If not provided, uses current active child.
        
        Returns:
            List of students with: studentGuid, familyName, privateName, classCode, classNum, city, address, cellphone
        """
        async with self._with_child_context(child_guid, child_name):
            return await self._request("students/alfon")
    
    async def get_behave(self, child_guid: Optional[str] = None, child_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get behavior events for the student (attendance, absences, good words, etc.)
        
        Args:
            child_guid: Optional child GUID to query. If not provided, uses current active child.
            child_name: Optional child name to query. If not provided, uses current active child.
        
        Returns:
            List of behavior events with: studentGuid, eventCode, justified, lessonId, timestamp, achvaName, etc.
        """
        async with self._with_child_context(child_guid, child_name):
            return await self._request("students/behave")
    
    async def get_files(self, child_guid: Optional[str] = None, child_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get files for the student
        
        Args:
            child_guid: Optional child GUID to query. If not provided, uses current active child.
            child_name: Optional child name to query. If not provided, uses current active child.
        """
        async with self._with_child_context(child_guid, child_name):
            return await self._request("students/files")
    
    async def get_groups(self, child_guid: Optional[str] = None, child_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get groups/classes the student belongs to
        
        Args:
            child_guid: Optional child GUID to query. If not provided, uses current active child.
            child_name: Optional child name to query. If not provided, uses current active child.
        """
        async with self._with_child_context(child_guid, child_name):
            return await self._request("students/groups")
    
    async def get_timetable(self, child_guid: Optional[str] = None, child_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get the student's timetable/schedule
        
        Args:
            child_guid: Optional child GUID to query. If not provided, uses current active child.
            child_name: Optional child name to query. If not provided, uses current active child.
        
        Returns:
            List of timetable entries with lesson times, subjects, and classrooms
        """
        async with self._with_child_context(child_guid, child_name):
            return await self._request("students/timetable")
    
    async def get_maakav(self, child_guid: Optional[str] = None, child_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get maakav (progress tracking) information for the student
        
        Args:
            child_guid: Optional child GUID to query. If not provided, uses current active child.
            child_name: Optional child name to query. If not provided, uses current active child.
        """
        async with self._with_child_context(child_guid, child_name):
            return await self._request("students/maakav")
    
    async def get_lessons_history(self, child_guid: Optional[str] = None, child_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get lessons history for the student
        
        Args:
            child_guid: Optional child GUID to query. If not provided, uses current active child.
            child_name: Optional child name to query. If not provided, uses current active child.
        
        Returns:
            List of past lessons with details about topics covered, dates, and teachers
        """
        async with self._with_child_context(child_guid, child_name):
            return await self._request("students/lessons/history")
    
    async def close(self):
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("HTTP session closed")
