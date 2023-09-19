import aiohttp

from config import API_TOKEN


async def create_user(name, surname, phone, telegram_id, email='', type='fl', company='', inn=''):
    """создает пользователя веб-сайта используя апи"""
    root_url = "https://stroyset.pro"
    uri = f"/api/tg/create-user?api_key={API_TOKEN}"
    payload = {
        'firts_name': name,
        'last_name': surname,
        'type': type,
        'company': company,
        'inn': inn,
        'phone': phone,
        'email': email,
        'telegram_id': telegram_id
    }
    headers = {}

    async with aiohttp.ClientSession() as session:
        async with session.post(root_url + uri, data=payload, headers=headers) as response:
            response_text = await response.json()

    return response_text


async def create_ad(user_id, category_id, description, location, location_id, title='', price=None):
    """создает объявление используя апи веб-сайта"""

    root_url = "https://stroyset.lh/api"
    uri = f"/api/tg/create-ad?api_key={API_TOKEN}"

    payload = {
        'Ad[user_id]': user_id,
        'Ad[category_id]': category_id,
        'Ad[title]': title,
        'Ad[description]': description,
        'Ad[meta][location]': location,
        'Ad[meta][location_id]': location_id,
        'Ad[meta][price]': price
    }
    headers = {}

    async with aiohttp.ClientSession() as session:
        async with session.post(root_url + uri, data=payload, headers=headers) as response:
            response_text = await response.text()
            print(response_text)


async def get_federal_districts():
    """возвращает список федеральных округов получаемых по апи от веб-сайта"""
    root_url = "http://stroyset.pro"
    uri = f"/api/tg/get-federal-districts?api_key={API_TOKEN}"
    headers = {}

    async with aiohttp.ClientSession() as session:
        async with session.post(root_url + uri, headers=headers) as response:
            districts = await response.json()
    return districts['federal_districts']


async def get_regions_by_district(district):
    """возвращает список регионов по федеральному округу"""
    regions_list = []
    root_url = "http://stroyset.pro"
    headers = {}
    async with aiohttp.ClientSession() as session:
        link = root_url + f"/api/tg/get-regions?api_key={API_TOKEN}&federal_district={district}"
        async with session.get(link, headers=headers) as response:
            district_regions = await response.json()
    for region in district_regions['regions']:
        regions_list.append((region['name_with_type'], region['kladr_id']))
    return regions_list


async def get_cities_by_region(region_kladr_id):
    """возвращает список городов по переданному kladr_id региона"""
    root_url = "http://stroyset.pro"
    headers = {}
    async with aiohttp.ClientSession() as session:
        link = root_url + f"/api/tg/get-cities?api_key={API_TOKEN}&region_kladr_id={region_kladr_id}"
        async with session.get(link, headers=headers) as response:
            cities = await response.json()
        cities_list = cities['cities']
        processed_cities_list = [(city['city'], city['kladr_id']) for
                                     city in cities_list]
    return processed_cities_list


async def get_categories_data():
    """возвращает обработанный список словарей с названиями и id категорий
    (принадлежащих родительским категориям 1 и 2)"""
    processed_data = []
    root_url = "http://stroyset.pro"
    needed_parent_id_list = [2, 3]
    for parent_id in needed_parent_id_list:
        uri = f"/api/tg/get-categories?api_key={API_TOKEN}&parent_id={parent_id}"
        headers = {}

        async with aiohttp.ClientSession() as session:
            async with session.post(root_url + uri, headers=headers) as response:
                categories = await response.json()
                category_list = categories['categories']
                processed_category_data = [{category['title']:category['id']} for category in category_list]
        processed_data.extend(processed_category_data)

    return processed_data


async def get_contractors(city_kladr_id = None):
    """возращает список староителей"""
    url = f"https://stroyset.pro/api/tg/get-contractors?api_key={API_TOKEN}&category_id=3&page=1&per-page=5&" \
          f"region={city_kladr_id}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                contractors = data['contractors']
                contractors_list = [(contractor['firts_name'] + ' ' + contractor['last_name'],
                                     contractor['type'],
                                     contractor['company_description'].replace('\r\n', ' '),
                                     contractor['phone']) for
                                    contractor in contractors]
                return contractors_list


async def subscribe_to_category(website_user_id, category_id):
    """подписывает пользователя с website_user_id на категории с category_id и по id города city_kladr_id"""

    root_url = "https://stroyset.pro"
    uri = f"/api/tg/subscribe?api_key={API_TOKEN}"
    payload = {
        'user_id': website_user_id,
        'category[]': category_id,
    }
    headers = {}

    async with aiohttp.ClientSession() as session:
        async with session.post(root_url + uri, data=payload, headers=headers) as response:
            await response.text()


async def create_contractor(website_user_id, description, category_id, city_kladr_id):
    url = f"https://stroyset.pro/api/tg/create-contractor?api_key={API_TOKEN}"

    payload = {
        "company_description": description,
        "user_id": website_user_id,
        "category": category_id,
        "region": city_kladr_id,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            if response.status == 200:
                await response.text()
