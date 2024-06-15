from aiogram import Router, Bot, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters.callback_data import CallbackData, CallbackQuery 

from keyboard.admin_reply_kb import admin_kb, skip_kb
from keyboard.admin_inline_kb import change_current_task
from keyboard.admin_inline_kb import ChangeCurrentSets

from database import set_new_task, get_tasks_for_admin, delete_row, check_active_task, set_active_task

import json

router = Router()


class AddTask(StatesGroup):
    enter_name = State()
    enter_link = State()
    enter_description = State()
    enter_reward = State()
    
    task_submit = State()
    last_one = State()

    #reworke states
    reworked_name = State()
    reworked_link = State()
    reworked_description = State()
    reworked_reward = State()

    #
    delete_task = State()
    activate_task = State()

@router.message(Command("admin"))
async def give_admin_handler(message: Message, bot: Bot) -> None:
    user_id = message.from_user.id
    member = await bot.get_chat_member(chat_id='@funticketowners', user_id=user_id)
    if member.status == "creator" or member.status == "administrator":
        await message.answer("это работает, блять, man it works", reply_markup=admin_kb())


@router.message(F.text.lower() == "просмотр тасков")
async def add_task_fsm_handler(message: Message, bot: Bot) -> None:
    user_id = message.from_user.id
    member = await bot.get_chat_member(chat_id='@funticketowners', user_id=user_id)
    if member.status == "creator" or member.status == "administrator":
        json_res = get_tasks_for_admin("tasks")
        tasks_j =  json.loads(json_res)
        plane_text = ""
        for item in tasks_j:
            plane_text += f"{item['id']}. {item['channel_name']}\nlink:{item['channel_link']}\nis_active:{item['is_active']}\nreward:{item['reward']}\n\n"
        await message.answer(f"{plane_text}")


@router.message(StateFilter(None), F.text.lower() == "добавить таск")
@router.message(StateFilter(None), Command("add_task"))
async def add_task_fsm_handler(message: Message, bot: Bot, state: FSMContext) -> None:
    user_id = message.from_user.id
    try:
        member = await bot.get_chat_member(chat_id='@funticketowners', user_id=user_id)
        if member.status == "creator" or member.status == "administrator":
            await message.answer(f"Введите название таска:")
            await state.set_state(AddTask.enter_name)
    except Exception as e:
        print("[Exception] - ", e)


@router.message(AddTask.enter_name)
async def add_name_fsm_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(task_name=message.text)
    await message.answer(f"Введите ссылку:")
    await state.set_state(AddTask.enter_link)

@router.message(AddTask.enter_link)
async def add_link_fsm_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(task_link=message.text)
    await message.answer(f"Введите описание:", reply_markup=skip_kb())
    await state.set_state(AddTask.enter_description)

@router.message(AddTask.enter_description)
async def add_description_fsm_handler(message: Message, state: FSMContext) -> None:
    if message.text.lower() == "пропустить":
        await state.update_data(task_description=None)
    else:
        await state.update_data(task_description=message.text)
    await message.answer(f"Введите награду (если пропустить, то 25 $FTK):", reply_markup=skip_kb())
    await state.set_state(AddTask.enter_reward)

@router.message(AddTask.enter_reward)
async def add_reward_fsm_handler(message: Message, state: FSMContext) -> None:
    if message.text.lower() == "пропустить":
        await state.update_data(task_reward=25)
    else:
        if message.text.isdigit():
            await state.update_data(task_reward=int(message.text))
        else:
            await message.answer(f"Неправильно введено число")
            await message.answer(f"Введите награду (если пропустить, то 25 $FTK):")
            return
    
    await message.answer(f"Предпросмотр", reply_markup=admin_kb())
    data = await state.get_data()
    await message.answer(
        f"Название: {data['task_name']}\nСсылка: {data['task_link']}\nОписание: {data['task_description']}\nНаграда: {data['task_reward']}",
        reply_markup=change_current_task(),
        )
    await state.set_state(AddTask.last_one)

@router.callback_query(AddTask.last_one, ChangeCurrentSets.filter())
async def change_current_sets_handler(callback: CallbackQuery, state: FSMContext) -> None:
    foo = callback.data.split(":")[1]
    if foo == "submit":
        await state.set_state(AddTask.task_submit)

    elif foo == "current_name":
        await state.update_data(message_id=callback.message.message_id)
        await callback.message.answer(f"Введите новое название:")
        await state.set_state(AddTask.reworked_name)
        
    elif foo == "current_link":
        await state.update_data(message_id=callback.message.message_id)
        await callback.message.answer(f"Введите новую ссылку:")
        await state.set_state(AddTask.reworked_link)

    elif foo == "current_desc":
        await state.update_data(message_id=callback.message.message_id)
        await callback.message.answer(f"Введите новое описание:")
        await state.set_state(AddTask.reworked_description)

    elif foo == "current_reward":
        await state.update_data(message_id=callback.message.message_id)
        await callback.message.answer(f"Введите новую награду:")
        await state.set_state(AddTask.reworked_reward)



