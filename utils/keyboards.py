from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from database.materials_lib import MATERIAL_GROUPS
from database.tools_lib import OPERATIONS, TURNING_TOOLS, MILLING_TOOLS

class Keyboards:
    @staticmethod
    def _create_markup(buttons: list, row_width: int = 2) -> ReplyKeyboardMarkup:
        """Создает клавиатуру с заданными кнопками"""
        markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=row_width)
        markup.add(*[KeyboardButton(btn) for btn in buttons])
        return markup

    @staticmethod
    def main_menu() -> ReplyKeyboardMarkup:
        """Главное меню"""
        buttons = ["Токарная обработка", "Фрезерная обработка"]
        return Keyboards._create_markup(buttons)

    @staticmethod
    def operations_menu(process_type: str) -> ReplyKeyboardMarkup:
        """Меню операций для токарной/фрезерной обработки"""
        buttons = OPERATIONS[process_type] + ["Назад"]
        return Keyboards._create_markup(buttons, row_width=1)

    @staticmethod
    def material_groups() -> ReplyKeyboardMarkup:
        """Список групп материалов"""
        buttons = list(MATERIAL_GROUPS.keys()) + ["Назад"]
        return Keyboards._create_markup(buttons, row_width=2)

    @staticmethod
    def materials_from_group(group: str) -> ReplyKeyboardMarkup:
        """Список материалов в группе"""
        buttons = MATERIAL_GROUPS[group] + ["Назад"]
        return Keyboards._create_markup(buttons, row_width=2)

    @staticmethod
    def tools_menu(process_type: str) -> ReplyKeyboardMarkup:
        """Список инструментов для типа обработки"""
        tools = list(TURNING_TOOLS.keys()) if process_type == "turning" else list(MILLING_TOOLS.keys())
        buttons = tools + ["Назад"]
        return Keyboards._create_markup(buttons, row_width=1)

    @staticmethod
    def yes_no_keyboard() -> ReplyKeyboardMarkup:
        """Клавиатура Да/Нет"""
        return Keyboards._create_markup(["Да", "Нет"], row_width=2)