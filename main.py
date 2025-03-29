import telebot
from telebot import types
import logging
from config import BOT_TOKEN, ADMIN_CHAT_ID
from database.materials_lib import MATERIALS, MATERIAL_GROUPS
from database.tools_lib import TURNING_TOOLS, MILLING_TOOLS, OPERATIONS
from calculations.turning_calc import TurningCalculator
from calculations.milling_calc import MillingCalculator
from utils.keyboards import Keyboards


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(BOT_TOKEN)

class UserState:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.process_type = None  # turning/milling
        self.operation = None
        self.material = None
        self.tool = None
        self.calculator = None
        self.awaiting_input = None  # diameter/teeth/etc

user_states = {}

def get_user_state(user_id):
    if user_id not in user_states:
        user_states[user_id] = UserState()
    return user_states[user_id]

# Форматирование результатов
def format_turning_result(result):
    return (
        f"⚙️ *Результаты токарной обработки:*\n\n"
        f"🔧 Операция: {result['operation']}\n"
        f"📏 Материал: {result['material']}\n"
        f"🛠 Инструмент: {result['tool']}\n"
        f"📐 Диаметр: {result['diameter']} мм\n\n"
        f"⚡ *Параметры:*\n"
        f"- Скорость резания: {result['speed']} м/мин\n"
        f"- Подача: {result['feed']} мм/об\n"
        f"- Обороты: {result['rpm']} об/мин\n\n"
        f"💡 *Рекомендации:*\n"
        f"• Используйте СОЖ для охлаждения\n"
        f"• Для чистовой обработки уменьшите подачу на 20%"
    )

def format_milling_result(result):
    response = (
        f"⚙️ *Результаты фрезерования:*\n\n"
        f"🔧 Операция: {result['operation']}\n"
        f"📏 Материал: {result['material']}\n"
        f"🛠 Инструмент: {result['tool']}\n"
        f"📐 Диаметр фрезы: {result['diameter']} мм\n"
        f"🦷 Зубьев: {result['teeth']}\n\n"
        f"⚡ *Параметры:*\n"
        f"- Скорость: {result['speed']} м/мин\n"
        f"- Подача на зуб: {result['feed_per_tooth']} мм/зуб\n"
        f"- Обороты: {result['rpm']} об/мин\n"
        f"- Минутная подача: {result['feed_rate']} мм/мин\n"
    )
    
    if result['operation'] == "Спиральное фрезерование":
        response += (
            f"\n🌀 *Параметры спирали:*\n"
            f"- Шаг между проходами: {result['step_over']} мм\n"
            f"- Вертикальная подача: {result['plunge_rate']} мм/мин\n"
            f"- Глубина резания: {result['cutting_depth']} мм\n"
            f"\n💡 *Рекомендации:*\n"
            f"• Используйте компрессионные фрезы\n"
            f"• Начинайте с 70% от расчетной подачи"
        )
    return response

# Обработчики сообщений
@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    user = get_user_state(message.from_user.id)
    user.reset()
    bot.send_message(message.chat.id,
                   "🔧 *CNC Cutting Bot*\nВыберите тип обработки:",
                   reply_markup=Keyboards.main_menu(),
                   parse_mode='Markdown')

@bot.message_handler(func=lambda msg: msg.text in ["Токарная обработка", "Фрезерная обработка"])
def handle_process_type(message):
    user = get_user_state(message.from_user.id)
    user.process_type = "turning" if message.text == "Токарная обработка" else "milling"
    user.calculator = TurningCalculator() if user.process_type == "turning" else MillingCalculator()
    
    bot.send_message(message.chat.id,
                   f"Выберите операцию:",
                   reply_markup=Keyboards.operations_menu(user.process_type))

@bot.message_handler(func=lambda msg: msg.text in OPERATIONS['turning'] + OPERATIONS['milling'])
def handle_operation(message):
    user = get_user_state(message.from_user.id)
    user.operation = message.text
    bot.send_message(message.chat.id,
                   "Выберите группу материала:",
                   reply_markup=Keyboards.material_groups())

@bot.message_handler(func=lambda msg: msg.text in MATERIAL_GROUPS.keys())
def handle_material_group(message):
    user = get_user_state(message.from_user.id)
    user.material_group = message.text
    bot.send_message(message.chat.id,
                   "Выберите материал:",
                   reply_markup=Keyboards.materials_from_group(message.text))

