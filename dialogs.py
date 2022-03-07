import locale
import logging
from calendar import monthcalendar
from datetime import date
from time import mktime
from typing import List

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram_dialog import DialogManager, Window, Dialog
from aiogram_dialog.widgets.kbd import Calendar
from aiogram_dialog.widgets.kbd.calendar_kbd import SCOPE_MONTHS, MONTH_PREV, MONTH_NEXT
from aiogram_dialog.widgets.text import Const

from services.handlers import MainHandler

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')


class MySG(StatesGroup):
    main = State()


async def on_date_selected(c: CallbackQuery, widget, manager: DialogManager, selected_date: date):
    logging.warning(selected_date)
    logging.warning(c.from_user)
    await manager.done()
    logging.warning(f'chat_instance {c.chat_instance}')
    handler = MainHandler(c.bot)
    await handler.save_record_date(c.from_user.values, selected_date)


class CustomCalendar(Calendar):
    def __init__(self, d_id: str, on_click, when=None):
        super().__init__(d_id, on_click, when)

    def days_kbd(self, offset) -> List[List[InlineKeyboardButton]]:
        header_week = offset.strftime("%B %Y")
        now = date.today()
        weekheader = [InlineKeyboardButton(text=dayname, callback_data=" ")
                      for dayname in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]]
        days = []
        for week in monthcalendar(offset.year, offset.month):
            week_row = []
            for day in week:
                if day == 0:
                    week_row.append(InlineKeyboardButton(text=" ",
                                                         callback_data=" "))
                elif day < now.day:
                    week_row.append(InlineKeyboardButton(text=str(day),
                                                         callback_data=" "))
                else:
                    raw_date = int(mktime(date(offset.year, offset.month, day).timetuple()))
                    week_row.append(InlineKeyboardButton(text=str(day),
                                                         callback_data=f"{self.widget_id}:{raw_date}"))
            days.append(week_row)
        return [
            [
                InlineKeyboardButton(text=header_week,
                                     callback_data=f"{self.widget_id}:{SCOPE_MONTHS}"),
            ],
            weekheader,
            *days,
            [
                InlineKeyboardButton(text="Предидущий",
                                     callback_data=f"{self.widget_id}:{MONTH_PREV}"),
                InlineKeyboardButton(text="Сдедующий",
                                     callback_data=f"{self.widget_id}:{MONTH_NEXT}"),
            ],
        ]


calendar = CustomCalendar(d_id='calendar', on_click=on_date_selected)

main_window = Window(
    Const("Привет!\n"
          "Выберите на какое число вы хотите записаться!"),
    calendar,
    state=MySG.main,
)

calendar_dialog = Dialog(main_window)
