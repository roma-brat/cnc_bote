from dataclasses import dataclass
from typing import Optional

@dataclass
class CuttingTool:
    name: str
    tool_type: str  # "turning" или "milling"
    material: str  # Материал инструмента
    diameter: Optional[float] = None  # Для фрез (в мм)
    cutting_edge_angle: Optional[float] = None  # Для токарных резцов (в градусах)

# Классификация инструмента по обрабатываемым материалам
TOOL_MATERIALS = {
    "Быстрорежущая сталь": ["Конструкционная сталь", "Легированная сталь", "Чугун"],
    "Твердый сплав": ["Конструкционная сталь", "Легированная сталь", "Нержавеющая сталь", "Чугун"],
    "Минералокерамика": ["Конструкционная сталь", "Легированная сталь"],
    "Алмаз": ["Цветные металлы", "Композиты"],
    "CBN": ["Закаленные стали", "Чугун"],
}

# Токарные инструменты
TURNING_TOOLS = {
    "Резец проходной Т5К10": CuttingTool("Резец проходной Т5К10", "turning", "Твердый сплав", cutting_edge_angle=45),
    "Резец подрезной Т15К6": CuttingTool("Резец подрезной Т15К6", "turning", "Твердый сплав", cutting_edge_angle=90),
    "Резец расточной ВК8": CuttingTool("Резец расточной ВК8", "turning", "Твердый сплав", cutting_edge_angle=60),
    "Резец резьбовой Р18": CuttingTool("Резец резьбовой Р18", "turning", "Быстрорежущая сталь", cutting_edge_angle=60),
}

# Фрезерные инструменты
MILLING_TOOLS = {
    "Фреза концевая 6мм Т5К10": CuttingTool("Фреза концевая 6мм Т5К10", "milling", "Твердый сплав", diameter=6),
    "Фреза концевая 10мм Т15К6": CuttingTool("Фреза концевая 10мм Т15К6", "milling", "Твердый сплав", diameter=10),
    "Фреза торцевая 20мм ВК8": CuttingTool("Фреза торцевая 20мм ВК8", "milling", "Твердый сплав", diameter=20),
    "Фреза червячная Р6М5": CuttingTool("Фреза червячная Р6М5", "milling", "Быстрорежущая сталь", diameter=50),
}

# Виды обработок
OPERATIONS = {
    "turning": ["Наружное точение", "Растачивание", "Подрезание", "Резьбонарезание", "Отрезание"],
    "milling": ["Торцевое фрезерование", "Контурное фрезерование", "Черновое фрезерование", "Чистовое фрезерование", "Спиральное фрезерование"],
}