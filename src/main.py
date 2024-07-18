import asyncio
from decimal import Decimal
import re

from bs4 import BeautifulSoup

from data.appOptions import AppOptions
from data.entities.product import Product
from data.repositories.productRepository import ProductRepository
from service.telegramService import TelegramService

import requests

async def getPriceDecimal(priceText):
        numeric_str = re.sub(r'[^\d,]', '', priceText)
        numeric_str = numeric_str.replace(',', '.')
        price_decimal = Decimal(numeric_str)

        return price_decimal

async def calculateMaxPage(url, headers, session):
    response = session.get(url, headers=headers)

    if response.status_code == 200:
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')

        span = soup.find('span', class_=lambda x: x and x.startswith('totalProductCount'))
    
        if url == 'https://www.hepsiburada.com/dyson/dikey-supurge-c-80160032':
            return 1
        else:
            return int(int(span.text) / 36) 
    else:
        print("response is not ok")

async def Main(url):

    appOptions = AppOptions(url)

    product_repo = appOptions.product_repo

    telegram_service = appOptions.telegram_service
    
    url = appOptions.url

    headers = appOptions.headers

    session = requests.Session()
    with requests.Session() as session:

        #too many redirects exception
        session.max_redirects = 60

        max_page = await calculateMaxPage(appOptions.url, appOptions.headers, session)
        #print("max_page: ", max_page)
        print(max_page)
        for i in range(1, (int(max_page) + 1)):
            print("----------------NEW ITERATION---------------------" * 8)
            
            url = appOptions.url

            if(i == 1):
                url = url
            else:
                url = f"{url}?sayfa={i}"
            
            response = session.get(url, headers=headers)

            if response.status_code == 200:
                html_content = response.content
                soup = BeautifulSoup(html_content, 'html.parser')

                container = soup.find(id='container')

                productList = container.find_all('div', id=lambda x: x and x.startswith('ProductList'))
                first_product_list_div = productList[0]

                ul_element = first_product_list_div.find('ul', class_=lambda x: x and x.startswith('productListContent'))
                lis = ul_element.find_all('li')
                for li in lis:
                    div = li.find('div')
                    try:                                          
                        a_element = div.find('a')
                    except:
                        pass              
                    if a_element is None:
                        
                        print("item passed, 'a_element' is not found")
                        continue
                    
                    link = a_element.get('href')
                    title = a_element.get('title')

                    product_info_div_element = a_element.find('div', {'data-test-id': 'product-info-wrapper'})
                    price_div_element = product_info_div_element.find('div', {'data-test-id': 'price-current-price'})
                    if(price_div_element is None):
                        print("item passed, 'price_div_element' is not found")
                        continue

                    price_str = price_div_element.get_text()
                    price_decimal = await getPriceDecimal(price_str)

                    print("title: ", title , "link: ", link, "price: ", price_decimal)

                    existing_product = product_repo.get_product_by_link(link=link)

                    try:
                        if(existing_product == False):
                            product = Product(id=None, title=title, link=link, price=price_decimal)
                            product_repo.add_product(product=product)
                        else:
                            if(Decimal(existing_product.price) != Decimal(price_decimal)):
                                print("price change cathced. old price: ", existing_product.price, " new price: ", price_decimal,"link","https://hepsiburada.com"+link)
                                
                                old_price = Decimal(existing_product.price)

                                existing_product.price = price_decimal
                               
                                product_repo.update_product(existing_product)
                                
                                isInstallment = Decimal(price_decimal) <= old_price * Decimal(0.92)
                                
                                if(isInstallment):
                                    installment_rate = ((old_price - price_decimal) / old_price) * 100
                                    installment_rate = "{:.1f}".format(installment_rate)
                                    message = f"https://hepsiburada.com{str(link)} linkli, {existing_product.title} başlıklı ürünün fiyatında indirim oldu. Önceki fiyat: {old_price}, Yeni fiyat: {price_decimal}. İndirim oranı: %{installment_rate}"
                                    await appOptions.telegram_service.send_message(message)

                                    
                            else:
                                print("item exists in database. and price is remaining same. item link: ", link)
                                pass
                                

                    except Exception as e:    
                        print("error occured while iteration: ", e)
                        continue
            else:
                print("Initial request failed with status code:", response.status_code, "message: ", response.content)
while True:
    asyncio.run(Main(url='https://www.hepsiburada.com/cep-telefonlari-c-371965'))
    
