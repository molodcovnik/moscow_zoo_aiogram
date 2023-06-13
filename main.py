from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

import keyboards
import sqlite_db

from config import TOKEN
from keyboards import ikb_start, get_ikb_for_answer
from states import QuizStatesGroup, RegistrationUserStatesGroup

storage = MemoryStorage()

bot = Bot(TOKEN)
dp = Dispatcher(bot=bot, storage=storage)


async def on_startup(_):
    await sqlite_db.db_zoo_connect()
    print('Соединение с базой данных успешно установлено!')


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text='Привет от бота зоопарка!\n Давай узнаем какой ты зверь!',
                           reply_markup=keyboards.ikb_start)


@dp.callback_query_handler(lambda c: c.data == 'stop', state='*')
async def cancel_states(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await state.finish()
    await bot.send_message(callback_query.from_user.id, 'Вы отменили прохождение теста!')


@dp.callback_query_handler(lambda c: c.data == 'stop_reg', state='*')
async def cancel_states_for_registration(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await state.finish()
    with open('media/MZoo-logo.jpg', 'rb') as photo:
        await bot.send_photo(chat_id=callback_query.from_user.id,
                             photo=photo,
                             caption="""Вы остановили процесс регистрации!
        \nА зря, ведь тогда бы Вы смогли учавствовать во всех разыгрышах нашего зоопарка, и иметь возможность выигрывать крутые призы...""")


@dp.callback_query_handler(lambda c: c.data.startswith('play'))
async def process_callback_start_quiz(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await QuizStatesGroup.first_question.set()
    i = 1
    question = await sqlite_db.get_questions(i)
    kb = await get_ikb_for_answer(i)
    await callback_query.message.answer(text=question, reply_markup=kb)


# Добавить адрес сделать все красиво
@dp.callback_query_handler(lambda c: c.data.startswith('contacts'))
async def get_contacts(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.answer(text='Для связи по опеке:'
                                             '\n+7(958) 813-15-60'
                                             '\na.sharapova@moscowzoo.ru',
                                        reply_markup=keyboards.ikb_contacts)

@dp.callback_query_handler(lambda c: c.data.startswith('guardianship'))
async def get_info_about_guardianship_program(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)


    text = """Программа «Возьми животное под опеку» дает возможность опекунам ощутить свою причастность к делу сохранения природы, участвовать в жизни Московского зоопарка и его обитателей, видеть конкретные результаты своей деятельности. Опекать – значит помогать любимым животным.
    
    В настоящее время опекуны объединились в неформальное сообщество — Клуб друзей Московского зоопарка.
    \n5 уровней участия в программе:
    \n1. Индивидуальный (пожертвование до 50 тыс. рублей в год)
    \n2. Партнерский (пожертвование от 50 до 150 тыс. рублей в год)
    \n3. Представительский (пожертвование от 150 до 300 тыс. рублей в год)
    \n4. Почетный (пожертвование от 300 тыс. до 1 млн. рублей в год)
    \n5. Президентский (пожертвование от 1 млн. рублей в год и более)
    \nКак выбрать животное? Можете пройти наш тест или изучить наш сайт.
    \nСтоимость опеки рассчитывается из ежедневного рациона питания животного.
    \nЕсли вы уже выбрали животное и хотите узнать стоимость опеки над ним, вам нужно отправить свой запрос на почту, позвонить по телефонам или оставить заявку на сайте."""

    await callback_query.message.answer(text=text,
                                        reply_markup=keyboards.ikb_guardianship)


@dp.callback_query_handler(lambda c: c.data.startswith('account'))
async def get_account(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    uid = callback_query.from_user.id
    check = await sqlite_db.check_user_on_reg(uid)
    if check:
        user_data = await sqlite_db.get_user_data(uid)
        name = user_data[0]
        last_name = user_data[1]
        try:
            date_of_birth = user_data[2].split('-')
            day_b = f'{date_of_birth[2]}-{date_of_birth[1]}-{date_of_birth[0]}'
        except Exception:
            day_b = user_data[2]

        check_zoo = await sqlite_db.check_result_test(uid)
        if check_zoo[0] >= 1:
            z = await sqlite_db.get_animal(uid)
            zoo = z[0]
        else:
            zoo = 'тест еще не пройден'
        await callback_query.message.answer(f"""<b>Аккаунт</b>
                                            \nИмя: {name}
                                            \nФамилия: {last_name}
                                            \nДата рождения: {day_b}
                                            \n<b>Результат теста:</b> {zoo}""",
                                            parse_mode='HTML',
                                            reply_markup=keyboards.ikb_reset_result)
    else:
        await callback_query.message.answer(f'Вы еще не зарегистрированы...')


@dp.callback_query_handler(lambda c: c.data.startswith('reg'))
async def process_callback_start_registration_user(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    uid = callback_query.from_user.id
    check = await sqlite_db.check_user_on_reg(uid)
    if check:
        await callback_query.message.answer('Вы уже зарегистрированны',
                                            reply_markup=keyboards.ikb_start)
    else:
        await callback_query.message.answer(text='Как Вас зовут?', reply_markup=keyboards.ikb_stop_reg)
        await RegistrationUserStatesGroup.name.set()


@dp.message_handler(state=RegistrationUserStatesGroup.name)
async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await RegistrationUserStatesGroup.next()
    await message.reply("Введите вашу фамилию.", reply_markup=keyboards.ikb_stop_reg)

@dp.message_handler(state=RegistrationUserStatesGroup.last_name)
async def load_last_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['last_name'] = message.text

    await RegistrationUserStatesGroup.next()
    await message.reply('Ваша дата рождения\nв формате "01-01-2000"', reply_markup=keyboards.ikb_stop_reg)

@dp.message_handler(state=RegistrationUserStatesGroup.date_of_birth)
async def load_last_name(message: types.Message, state: FSMContext):
    value = message.text
    if value[:2].isnumeric():
        async with state.proxy() as data:
            data['date_of_birth'] = message.text

        await RegistrationUserStatesGroup.next()
        await message.answer("Согласие на обработку Ваших персональных данных?", reply_markup=keyboards.ikb_agree)
    else:
        await message.reply('Введите дату')


@dp.callback_query_handler(state=RegistrationUserStatesGroup.agreement)
async def load_agreement(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        data['agree'] = callback_query.data
    if data['agree'] == 'agree':
        uid = callback_query.from_user.id
        user_name = callback_query.from_user.username
        name = data['name']
        last_name = data['last_name']
        date_of_birth = data['date_of_birth']
        agreement = data['agree']
        try:
            await sqlite_db.registration_user(uid, user_name, name, last_name, date_of_birth, agreement)
            with open('media/MZoo-logo.jpg', 'rb') as photo:
                await bot.send_photo(chat_id=callback_query.from_user.id,
                                     photo=photo,
                                     caption=f'<b>{data["name"]}, Добро пожаловать в Наш Зоопарк!</b>\nВы успешно зарегистрировались в нашем боте!',
                                     parse_mode='HTML',
                                     reply_markup=keyboards.ikb_after_reg)
        except Exception as e:
            print(e)
            await bot.send_message(chat_id=callback_query.from_user.id,
                                   text='Вы уже зарегистрированны в боте',
                                   reply_markup=keyboards.ikb_play_quiz)
        finally:
            await state.finish()
    else:
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text='Вы не завершили регистрацию')
        await state.finish()


@dp.callback_query_handler(state=QuizStatesGroup.first_question)
async def load_first_question(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        data['first_answer'] = callback_query.data
    print(data['first_answer'])
    await QuizStatesGroup.next()
    i = 2
    question = await sqlite_db.get_questions(i)
    kb = await get_ikb_for_answer(i)
    await callback_query.message.answer(text=question, reply_markup=kb)

@dp.message_handler(state=QuizStatesGroup.all_states)
async def first_test_state_case_met(message: types.Message):
    await message.reply('Выберете из предложенных вариантов', reply=False)


@dp.callback_query_handler(state=QuizStatesGroup.second_question)
async def load_second_question(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        data['second_answer'] = callback_query.data
    print(data['second_answer'])
    await QuizStatesGroup.next()
    i = 3
    question = await sqlite_db.get_questions(i)
    kb = await get_ikb_for_answer(i)
    await callback_query.message.answer(text=question, reply_markup=kb)


@dp.callback_query_handler(state=QuizStatesGroup.third_question)
async def load_third_question(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        data['third_answer'] = callback_query.data
    print(data['third_answer'])
    await QuizStatesGroup.next()
    i = 4
    question = await sqlite_db.get_questions(i)
    kb = await get_ikb_for_answer(i)
    await callback_query.message.answer(text=question, reply_markup=kb)

@dp.callback_query_handler(state=QuizStatesGroup.fourth_question)
async def load_fourth_question(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        data['fourth_answer'] = callback_query.data

    await QuizStatesGroup.next()
    i = 5
    question = await sqlite_db.get_questions(i)
    kb = await get_ikb_for_answer(i)
    await callback_query.message.answer(text=question, reply_markup=kb)

@dp.callback_query_handler(state=QuizStatesGroup.fifth_question)
async def load_fifth_question(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    async with state.proxy() as data:
        data['fifth_answer'] = callback_query.data

    user_id = callback_query.from_user.id
    a_id_1 = data['first_answer']
    a_id_2 = data['second_answer']
    a_id_3 = data['third_answer']
    a_id_4 = data['fourth_answer']
    a_id_5 = data['fifth_answer']
    try:
        await sqlite_db.registration_user_answers(user_id, a_id_1, a_id_2, a_id_3, a_id_4, a_id_5)
        await state.finish()
        await callback_query.message.answer('Вы успешно прошли тест',
                                            reply_markup=keyboards.ikb_results)
    except Exception as e:
        print(e)
        await state.finish()
        await callback_query.message.answer('Вы уже проходили тест. Для того чтобы сбросить результат, зарегистрируйтесь!',
                                            reply_markup=keyboards.ikb_start)


@dp.callback_query_handler(lambda c: c.data.startswith('reset_result'))
async def reset_result(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    uid = callback_query.from_user.id
    check = await sqlite_db.check_user_on_reg(uid)
    if check:
        await sqlite_db.reset_result(uid)
        await callback_query.message.answer(text='Результат сброшен.\nМожете пройти тест еще раз',
                                            reply_markup=keyboards.ikb_play_quiz)
    else:
        await sqlite_db.reset_result_for_nonauth(uid)
        await callback_query.message.answer(text='Результат сброшен.\nМожете пройти тест еще раз',
                                            reply_markup=keyboards.ikb_play_quiz)


@dp.callback_query_handler(lambda c: c.data.startswith('get_results'))
async def get_results(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    uid = callback_query.from_user.id
    result = await sqlite_db.get_results(uid)
    id_animal = result[2]
    text = result[0]
    photo = result[1]
    await bot.send_photo(chat_id=uid,
                         caption=f'Кажется, Ваш тотэмный зверь это - <b>{text}!</b>',
                         photo=f'{photo}',
                         parse_mode='HTML',
                         reply_markup=keyboards.ikb_reset_result)

    await callback_query.message.answer(f"""Кстати, Вы можете взять его себе под опеку.\n<b>{text}</b> ждет Вас!""",
                                        reply_markup=keyboards.ikb_guardianship_program,
                                        parse_mode='HTML')


@dp.message_handler(commands=['animals'])
async def get_animal(message: types.Message):
    text = sqlite_db.get_animals()[0][0]
    img = sqlite_db.get_animals()[0][1]
    await bot.send_photo(chat_id=message.from_user.id,
                         photo=img,
                         caption=f'<b>{text}</b>',
                         parse_mode='HTML')


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp,
                           skip_updates=True,
                           on_startup=on_startup)
