"""
UAF-81.99: Voronoi Fracture Engine.
Generates uniform and radial impact cluster Voronoi seed distributions and partitions
3D volumes into hierarchical Macro Chunks and Micro Debris fragments.
"""

import math
import random
from typing import Dict, List, Optional, Tuple, Set

from ..core.contracts import (
    Vector3D,
    BoundingBox3D,
    VoronoiSite,
    FracturedPiece,
    ClusterHierarchyLevel,
    FracturePatternType,
)


class VoronoiFractureEngine:
    """
    Solves 3D Voronoi site distributions and hierarchical mesh fragment clustering.
    """

    @staticmethod
    def generate_uniform_sites(
        bounds: BoundingBox3D,
        count: int = 15,
        seed: int = 42,
    ) -> List[VoronoiSite]:
        """
        Distributes Voronoi seed sites uniformly across the bounding volume.
        """
        rng = random.Random(seed)
        sites: List[VoronoiSite] = []

        for i in range(count):
            px = bounds.min_x + rng.random() * (bounds.max_x - bounds.min_x)
            py = bounds.min_y + rng.random() * (bounds.max_y - bounds.min_y)
            pz = bounds.min_z + rng.random() * (bounds.max_z - bounds.min_z)

            sites.append(
                VoronoiSite(
                    site_id=f"site_u_{i}",
                    position=Vector3D(x=round(px, 3), y=round(py, 3), z=round(pz, 3)),
                    cluster_id=i,
                )
            )

        return sites

    @staticmethod
    def generate_radial_cluster_sites(
        bounds: BoundingBox3D,
        impact_point: Vector3D,
        count: int = 25,
        decay_k: float = 1.5,
        seed: int = 42,
    ) -> List[VoronoiSite]:
        """
        Generates Voronoi sites concentrated near an impact point using exponential radial decay.
        """
        rng = random.Random(seed)
        sites: List[VoronoiSite] = []

        max_radius = max(
            impact_point.distance_to(Vector3D(x=bounds.min_x, y=bounds.min_y, z=bounds.min_z)),
            impact_point.distance_to(Vector3D(x=bounds.max_x, y=bounds.max_y, z=bounds.max_z)),
        )
        max_radius = max(0.5, max_radius)

        for i in range(count):
            # Exponential radial distribution
            u = rng.random()
            # Inverse transform sampling for exponential distribution clamped to max_radius
            r = -math.log(max(1e-6, 1.0 - u * (1.0 - math.exp(-decay_k * max_radius)))) / decay_k

            # Random 3D spherical direction
            theta = rng.random() * 2.0 * math.pi
            phi = math.acos(2.0 * rng.random() - 1.0)

            dx = r * math.sin(phi) * math.cos(theta)
            dy = r * math.sin(phi) * math.sin(theta)
            dz = r * math.cos(phi)

            px = min(bounds.max_x, max(bounds.min_x, impact_point.x + dx))
            py = min(bounds.max_y, max(bounds.min_y, impact_point.y + dy))
            pz = min(bounds.max_z, max(bounds.min_z, impact_point.z + dz))

            sites.append(
                VoronoiSite(
                    site_id=f"site_rad_{i}",
                    position=Vector3D(x=round(px, 3), y=round(py, 3), z=round(pz, 3)),
                    weight=round(1.0 / (1.0 + r), 3),
                    cluster_id=i,
                )
            )

        return sites

    @staticmethod
    def partition_volume_into_pieces(
        bounds: BoundingBox3D,
        sites: List[VoronoiSite],
        impact_point: Optional[Vector3D] = None,
        micro_debris_radius_m: float = 1.0,
    ) -> List[FracturedPiece]:
        """
        Partitions the volume into hierarchical FracturedPieces based on Voronoi site proximity.
        """
        if not sites:
            # Single unfractured piece
            vol = bounds.volume()
            return [
                FracturedPiece(
                    piece_id="piece_root",
                    cluster_level=ClusterHierarchyLevel.ROOT_WHOLE,
                    centroid=bounds.center(),
                    volume_m3=round(vol, 4),
                    bounding_box=bounds,
                )
            ]

        total_vol = bounds.volume()
        base_piece_vol = total_vol / len(sites)

        pieces: List[FracturedPiece] = []

        for site in sites:
            dist_to_impact = site.position.distance_to(impact_point) if impact_point else 999.0
            is_micro = impact_point is not None and dist_to_impact <= micro_debris_radius_m

            level = ClusterHierarchyLevel.MICRO_DEBRIS if is_micro else ClusterHierarchyLevel.MACRO_CHUNK
            # Micro pieces are smaller; adjust volume share
            vol_mult = 0.4 if is_micro else 1.2
            piece_vol = base_piece_vol * vol_mult

            # Approximate local bounding box around site
            half_extent = (piece_vol ** (1.0 / 3.0)) * 0.5
            box = BoundingBox3D(
                min_x=max(bounds.min_x, site.position.x - half_extent),
                max_x=min(bounds.max_x, site.position.x + half_extent),
                min_y=max(bounds.min_y, site.position.y - half_extent),
                max_y=min(bounds.max_y, site.position.y + half_extent),
                min_z=max(bounds.min_z, site.position.z - half_extent),
                max_z=min(bounds.max_z, site.position.z + half_extent),
            )

            pieces.append(
                FracturedPiece(
                    piece_id=f"piece_{site.site_id}",
                    parent_piece_id="piece_root",
                    cluster_level=level,
                    centroid=site.position,
                    volume_m3=round(piece_vol, 4),
                    bounding_box=box,
                )
            )

        # Build contact graph: connect pieces within distance threshold
        for i in range(len(pieces)):
            for j in range(i + 1, len(pieces)):
                p_i = pieces[i]
                p_j = pieces[j]
                dist = p_i.centroid.distance_to(p_j.centroid)
                max_reach = (p_i.volume_m3 ** (1.0 / 3.0) + p_j.volume_m3 ** (1.0 / 3.0)) * 0.85

                if dist <= max_reach:
                    contact_area = round(min(p_i.volume_m3, p_j.volume_m3) ** (2.0 / 3.0), 4)
                    p_i.neighbor_piece_ids.append(p_j.piece_id)
                    p_i.contact_areas[p_j.piece_id] = contact_area
                    p_j.neighbor_piece_ids.append(p_i.piece_id)
                    p_j.contact_areas[p_i.piece_id] = contact_area

        return pieces
