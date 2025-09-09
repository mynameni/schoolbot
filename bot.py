from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime, time

# ---------- Настройки ----------
TOKEN = "8366890929:AAHbEqoLqyQr1U8BEua7MPf6j1IquvvpGBg"  # вставь сюда токен своего бота
END_OF_DAY = time(12, 0)

schedule_raw = {
    0: ["Разговоры о важном", "химия/алгебра/история", "иностранный язык", "биология",
        "геометрия", "русский язык", "обществознание", "ОБЗР"],
    1: ["химия", "русский язык", "литература", "история",
        "биология/инф/обществ", "физика", "вероятность и статистика"],
    2: ["биология/инф/право", "литература", "история", "география",
        "обществознание", "алгебра", "геометрия"],
    3: ["Россия – мои горизонты", "химия/инф/обществ", "алгебра",
        "иностранный язык", "русский язык", "биология/геом/история", "физкультура"],
    4: ["иностранный язык", "литература", "биология/геом/право",
        "алгебра", "физкультура", "информатика", "физика"]
}
DAY_NAMES = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница",
             "Суббота", "Воскресенье"]
PROFILE = {"алгебра", "геометрия", "информатика"}

# ---------- Логика подсчета ----------
def normalize_token(token: str) -> str:
    t = token.strip().lower()
    if t.startswith("геом"):
        return "геометрия"
    if t.startswith("инф"):
        return "информатика"
    return t

def extract_profile_from_combo(lesson: str):
    if "/" not in lesson:
        return lesson
    for raw in lesson.split("/"):
        norm = normalize_token(raw)
        if norm in PROFILE:
            return norm.capitalize()
    return None

def filtered_day(day_idx: int):
    items = []
    for lesson in schedule_raw.get(day_idx, []):
        picked = extract_profile_from_combo(lesson)
        if picked is None:
            continue
        items.append(picked if "/" in lesson else lesson)
    return items

def tomorrow_idx(idx: int):
    if idx >= 4:
        return 0
    return idx + 1

def compute_lists():
    now = datetime.now()
    today_idx = now.weekday()

    base_idx = today_idx
    tmr_idx = tomorrow_idx(today_idx)

    today_lessons = filtered_day(base_idx)
    tmr_lessons = filtered_day(tmr_idx)

    remove = [x for x in today_lessons if x not in tmr_lessons]
    add = [x for x in tmr_lessons if x not in today_lessons]

    return {
        "now": now,
        "today_idx": base_idx,
        "tmr_idx": tmr_idx,
        "today_lessons": today_lessons,
        "tmr_lessons": tmr_lessons,
        "to_remove": remove,
        "to_add": add
    }

# ---------- Функции бота ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = compute_lists()
    now_txt = data["now"].strftime("%d.%m.%Y %H:%M")
    
    msg = f"Привет! Сейчас: {now_txt}\n\n"
    
    # Сегодня
    msg += f"📅 Сегодня ({DAY_NAMES[data['today_idx']]}):\n"
    for i, lesson in enumerate(data["today_lessons"], start=1):
        msg += f"{i}. {lesson}\n"
    
    # Завтра
    msg += f"\n📅 Завтра ({DAY_NAMES[data['tmr_idx']]}):\n"
    for i, lesson in enumerate(data["tmr_lessons"], start=1):
        msg += f"{i}. {lesson}\n"
    
    # Вынуть
    msg += "\n📤 Вынуть:\n"
    if data["to_remove"]:
        for i, item in enumerate(data["to_remove"], start=1):
            msg += f"{i}. {item}\n"
    else:
        msg += "Ничего\n"
    
    # Положить
    msg += "\n📥 Положить:\n"
    if data["to_add"]:
        for i, item in enumerate(data["to_add"], start=1):
            msg += f"{i}. {item}\n"
    else:
        msg += "Ничего\n"
    
    await update.message.reply_text(msg)


# ---------- Основная функция ----------
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()


