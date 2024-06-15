from aiogram import Bot, Router, html, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.filters.callback_data import CallbackData, CallbackQuery 

from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import table_name_dev as table_name
from database import user_exists, set_new_user, get_referral_count, get_balance, give_coins
from database import get_tasks_for_admin, count_of_active_task, get_user_completed_info, get_user_all_tasks_from_complete, set_user_completed_info
from database import get_parsed_link
from config import bot_name

from keyboard.user_reply import user_main_kb

import json


router = Router()


class SubsCheck(CallbackData, prefix='sub'):
    action: str

@router.message(CommandStart())
async def command_start_handler(message: Message, bot: Bot) -> None:
    commandf, *args = message.text.split()
    #добавить проверка на существующего юзера
    if args:
        if int(args[0]) == message.from_user.id:
            await message.answer(f"sorry, but you can't invite yourself.", reply_markup=user_main_kb())
        else:
            if user_exists(table_name, message.from_user.id):
                await message.answer(f"you are already registered.", reply_markup=user_main_kb())
            else:
                set_new_user(table_name, message.from_user.id, args[0])
                give_coins(table_name, int(args[0]), 50)
                await message.answer(f"you can say thank you to the kind person who shared this link with you, because it gave you 100 $FTK", reply_markup=user_main_kb())
                await bot.send_message(int(args[0]), "congratulations, you have a new referral! you received 50 $FTK for it.")
    else:
        if user_exists(table_name, message.from_user.id):
            await message.answer(f"you are already registered.", reply_markup=user_main_kb())
        else:
            set_new_user(table_name, message.from_user.id)
            await message.answer(f"cool, now you're with us! Keep 50 $FTK.", reply_markup=user_main_kb())
#заменить канал


@router.message(F.text.lower() == "referrals")
# @router.message(Command("referrals"))
async def message_handler(message: Message) -> None:
    total_refs = get_referral_count(table_name, message.from_user.id)
    await message.answer(f"total referrals: {total_refs}.\nyour referral link:\n{html.code(str(bot_name) + "?start=" + str(message.from_user.id))}")


@router.message(F.text.lower() == "balance")
# @router.message(Command("balance"))
async def message_handler(message: Message) -> None:
    await message.answer(f"your balance: {get_balance(table_name, message.from_user.id)} $FTK")


def make_inline_update_kb(tasks_act, tasks_done):
    builder = InlineKeyboardBuilder()
    for item in tasks_act:
        if item['is_active'] == True:

            builder.button(text=item['channel_name'], url=item['channel_link'])
    builder.button(text="update", callback_data=SubsCheck(action="update"))
    builder.adjust(1)
    return builder.as_markup()


@router.message(F.text.lower() == "tasks")
@router.message(Command("show_tasks"))
async def message_handler(message: Message) -> None:
    
    json_res = get_tasks_for_admin("tasks")
    tasks_j = json.loads(json_res)
    num = count_of_active_task("tasks")
    if num != 0:
        
        builder = InlineKeyboardBuilder()
        for item in tasks_j:
            if item['is_active'] == True:
                builder.button(text=item['channel_name'], url=item['channel_link'])
        builder.button(text="update", callback_data=SubsCheck(action="update"))
        builder.adjust(1)
        await message.answer("available tasks:", reply_markup=builder.as_markup())
    else:
        await message.answer("no active tasks")

# @router.callback_query(SubsCheck.filter())
# async def callbacks_num_change_fab(
#         callback: CallbackQuery, 
#         callback_data: SubsCheck
#     ) -> None:
#     await callback.message.answer(f"you chose {callback_data.action}")

#     await callback.answer()
@router.callback_query(SubsCheck.filter(F.action == "update"))
async def callbacks_num_change_fab(
        callback: CallbackQuery, 
        callback_data: SubsCheck
    ) -> None:
    # Initialize the keyboard builder
    builder = InlineKeyboardBuilder()

    try:
        # Fetch and parse the tasks and user task info
        json_res = get_tasks_for_admin("tasks")
        tasks_j = json.loads(json_res)
        user_task_info = get_user_all_tasks_from_complete("task_completion", callback.from_user.id)
        user_tasks_all = json.loads(user_task_info)
    except Exception as e:
        await callback.message.answer(f"Error: {e}")
        return

    # If user_tasks_all is empty or None, initialize it as an empty list
    if not user_tasks_all:
        user_tasks_all = []

    user_task_ids = {task['task_id'] for task in user_tasks_all if task['completed']}

    for item in tasks_j:
        if item['is_active']:
            link_to_parse = get_parsed_link("tasks", item['id'])
            member_chal = await callback.bot.get_chat_member(chat_id=link_to_parse, user_id=callback.from_user.id)

            if item['id'] in user_task_ids:
                builder.button(text=f"{item['channel_name']} ✅", url=item['channel_link'])
            elif member_chal.status != "left":
                set_user_completed_info("task_completion", callback.from_user.id, item['id'], True)
                give_coins(table_name, callback.from_user.id, item['reward'])
                builder.button(text=f"{item['channel_name']} ✅", url=item['channel_link'])
            else:
                builder.button(text=f"{item['channel_name']} 🚫", url=item['channel_link'])

    # Add the update button
    builder.button(text="update", callback_data=SubsCheck(action="update"))
    builder.adjust(1)

    # Update the reply markup
    await callback.message.edit_reply_markup(reply_markup=builder.as_markup())
    await callback.answer()
  