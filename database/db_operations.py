from .materials_lib import MATERIALS, MATERIAL_GROUPS, Material
from .tools_lib import TURNING_TOOLS, MILLING_TOOLS, CuttingTool

class DatabaseOperations:
    @staticmethod
    def add_material(name: str, group: str, hardness: float, 
                    tensile_strength: float, speed_range: tuple, feed_range: tuple) -> bool:
        if name in MATERIALS:
            return False
            
        MATERIALS[name] = Material(name, group, hardness, tensile_strength, speed_range, feed_range)
        
        if group not in MATERIAL_GROUPS:
            MATERIAL_GROUPS[group] = []
        MATERIAL_GROUPS[group].append(name)
        
        return True

    @staticmethod
    def add_tool(name: str, tool_type: str, tool_material: str, **kwargs) -> bool:
        if tool_type == "turning":
            if name in TURNING_TOOLS:
                return False
            TURNING_TOOLS[name] = CuttingTool(name, tool_type, tool_material, **kwargs)
        else:
            if name in MILLING_TOOLS:
                return False
            MILLING_TOOLS[name] = CuttingTool(name, tool_type, tool_material, **kwargs)
        return True