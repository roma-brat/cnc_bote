class MillingCalculator:
    @staticmethod
    def calculate_cutting_speed(material, tool, operation_type):
        # Базовые скорости резания в м/мин
        base_speeds = {
            "Торцевое фрезерование": 1.0,
            "Контурное фрезерование": 0.9,
            "Черновое фрезерование": 1.1,
            "Чистовое фрезерование": 0.8,
            "Спиральное фрезерование": 0.7,
        }
        
        material_speed = material.recommended_speed
        if isinstance(material_speed, tuple):
            material_speed = sum(material_speed) / 2
            
        tool_factor = 1.0
        if tool.material == "Твердый сплав":
            tool_factor = 1.3
        elif tool.material == "Быстрорежущая сталь":
            tool_factor = 0.7
            
        operation_factor = base_speeds.get(operation_type, 1.0)
        
        return material_speed * tool_factor * operation_factor

    @staticmethod
    def calculate_feed_per_tooth(material, tool, operation_type):
        # Базовые подачи на зуб в мм/зуб
        base_feeds = {
            "Торцевое фрезерование": 0.1,
            "Контурное фрезерование": 0.08,
            "Черновое фрезерование": 0.15,
            "Чистовое фрезерование": 0.05,
            "Спиральное фрезерование": 0.07,
        }
        
        material_feed = material.recommended_feed
        if isinstance(material_feed, tuple):
            material_feed = sum(material_feed) / 2
            
        tool_factor = 1.0
        if tool.material == "Твердый сплав":
            tool_factor = 1.2
        elif tool.material == "Быстрорежущая сталь":
            tool_factor = 0.8
            
        operation_factor = base_feeds.get(operation_type, 1.0)
        
        return material_feed * tool_factor * operation_factor

    @staticmethod
    def calculate_rpm(cutting_speed, diameter):
        """Расчет оборотов в минуту для фрезы"""
        if diameter == 0:
            return 0
        return (cutting_speed * 1000) / (3.1416 * diameter)

    @staticmethod
    def calculate_feed_rate(feed_per_tooth, num_teeth, rpm):
        """Расчет минутной подачи в мм/мин"""
        return feed_per_tooth * num_teeth * rpm

    @staticmethod
    def calculate_helical_milling(
        tool_diameter: float,
        tool_type: str,
        material: str,
        cutting_depth: float,
        operation: str = "Спиральное фрезерование"
    ) -> dict:
        """
        Расчет параметров спирального фрезерования
        :param tool_diameter: диаметр фрезы (мм)
        :param tool_type: тип фрезы (торцевая, концевая и т.д.)
        :param material: обрабатываемый материал
        :param cutting_depth: глубина резания (мм)
        :param operation: тип операции
        :return: словарь с параметрами
        """
         # Базовые коэффициенты для разных материалов
        MATERIAL_COEFFICIENTS = {
            "Алюминий": {"step_over": 0.4, "plunge_factor": 0.3, "helix_angle": 30},
            "Сталь": {"step_over": 0.25, "plunge_factor": 0.2, "helix_angle": 15},
            "Нержавеющая сталь": {"step_over": 0.2, "plunge_factor": 0.15, "helix_angle": 10},
            "Титан": {"step_over": 0.15, "plunge_factor": 0.1, "helix_angle": 7}
        }

        # Определение коэффициентов по материалу
        coeff = MATERIAL_COEFFICIENTS.get(material, MATERIAL_COEFFICIENTS["Сталь"])

        # Расчет основных параметров
        step_over = tool_diameter * coeff["step_over"]  # Шаг между проходами
        max_plunge = tool_diameter * coeff["plunge_factor"]  # Макс. вертикальная подача
    
        # Рекомендуемый угол спирали (градусы)
        helix_angle = coeff["helix_angle"]
    
        # Расчет скорости подачи при спиральном врезании
        if tool_type == "Торцевая фреза":
            plunge_rate = max_plunge * 0.7  # Более агрессивная подача
        else:
            plunge_rate = max_plunge * 0.5  # Консервативная подача для концевых фрез

        # Коррекция для глубокого резания
        if cutting_depth > 3 * tool_diameter:
            plunge_rate *= 0.7
            step_over *= 0.8

        return {
            "operation": operation,
            "step_over": round(step_over, 2),
            "max_plunge_rate": round(plunge_rate, 2),
            "recommended_helix_angle": helix_angle,
            "tool_diameter": tool_diameter,
            "material": material,
            "notes": [
                f"Угол спирали: {helix_angle}°",
                "Используйте охлаждение СОЖ",
                "Рекомендуется чистовой проход"
            ]
        }