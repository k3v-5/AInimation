from dataclasses import dataclass, field
from typing import Tuple, Dict, Any, List, Optional

@dataclass
class SocketDefinition:
    socket_id: str
    parent_component: str
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0) # en uu (cm)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0) # Roll, Pitch, Yaw

class SocketManager:
    def __init__(self):
        self.sockets: Dict[str, SocketDefinition] = {}

    def register_socket(self, socket_def: SocketDefinition) -> Tuple[bool, Optional[str]]:
        if socket_def.socket_id in self.sockets:
            return False, f"SOCKET_INVALID: Socket '{socket_def.socket_id}' already exists."
        self.sockets[socket_def.socket_id] = socket_def
        return True, None

    def list_sockets(self) -> List[SocketDefinition]:
        return list(self.sockets.values())
