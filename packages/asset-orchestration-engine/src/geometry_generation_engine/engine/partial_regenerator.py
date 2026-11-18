from typing import List, Dict, Set

class PartialRegenerator:
    @classmethod
    def get_affected_components(
        cls,
        target_components: List[str],
        dependency_graph: Dict[str, List[str]]
    ) -> Set[str]:
        affected = set(target_components)
        queue = list(target_components)

        while queue:
            curr = queue.pop(0)
            for parent, children in dependency_graph.items():
                if curr in children and parent not in affected:
                    # Si el componente curr depende de parent, o si children dependen de curr
                    pass
            for child in dependency_graph.get(curr, []):
                if child not in affected:
                    affected.add(child)
                    queue.append(child)

        return affected
