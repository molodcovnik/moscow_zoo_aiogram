from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import sqlite_db

ikb_start = InlineKeyboardMarkup(row_width=2)
ib_reg = InlineKeyboardButton(text='Регистрация в боте',
                              callback_data='reg')

ib_play = InlineKeyboardButton(text='Пройти тест',
                               callback_data='play')

ib_contacts = InlineKeyboardButton(text='Наши контакты',
                                   callback_data='contacts')

ib_account = InlineKeyboardButton(text='Ваш профиль',
                                   callback_data='account')

ikb_after_reg = InlineKeyboardMarkup(row_width=2).add(ib_play, ib_account, ib_contacts)

ib_site = InlineKeyboardButton(text='Сайт зоопарка',
                                url='https://moscowzoo.ru/')

ikb_contacts = InlineKeyboardMarkup().add(ib_site)

ikb_guardianship = InlineKeyboardMarkup().add(ib_contacts)

ikb_account = InlineKeyboardMarkup().add(ib_account)

ikb_agree = InlineKeyboardMarkup(row_width=2)

ib_agree = InlineKeyboardButton(text='Согласен',
                                callback_data='agree')

ib_disagree = InlineKeyboardButton(text='Не согласен',
                                   callback_data='disagree')

ikb_agree.add(ib_agree, ib_disagree)

ikb_play_quiz = InlineKeyboardMarkup().add(InlineKeyboardButton(text='Пройти тест',
                                                                callback_data='play'))

ikb_stop_reg = InlineKeyboardMarkup().add(InlineKeyboardButton(text='Остановить',
                                                               callback_data='stop_reg'))


ikb_reset_result = InlineKeyboardMarkup().add(InlineKeyboardButton(text='Сбросить результат',
                                                                   callback_data='reset_result'))

ikb_results = InlineKeyboardMarkup().add(InlineKeyboardButton(text='Показать результат',
                                                              callback_data='get_results'))

ib_guardianship_program = InlineKeyboardButton(text='Программа опеки',
                                               callback_data='guardianship')

ikb_guardianship_program = InlineKeyboardMarkup().add(ib_guardianship_program)

ikb_start.add(ib_play, ib_reg, ib_contacts, ib_account, ib_guardianship_program)

async def get_ikb_for_answer(i):
    values = await sqlite_db.get_ikb_for_answer(i)
    ikb = InlineKeyboardMarkup(row_width=1)

    for value in values:
        ikb.add(InlineKeyboardButton(text=f'{value[1]}', callback_data=f'{value[0]}'))
    ikb.add(InlineKeyboardButton(text='Остановить', callback_data='stop'))
    return ikb
