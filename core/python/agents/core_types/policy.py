import asyncio
import uuid
import logging
from enum import Enum
from typing import Dict, Optional, Tuple

logger = logging.getLogger("atlas.policy")

class CapabilityState(Enum):
    NONE = "NONE"
    REQUESTED = "REQUESTED"
    PENDING = "PENDING"
    GRANTED = "GRANTED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"

class AuthorizationManager:
    def __init__(self):
        # Maps capability -> state
        self._states: Dict[str, CapabilityState] = {}
        # Maps capability -> (request_id, one_time_code)
        self._requests: Dict[str, Tuple[str, str]] = {}
        # Maps capability -> Event to wake up waiting tasks
        self._events: Dict[str, asyncio.Event] = {}
        # Callback to trigger IPC request to frontend
        self._auth_request_callback = None
        
    def set_auth_request_callback(self, callback):
        """Callback signature: async def callback(capability: str, request_id: str)"""
        self._auth_request_callback = callback

    def get_state(self, capability: str) -> CapabilityState:
        return self._states.get(capability, CapabilityState.NONE)

    async def request_capability(self, capability: str) -> CapabilityState:
        state = self.get_state(capability)
        
        if state == CapabilityState.GRANTED:
            return state
            
        if state in (CapabilityState.NONE, CapabilityState.EXPIRED, CapabilityState.REVOKED):
            self._states[capability] = CapabilityState.REQUESTED
            request_id = str(uuid.uuid4())
            one_time_code = str(uuid.uuid4())
            self._requests[capability] = (request_id, one_time_code)
            
            self._states[capability] = CapabilityState.PENDING
            if capability not in self._events:
                self._events[capability] = asyncio.Event()
            self._events[capability].clear()
            
            logger.info(f"Capability {capability} requested. Request ID: {request_id}")
            
            if self._auth_request_callback:
                # Fire the callback to notify the frontend (which opens the URI)
                asyncio.create_task(self._auth_request_callback(capability, request_id))
            else:
                logger.warning("No auth_request_callback registered. Request will pend forever.")
                
        # Wait until state changes from PENDING
        await self._events[capability].wait()
        
        return self.get_state(capability)

    def validate_and_grant(self, request_id: str, code: str) -> bool:
        """Called by the auth callback endpoint to validate the code and grant the capability."""
        for cap, (req_id, expected_code) in self._requests.items():
            if req_id == request_id:
                if code == expected_code:
                    logger.info(f"Capability {cap} granted for request {request_id}")
                    self._states[cap] = CapabilityState.GRANTED
                    # Clear the request data (single-use code consumed)
                    del self._requests[cap]
                    if cap in self._events:
                        self._events[cap].set()
                    return True
                else:
                    logger.warning(f"Invalid code provided for request {request_id}")
                    return False
                    
        logger.warning(f"Request ID {request_id} not found.")
        return False

    def revoke(self, capability: str):
        if capability in self._states:
            self._states[capability] = CapabilityState.REVOKED
            if capability in self._events:
                self._events[capability].set()
