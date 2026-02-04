from aiogram.fsm.state import StatesGroup, State


class ExcludeKeywordsFSM(StatesGroup):
    waiting_new_keywords = State()
    selecting_keywords_to_delete = State()
