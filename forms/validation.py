import re


async def validate_mobile_number(number):
    """проверяем являеются ли введенные данные российским номером"""
    pattern = r'^(?:\+7|8|7)?\d{10}$'
    number = re.sub(r'\s|-', '', number)
    if re.match(pattern, number):
        return True
    else:
        return False


async def validate_email(email):
    """проверяем валидность email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True
    else:
        return False


async def validate_inn(inn):
    """проверяем достоверность ИНН проверив состоит ли он из цифр и подсчитав контрольную сумму"""
    pattern_10_digits = r'^\d{10}$'
    pattern_12_digits = r'^\d{12}$'
    if re.match(pattern_10_digits, inn) or re.match(pattern_12_digits, inn):
        if len(inn) == 10 and _check_control_digit_10(inn):
            return True
        elif len(inn) == 12 and _check_control_digit_12(inn):
            return True
    return False


def _check_control_digit_10(inn):
    """Высчитываем контрольную сумму для 10-ти значного инн"""
    coefficients = [2, 4, 10, 3, 5, 9, 4, 6, 8]
    control_sum = sum(int(digit) * coeff for digit, coeff in zip(inn[:9], coefficients)) % 11
    control_digit = control_sum % 10 if control_sum < 10 else 0
    return int(inn[9]) == control_digit


def _check_control_digit_12(inn):
    """Высчитываем контрольную сумму для 12-ти значного инн"""
    coefficients1 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
    coefficients2 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
    control_sum1 = sum(int(digit) * coeff for digit, coeff in zip(inn[:10], coefficients1)) % 11
    control_sum2 = sum(int(digit) * coeff for digit, coeff in zip(inn[:11], coefficients2)) % 11
    control_digit1 = control_sum1 % 10 if control_sum1 < 10 else 0
    control_digit2 = control_sum2 % 10 if control_sum2 < 10 else 0
    return int(inn[10]) == control_digit1 and int(inn[11]) == control_digit2
