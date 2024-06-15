from aiogram.utils.keyboard import ReplyKeyboardBuilder

def admin_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text="Добавить таск")
    builder.button(text="Просмотр тасков")
    builder.button(text="Изменить статус")
    builder.button(text="Удалить таск")

    # builder.adjust(2, 1)
    builder.adjust(1)
    return builder.as_markup(
        resize_keyboard=True, 
        input_field_placeholder="Работай...",
        selective = True
    )

def skip_kb():
    skip_bld = ReplyKeyboardBuilder()
    skip_bld.button(text="Пропустить")
    return skip_bld.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Можно пропустить, но будет присвоено значение по умолчанию",
        selective = True,
        one_time_keyboard=True
    )