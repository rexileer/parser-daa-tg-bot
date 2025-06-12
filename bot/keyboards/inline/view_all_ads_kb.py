from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def view_all_ads_keyboard(website_url="http://localhost:8000"):
    """
    Create an inline keyboard with a button to view all ads on the website
    """
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text="🔍 Смотреть все объявления на сайте", 
                url=website_url
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard) 