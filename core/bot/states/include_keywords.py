from aiogram.fsm.state import StatesGroup, State


class IncludeKeywordsFSM(StatesGroup):
    selecting_category = State()
    selecting_action = State()
    waiting_new_keywords = State()
    selecting_keywords_to_delete = State()
