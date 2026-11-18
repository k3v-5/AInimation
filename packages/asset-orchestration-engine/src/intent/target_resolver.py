import re
from typing import Dict, List, Optional, Tuple
from ..core.scene_graph import SceneGraph

class TargetResolver:
    # Diccionario de sinónimos comunes (ES/EN)
    SYNONYMS: Dict[str, List[str]] = {
        "blade": ["hoja", "filo", "espada_hoja", "blade"],
        "handle": ["mango", "empunadura", "grip", "handle"],
        "guard": ["guarda", "gavilanes", "cruz", "guard"],
        "pommel": ["pomo", "remate", "pommel"],
        "seat": ["asiento", "base", "seat"],
        "leg": ["pata", "patas", "leg", "legs"],
        "body": ["cuerpo", "barril", "cubo", "body", "barrel", "cube", "base"],
        "barrel": ["barril", "barrel", "tanque"],
        "shield": ["escudo", "shield"],
        "sword": ["espada", "sword"]
    }

    @classmethod
    def normalize_text(cls, text: str) -> str:
        t = text.lower().strip()
        t = re.sub(r'^(el|la|los|las|un|una|the|a|an)\s+', '', t)
        t = t.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")
        return t

    @classmethod
    def resolve_component(cls, raw_name: str, graph: SceneGraph) -> Tuple[Optional[str], float, List[str]]:
        """
        Devuelve (target_id, confidence, candidates)
        Si hay ambigüedad -> (None, <0.70, [candidatos])
        """
        if not raw_name:
            return None, 0.0, []

        clean_query = cls.normalize_text(raw_name)

        # 1. Coincidencia exacta con ID de nodo o nombre de nodo
        exact_matches = []
        for nid, node in graph.nodes.items():
            if nid == graph.root_id:
                continue
            if node.id.lower() == clean_query.lower() or node.name.lower() == clean_query.lower():
                exact_matches.append(nid)

        if len(exact_matches) == 1:
            return exact_matches[0], 1.0, exact_matches

        # 2. Coincidencia por sufijo/nombre de componente
        suffix_matches = []
        for nid, node in graph.nodes.items():
            if nid == graph.root_id:
                continue
            norm_node_name = cls.normalize_text(node.name)
            if norm_node_name == clean_query or nid.lower().endswith(f".{clean_query}"):
                suffix_matches.append(nid)

        if len(suffix_matches) == 1:
            return suffix_matches[0], 0.98, suffix_matches

        # 3. Coincidencia por sinónimos
        synonym_matches = []
        for syn_key, syn_list in cls.SYNONYMS.items():
            norm_syn_list = [cls.normalize_text(s) for s in syn_list]
            if clean_query in norm_syn_list or clean_query == syn_key:
                # Buscar nodos que coincidan con syn_key o contengan syn_key / sinónimos
                for nid, node in graph.nodes.items():
                    if nid == graph.root_id:
                        continue
                    n_clean = cls.normalize_text(node.name)
                    if (n_clean == syn_key or any(n_clean == s for s in norm_syn_list)
                        or syn_key in n_clean or any(s in n_clean for s in norm_syn_list)):
                        if nid not in synonym_matches:
                            synonym_matches.append(nid)

        if len(synonym_matches) == 1:
            return synonym_matches[0], 0.95, synonym_matches
        elif len(synonym_matches) > 1:
            # Ambigüedad detectada
            return None, 0.50, synonym_matches

        # 4. Búsqueda por subcadena / partial match
        partial_matches = []
        for nid, node in graph.nodes.items():
            if nid == graph.root_id:
                continue
            n_clean = cls.normalize_text(node.name)
            if clean_query in n_clean or n_clean in clean_query:
                partial_matches.append(nid)

        if len(partial_matches) == 1:
            return partial_matches[0], 0.85, partial_matches
        elif len(partial_matches) > 1:
            return None, 0.40, partial_matches

        # Si el asset tiene solo 1 componente hijo, resolverlo como fallback seguro
        child_nodes = [nid for nid in graph.nodes.keys() if nid != graph.root_id]
        if len(child_nodes) == 1 and clean_query in ["it", "objeto", "componente", "modelo", "mesh", "shape"]:
            return child_nodes[0], 0.90, child_nodes

        return None, 0.0, []
