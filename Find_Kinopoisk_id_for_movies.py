import requests
import hashlib
import base64
import json

KINOPOISK_API_URL = "https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword"
SMARTY_API_MODIFY_URL = ""
SMARTY_API_DETAIL_URL = ""
KINOPOISK_API_KEY = ''
SMARTY_API_KEY = ''
client_id = '1'


def _get_signature(request_data):
    sign_source = u''
    for (key, value) in sorted(request_data.items()):
        sign_source += u'%s:%s;' % (key, value)
    sign_source += SMARTY_API_KEY
    digester = hashlib.md5()
    sign_source_utf = sign_source.encode('utf-8')
    sign_source_base64 = base64.b64encode(sign_source_utf)
    digester.update(sign_source_base64)
    signature = digester.hexdigest()
    return signature


def send_data(data):
    data['client_id'] = client_id
    signature = _get_signature(data)
    data['signature'] = signature
    resource = requests.post(SMARTY_API_MODIFY_URL, data=data)
    return resource.text


def get_data(vid):
    params = {
        'vid': vid,
        'client_id': client_id,
        'api_key': SMARTY_API_KEY
    }
    try:
        response = requests.get(SMARTY_API_DETAIL_URL, params=params)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Ошибка при получении данных: {response.status_code}")
    except Exception as e:
        print(f"Ошибка запроса: {str(e)}")
    return None

def get_kinopoisk_id(movie_title, year):
    params = {
        "keyword": movie_title,
        "year": year
    }
    headers = {
        "X-API-KEY": KINOPOISK_API_KEY
    }
    response = requests.get(KINOPOISK_API_URL, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get("films"):
            return data["films"][0]["filmId"]
    return None


def update_kinopoisk_id(movie_id, kinopoisk_id):
    data = {
        "id": movie_id,
        "kinopoisk_id": kinopoisk_id
    }
    response_text = send_data(data)
    return response_text


def main(movie):
    movie_id = movie['id']
    movie_name = movie['name']
    movie_year = movie['year']

    kinopoisk_id = get_kinopoisk_id(movie_name, movie_year)
    if kinopoisk_id:
        response = update_kinopoisk_id(movie_id, kinopoisk_id)
        print(response)
    else:
        print(f"Кинопоиск не вернул kinopoisk_id для фильма {movie_name} ({movie_year})")


if __name__ == "__main__":
    vid_list = [9, 10]  # Список идентификаторов фильмов
    for vid in vid_list:
        response_data = get_data(vid)
        if response_data:
            try:
                data = json.loads(response_data)
                if 'id' in data:
                    main(data)
                else:
                    print("Ключ 'id' отсутствует в ответе")
            except json.JSONDecodeError as e:
                print(f"Ошибка декодирования JSON: {str(e)}")
        else:
            print("Не удалось получить данные")