@bot.message_handler(func=lambda msg: msg.text in MATERIALS.keys())
def handle_material(message):
    user = get_user_state(message.from_user.id)
    user.material = MATERIALS[message.text]
    bot.send_message(message.chat.id,
                   "Выберите инструмент:",
                   reply_markup=Keyboards.tools_menu(user.process_type))

# Токарная обработка
@bot.message_handler(func=lambda msg: msg.text in TURNING_TOOLS.keys())
def handle_turning_tool(message):
    user = get_user_state(message.from_user.id)
    user.tool = TURNING_TOOLS[message.text]
    user.awaiting_input = "turning_diameter"
    bot.send_message(message.chat.id,
                   "Введите диаметр обработки в мм:",
                   reply_markup=types.ReplyKeyboardRemove())
    
    

# Фрезерная обработка
@bot.message_handler(func=lambda msg: msg.text in MILLING_TOOLS.keys())
def handle_milling_tool(message):
    user = get_user_state(message.from_user.id)
    user.tool = MILLING_TOOLS[message.text]
    
    if user.operation == "Спиральное фрезерование":
        user.awaiting_input = "spiral_params"
        text = ("🌀 *Спиральное фрезерование*\n"
                "Введите параметры через пробел:\n"
                "<Диаметр фрезы> <Зубья> <Глубина>\n"
                "Пример: 12 4 20")
    else:
        user.awaiting_input = "milling_params"
        text = ("Введите параметры через пробел:\n"
                "<Диаметр фрезы> <Зубья>\n"
                "Пример: 12 4")
    
    bot.send_message(message.chat.id,
                   text,
                   reply_markup=types.ReplyKeyboardRemove(),
                   parse_mode='Markdown')

@bot.message_handler(func=lambda msg: True)
def handle_input(message):
    user = get_user_state(message.from_user.id)
    
    try:
        if user.awaiting_input == "turning_diameter":
            diameter = float(message.text)
            result = user.calculator.calculate(
                material=user.material,
                tool=user.tool,
                operation=user.operation,
                diameter=diameter
            )
            response = format_turning_result({
                **result,
                "material": user.material.name,
                "tool": user.tool.name,
                "diameter": diameter
            })
            user.reset()
            
        elif user.awaiting_input == "milling_params":
            diameter, teeth = map(float, message.text.split())
            result = user.calculator.calculate(
                material=user.material,
                tool=user.tool,
                operation=user.operation,
                diameter=diameter,
                teeth=int(teeth)
            )
            response = format_milling_result({
                **result,
                "material": user.material.name,
                "tool": user.tool.name,
                "diameter": diameter,
                "teeth": int(teeth)
            })
            user.reset()
            
        elif user.awaiting_input == "spiral_params":
            diameter, teeth, depth = map(float, message.text.split())
            result = user.calculator.calculate(
                material=user.material,
                tool=user.tool,
                operation=user.operation,
                diameter=diameter,
                teeth=int(teeth),
                cutting_depth=depth
            )
            response = format_milling_result({
                **result,
                "material": user.material.name,
                "tool": user.tool.name,
                "diameter": diameter,
                "teeth": int(teeth),
                "cutting_depth": depth
            })
            user.reset()
            
        else:
            raise ValueError("Неизвестный ввод")
            
        bot.send_message(message.chat.id,
                       response,
                       reply_markup=Keyboards.main_menu(),
                       parse_mode='Markdown')
        
    except ValueError as e:
        logger.error(f"Ошибка ввода: {str(e)}")
        error_text = {
            "turning_diameter": "Введите число для диаметра (например: 50.5)",
            "milling_params": "Введите два числа через пробел (например: 12 4)",
            "spiral_params": "Введите три числа через пробел (например: 12 4 20)"
        }.get(user.awaiting_input, "Неверный формат ввода")
        
        bot.send_message(message.chat.id,
                       f"❌ Ошибка! {error_text}",
                       reply_markup=Keyboards.main_menu())
        
    except Exception as e:
        logger.error(f"Системная ошибка: {str(e)}")
        bot.send_message(message.chat.id,
                       "⚠️ Произошла внутренняя ошибка. Попробуйте снова.",
                       reply_markup=Keyboards.main_menu())

if __name__ == "__main__":
    logger.info(" 🤖 Бот запущен...")

    try:
        #Отправляем сообщение при запуске
        bot.send_message(
            ADMIN_CHAT_ID,
            "🤖 Бот успешно запущен и готов к работе!\n"
            "Используйте /start для начала работы.",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f'Ошибка отправки стартового сообщения: {e}')

    bot.polling(none_stop=True)

    