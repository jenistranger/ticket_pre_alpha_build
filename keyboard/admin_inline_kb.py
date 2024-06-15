from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData, CallbackQuery 


class ChangeCurrentSets(CallbackData, prefix='ccs'):
    foo: str
    # bar: int


def change_current_task():
    builder = InlineKeyboardBuilder()

    builder.button(text="Изменить название", callback_data=ChangeCurrentSets(foo="current_name"))
    builder.button(text="Изменить ссылку", callback_data=ChangeCurrentSets(foo="current_link"))
    builder.button(text="Изменить описание", callback_data=ChangeCurrentSets(foo="current_desc"))
    builder.button(text="Изменить награду", callback_data=ChangeCurrentSets(foo="current_reward"))
    builder.button(text="Подвердить таск", callback_data=ChangeCurrentSets(foo="submit"))
    builder.adjust(1)


    return builder.as_markup()