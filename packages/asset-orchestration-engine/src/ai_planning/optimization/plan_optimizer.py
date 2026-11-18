from typing import List, Dict, Any, Tuple
from ..tasks.task_graph import PlannedTask

class PlanOptimizer:
    @staticmethod
    def optimize_tasks(tasks: List[PlannedTask]) -> List[PlannedTask]:
        """
        1. Deduplicación de tareas idénticas.
        2. Plegado de operaciones consecutivas (ej. MOVE +10, +20 -> MOVE +30).
        """
        if not tasks:
            return []

        optimized: List[PlannedTask] = []
        accumulated_move: Dict[str, List[float]] = {} # target -> [dx, dy, dz]

        for t in tasks:
            if t.task_type == "MOVE_ACTOR":
                delta = t.parameters.get("delta", (0.0, 0.0, 0.0))
                if t.target not in accumulated_move:
                    accumulated_move[t.target] = [0.0, 0.0, 0.0]
                accumulated_move[t.target][0] += delta[0]
                accumulated_move[t.target][1] += delta[1]
                accumulated_move[t.target][2] += delta[2]
            else:
                # Si había movimientos acumulados para otros targets, emitirlos
                for tgt, total_d in accumulated_move.items():
                    if total_d != [0.0, 0.0, 0.0]:
                        optimized.append(PlannedTask(
                            task_id=f"folded_move_{tgt}",
                            task_type="MOVE_ACTOR",
                            target=tgt,
                            parameters={"delta": tuple(total_d)}
                        ))
                accumulated_move.clear()
                optimized.append(t)

        # Emitir cualquier movimiento plegado remanente
        for tgt, total_d in accumulated_move.items():
            if total_d != [0.0, 0.0, 0.0]:
                optimized.append(PlannedTask(
                    task_id=f"folded_move_{tgt}",
                    task_type="MOVE_ACTOR",
                    target=tgt,
                    parameters={"delta": tuple(total_d)}
                ))

        return optimized
