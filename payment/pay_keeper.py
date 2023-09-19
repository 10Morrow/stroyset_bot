import aiohttp
import base64

from config import PAY_SYS_NAME, PAY_SYS_PASS


async def create_bill(amount):
    """создаем счет на оплату суммы amount"""
    user, password = PAY_SYS_NAME, PAY_SYS_PASS

    credentials = f"{user}:{password}"
    base64_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + base64_credentials
    }

    server_paykeeper = "https://demo.paykeeper.ru"

    payment_data = {
        "pay_amount": amount,
        "clientid": "stroyset",
    }

    async with aiohttp.ClientSession() as session:
        uri = "/info/settings/token/"
        async with session.get(server_paykeeper + uri, headers=headers) as response:
            response.raise_for_status()
            response_data = await response.json()
            if 'token' in response_data:
                token = response_data['token']
            else:
                raise ValueError("Ошибка: поле 'token' отсутствует в ответе сервера.")

        uri = "/change/invoice/preview/"

        payment_data['token'] = token

        async with session.post(server_paykeeper + uri, data=payment_data, headers=headers) as response:
            response.raise_for_status()
            response_data = await response.json()
            if 'invoice_id' in response_data:
                invoice_id = response_data['invoice_id']
            else:
                raise ValueError("Ошибка: поле 'invoice_id' отсутствует в ответе сервера.")

        link = f"{server_paykeeper}/bill/{invoice_id}/"

        return [link, invoice_id]


async def check_status(invoice_id):
    """проверяем статус выставленного счета по invoice_id"""
    user, password = PAY_SYS_NAME, PAY_SYS_PASS
    credentials = f"{user}:{password}"
    base64_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + base64_credentials
    }

    server_paykeeper = "https://demo.paykeeper.ru"

    async with aiohttp.ClientSession() as session:
        uri = f"/info/invoice/byid/?id={invoice_id}"

        async with session.get(server_paykeeper + uri, headers=headers) as response:
            response.raise_for_status()
            response_data = await response.json()

            if 'status' in response_data:
                status = response_data['status']
                return status
            else:
                raise ValueError("Ошибка: поле 'status' отсутствует в ответе сервера.")


async def cancel_payment(invoice_id):
    """отменяем выставленный счет по его invoice_id"""
    user, password = PAY_SYS_NAME, PAY_SYS_PASS

    credentials = f"{user}:{password}"
    base64_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + base64_credentials
    }

    server_paykeeper = "https://demo.paykeeper.ru"

    payment_data = {'id': invoice_id}

    async with aiohttp.ClientSession() as session:
        uri = "/info/settings/token/"
        async with session.get(server_paykeeper + uri, headers=headers) as response:
            response.raise_for_status()
            response_data = await response.json()
            if 'token' in response_data:
                token = response_data['token']
            else:
                raise ValueError("Ошибка: поле 'token' отсутствует в ответе сервера.")

        uri = "/change/invoice/revoke/"

        payment_data['token'] = token

        async with session.post(server_paykeeper + uri, data=payment_data, headers=headers) as response:
            response.raise_for_status()
            response_data = await response.json()
            if response_data['result'] == 'success':
                return True
            else:
                return False