@router.message(AddTask.reworked_name)
async def add_reward_fsm_handler(message: Message, state: FSMContext) -> None:

    message_name = message.text
    
    await state.update_data(task_name = message_name)
    data = await state.get_data()

    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=data["message_id"],
        text=f"Название: {data['task_name']}\nСсылка: {data['task_link']}\nОписание: {data['task_description']}\nНаграда: {data['task_reward']}",
        reply_markup=change_current_task()
    )

    await state.set_state(AddTask.last_one)


@router.message(AddTask.reworked_link)
async def add_reward_fsm_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(task_reward=int(message.text))
    data = await state.get_data()
    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=data["message_id"],
        text=f"Название: {data['task_name']}\nСсылка: {data['task_link']}\nОписание: {data['task_description']}\nНаграда: {data['task_reward']}",
        reply_markup=change_current_task()
    )
    await state.set_state(AddTask.last_one)

@router.message(AddTask.reworked_description)
async def add_reward_fsm_handler(message: Message, state: FSMContext) -> None:

    message_name = message.text
    
    await state.update_data(task_description = message_name)
    data = await state.get_data()

    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=data["message_id"],
        text=f"Название: {data['task_name']}\nСсылка: {data['task_link']}\nОписание: {data['task_description']}\nНаграда: {data['task_reward']}",
        reply_markup=change_current_task()
    )

    await state.set_state(AddTask.last_one)

@router.message(AddTask.reworked_reward)
async def add_reward_fsm_handler(message: Message, state: FSMContext) -> None:

    message_name = message.text
    
    await state.update_data(task_reward = message_name)
    data = await state.get_data()

    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=data["message_id"],
        text=f"Название: {data['task_name']}\nСсылка: {data['task_link']}\nОписание: {data['task_description']}\nНаграда: {data['task_reward']}",
        reply_markup=change_current_task()
    )

    await state.set_state(AddTask.last_one)



@router.callback_query(AddTask.task_submit, ChangeCurrentSets.filter(F.foo == 'submit'))
async def change_current_sets_handler(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    table = "tasks"
    channel_name = data["task_name"]
    channel_link = data["task_link"]
    description = data["task_description"]
    reward = int(data["task_reward"])
    set_new_task(table, channel_name, channel_link, description, reward)
    await state.clear()
    await callback.message.edit_text(
        text = "Добавлено в БД",
        )

@router.message(StateFilter(None), F.text.lower() == "удалить таск")
async def delete_task_handler(message: Message, bot: Bot, state: FSMContext) -> None:
    user_id = message.from_user.id
    member = await bot.get_chat_member(chat_id='@funticketowners', user_id=user_id)
    if member.status == "creator" or member.status == "administrator":
        await message.answer("Пиши id задания которое надо удалить:")
        await state.set_state(AddTask.delete_task)

@router.message(AddTask.delete_task)
async def delete_task_fsm_handler(message: Message, state: FSMContext) -> None:
    if message.text.isdigit():
        num = int(message.text)
        await state.clear()
        delete_row("tasks", num)
        await message.answer(f"Задание {num} удалено.", reply_markup=admin_kb())
    else:
        await message.answer(f"Нужно ввести число.")
        await message.answer("Пиши id задания которое надо удалить:")
        return
    


@router.message(StateFilter(None), F.text.contains("статус"))
async def activate_foo(message: Message, bot: Bot, state: FSMContext) -> None:
    user_id = message.from_user.id
    member = await bot.get_chat_member(chat_id='@funticketowners', user_id=user_id)
    if member.status == "creator" or member.status == "administrator":
        await message.answer("Пиши id задания которое надо активировать/деактивировать:")
        await state.set_state(AddTask.activate_task)

@router.message(AddTask.activate_task)
async def activate_task_fsm_handler(message: Message, state: FSMContext) -> None:
    if message.text.isdigit():
        num = int(message.text)
        await state.clear()
        if check_active_task("tasks", num):
            set_active_task("tasks", num, False)
        else:
            set_active_task("tasks", num, True)

        await message.answer(f"Статус задания {num} изменен.", reply_markup=admin_kb())
    else:
        await message.answer(f"Нужно ввести число.")
        await message.answer("Пиши id задания которое надо активировать/деактивировать:")
        return

