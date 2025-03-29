from database.materials_lib import Material
from database.tools_lib import CuttingTool
from typing import Dict, Union

class TurningCalculator:
    @staticmethod
    def calculate(material: Material, tool: CuttingTool, operation: str, diameter: float) -> Dict[str, Union[float, str]]:
        """
        Основной метод расчета параметров токарной обработки
        Возвращает словарь с полными результатами расчета
        """
        # Рассчитываем все параметры
        cutting_speed = TurningCalculator.calculate_cutting_speed(material, tool, operation)
        feed_rate = TurningCalculator.calculate_feed_rate(material, tool, operation)
        rpm = TurningCalculator.calculate_rpm(cutting_speed, diameter)
        
        return {
            "operation": operation,
            "speed": cutting_speed,
            "feed": feed_rate,
            "rpm": rpm,
            "material": material.name,
            "tool": tool.name,
            "diameter": diameter
        }

    @staticmethod
    def calculate_cutting_speed(material: Material, tool: CuttingTool, operation_type: str) -> float:
        """Расчет скорости резания в м/мин с учетом всех факторов"""
        # Базовые коэффициенты для разных операций
        operation_factors = {
            "Наружное точение": 1.0,
            "Растачивание": 0.8,
            "Подрезание": 0.9,
            "Резьбонарезание": 0.5,
            "Отрезание": 0.7,
        }
        
        # Получаем базовую скорость для материала
        material_speed = material.recommended_speed
        if isinstance(material_speed, tuple):
            material_speed = sum(material_speed) / 2
            
        # Корректировка по материалу инструмента
        tool_factor = 1.0
        if tool.material == "Твердый сплав":
            tool_factor = 1.2
        elif tool.material == "Быстрорежущая сталь":
            tool_factor = 0.8
            
        # Корректировка по типу операции
        operation_factor = operation_factors.get(operation_type, 1.0)
        
        return round(material_speed * tool_factor * operation_factor, 1)

    @staticmethod
    def calculate_feed_rate(material: Material, tool: CuttingTool, operation_type: str) -> float:
        """Расчет подачи в мм/об с учетом всех факторов"""
        # Базовые коэффициенты для разных операций
        operation_factors = {
            "Наружное точение": 1.0,
            "Растачивание": 0.8,
            "Подрезание": 0.7,
            "Резьбонарезание": 0.3,
            "Отрезание": 0.2,
        }
        
        # Получаем базовую подачу для материала
        material_feed = material.recommended_feed
        if isinstance(material_feed, tuple):
            material_feed = sum(material_feed) / 2
            
        # Корректировка по материалу инструмента
        tool_factor = 1.0
        if tool.material == "Твердый сплав":
            tool_factor = 1.1
        elif tool.material == "Быстрорежущая сталь":
            tool_factor = 0.9
            
        # Корректировка по типу операции
        operation_factor = operation_factors.get(operation_type, 1.0)
        
        return round(material_feed * tool_factor * operation_factor, 3)

    @staticmethod
    def calculate_rpm(cutting_speed: float, diameter: float) -> int:
        """
        Расчет оборотов шпинделя в минуту
        cutting_speed: скорость резания в м/мин
        diameter: диаметр обработки в мм
        """
        if diameter <= 0:
            return 0
        return round((cutting_speed * 1000) / (3.1416 * diameter))