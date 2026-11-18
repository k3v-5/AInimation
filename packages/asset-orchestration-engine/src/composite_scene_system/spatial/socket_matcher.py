import math
from typing import Dict, Any, Tuple, Optional
from ..core.scene_schema import SocketDefinition, AssetInstance

class SocketMatcher:
    @staticmethod
    def match_and_align(
        source_instance: AssetInstance,
        source_socket: SocketDefinition,
        target_instance: AssetInstance,
        target_socket: SocketDefinition
    ) -> Tuple[bool, Dict[str, float], str]:
        # 1. Validar compatibilidad de sockets
        if target_socket.socket_type not in source_socket.compatibility and source_socket.socket_type != target_socket.socket_type:
            return False, {}, f"INCOMPATIBLE_SOCKETS: {source_socket.socket_type} cannot connect to {target_socket.socket_type}."

        # 2. Calcular alineamiento automático
        t_target = target_instance.transform
        t_pos_x = t_target["x"] + target_socket.local_position[0]
        t_pos_y = t_target["y"] + target_socket.local_position[1]
        t_pos_z = t_target["z"] + target_socket.local_position[2]

        # Invertir orientación para conectar cara a cara
        aligned_rot_z = (t_target.get("rot_z", 0.0) + 180.0) % 360.0

        new_transform = {
            "x": round(t_pos_x - source_socket.local_position[0], 3),
            "y": round(t_pos_y - source_socket.local_position[1], 3),
            "z": round(t_pos_z - source_socket.local_position[2], 3),
            "rot_z": aligned_rot_z
        }

        return True, new_transform, "Socket aligned successfully."
