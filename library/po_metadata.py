"""
A function to download post office metadata from pochta.ru.
"""

import json
import requests


# The below cookies, headers and url were working as of 25.02.2021

COOKIES = {
    '_fbp': 'fb.1.1613842596243.1318686691',
    '_ga': 'GA1.2.84838967.1613842596',
    '_gat_UA-74289235-3': '1',
    '_gid': 'GA1.2.1432029342.1614233540',
    'sputnik_session': '1614233539960|3',
    'tmr_reqNum': '99',
    'tmr_detect': '0%7C1614233549846',
    '_ym_visorc': 'w',
    'tmr_lvid': '4a57d41268fe28c62a3ab35a70ffbbb2',
    'tmr_lvidTS': '1611758721869',
    'GUEST_LANGUAGE_ID': 'ru_RU',
    '_dc_gtm_UA-74289235-3': '1',
    '_gat_UA-74289235-1': '1',
    '_ym_isad': '2',
    'JSESSIONID': 'B5F099469E4EC3DB3844F7DDAAAD6CF6',
    '_gaexp': 'GAX1.2.4762Mz6JTbq9Wj_lOWrXCA.18704.1',
    'HeaderBusinessTooltip': 'showed',
    '_ym_d': '1613842596',
    '_ym_uid': '1611758721505322139',
    'sp_test': '1',
    'ANALYTICS_UUID': '31580e6b-e87e-4b2b-b630-b7f4ed28f6f7',
    'COOKIE_SUPPORT': 'true',
}

HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Origin': 'https://www.pochta.ru',
    'Content-Length': '97',
    'Accept-Language': 'en-us',
    'Host': 'www.pochta.ru',
    'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) '
                   'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 '
                   'Safari/605.1.15'),
    'Referer': 'https://www.pochta.ru/post-index',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

URL = ('https://www.pochta.ru/suggestions/v2/postoffice.find-nearest-by-'
       'postalcode-raw-filters')


class NotValidResponseError(Exception):
    pass


class EmptyResponseError(Exception):
    pass


def get_pochtaru_response(postcode: str) -> str:
    """Query pochta.ru for a postcode and return raw response string
    if successfull. Return `error` if failed."""
    data = f'{{"postalCode":"{postcode}","limit":1}}'
    try:
        resp = requests.post(URL, headers=HEADERS, cookies=COOKIES, data=data)
    except Exception:
        return 'error'
    return resp.text


def validate_pochtaru_response(response_string: str):
    """Evaulate if the response is a valid JSON and return a dictionary
    of data if it is. Raise custom Exception if it isn't."""
    try:
        metadata = json.loads(response_string)
    except json.decoder.JSONDecodeError:
        raise NotValidResponseError
    if metadata == []:
        raise EmptyResponseError
    return metadata[0]


def get_PO_address(postcode: str) -> str:
    """Download post office address given the post office postcode."""
    raw_response = get_pochtaru_response(postcode)
    if raw_response == 'error':
        return 'error'
    try:
        data = validate_pochtaru_response(raw_response)
    except NotValidResponseError:
        return 'error'
    except EmptyResponseError:
        return 'no such P.O.'
    return data['address']['fullAddress']
