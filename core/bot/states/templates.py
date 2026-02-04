from aiogram.fsm.state import StatesGroup, State


class TemplateFSM(StatesGroup):
    waiting_new_template = State()
