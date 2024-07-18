from data.repositories.productRepository import ProductRepository
from service.telegramService import TelegramService


class AppOptions:
    def __init__(self,url):
        self.product_repo = ProductRepository()
        self.telegram_service = TelegramService(bot_token='7393980187:AAGJHwoW6DY98jZOvTzdq0o7Ojt8X1VO28Q', chat_id='-1002203530212')
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'X-Client-Id': 'MoriaDesktop',
            'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            'Origin': 'https://www.hepsiburada.com'
        }