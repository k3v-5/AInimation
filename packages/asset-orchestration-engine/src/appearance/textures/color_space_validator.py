from typing import Tuple, Optional
from .texture_schema import TextureUsage, ColorSpace

class ColorSpaceValidator:
    # Regla estricta de color space por uso de textura
    USAGE_COLOR_SPACE_MAP = {
        TextureUsage.BASE_COLOR: ColorSpace.SRGB,
        TextureUsage.EMISSION: ColorSpace.SRGB,
        TextureUsage.ROUGHNESS: ColorSpace.NON_COLOR,
        TextureUsage.METALLIC: ColorSpace.NON_COLOR,
        TextureUsage.NORMAL: ColorSpace.NON_COLOR,
        TextureUsage.AO: ColorSpace.NON_COLOR,
        TextureUsage.MASK: ColorSpace.NON_COLOR,
        TextureUsage.OPACITY: ColorSpace.NON_COLOR,
    }

    @classmethod
    def validate_color_space(cls, usage: TextureUsage, color_space: ColorSpace) -> Tuple[bool, Optional[str]]:
        expected = cls.USAGE_COLOR_SPACE_MAP.get(usage)
        if expected and color_space != expected:
            return False, f"INVALID_COLOR_SPACE: Texture with usage '{usage.value}' must use '{expected.value}', but got '{color_space.value}'."
        return True, None
