from aiogram.dispatcher.filters.state import StatesGroup, State


class QuizStatesGroup(StatesGroup):
    first_question = State()
    second_question = State()
    third_question = State()
    fourth_question = State()
    fifth_question = State()


class RegistrationUserStatesGroup(StatesGroup):
    name = State()
    last_name = State()
    date_of_birth = State()
    agreement = State()
