from datetime import date

from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from db import *
from models import Vkfinder

with open('token.txt', 'r') as f:
    group_vk_token = f.readline().strip()
    personal_vk_token = f.readline().strip()

session = VkApi(token=group_vk_token)
session_personal = VkApi(token=personal_vk_token)
longpoll = VkLongPoll(session)


def hello_and_init_search(event, request):
    """если пришло привет, достать имя пользователя и отправить сообщение с инструкцией"""

    user_data = get_user_data(event.user_id)

    if request[0] != '-':
        message = f'Привет, {user_data["first_name"]}!\n Введите слово "поиск" без кавычек для поиска людей'
        write_message(event.user_id, message)

    # заход по - добавляем дополнительные данные
    else:
        if '--возраст' in request:
            user_data['bdate'] = f'xx.xx.{" ".join(request.split()[1:])}'  # --возраст 1987
        elif '--город' in request:
            b = [el.capitalize() for el in request.split()[1:]]  # вида Великий Устюг, иначе не найдётся
            city = ' '.join(b)
            data = session_personal.method('database.getCities',
                                           {'country_id': 1,
                                            'q': city,  # q - видимо от query
                                            'count': 1})
            city_id = data['items'][0]['id']
            user_data['city'] = city_id  # --город Великий Новгород не находится вообще
        elif '--пол' in request:
            user_data['sex'] = int(f'{" ".join(request.split()[1:])}')  # по идее --пол 2
        write_message(event.user_id, 'а теперь ещё раз слово "поиск" без кавечек')

    return user_data


def get_user_data(user_id):
    """получить данные пользователя"""
    user_data = session.method('users.get',
                               {'user_ids': user_id,
                                'fields': 'city,bdate,sex,country'}
                               )
    if user_data[0].get('city'):  # если там указан город, сразу оставить от него только id города
        city_id = user_data[0]['city']['id']
        print(city_id)
        user_data[0]['city'] = city_id
        print(user_data[0]['city'])
    return user_data[0]  # ибо там формат [{}]


def write_message(user_id, message):
    """отправить пользователю сообщение"""
    session.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': get_random_id()})


def data_check(event, user_data):
    bdate = user_data.get('bdate')
    if bdate:
        age = date.today().year - int(bdate.split('.')[-1])  # возраст пользователя из сессии
        user_data['age'] = age
        print(age)
    else:
        age = None
        user_data['age'] = None
    city = user_data.get('city')
    sex = user_data.get('sex')
    # relation = user_data.get('relation')

    if not bdate:
        message = 'не хватает возраста, введите год вашего рождения в формате --возраст ХХХХ (1997, 2000, 1945 итп)'
        write_message(event.user_id, message)
        return False
    elif not city:
        message = 'не хватает города, введите ваш город в формате --город Москва, или --город Щёлково'
        write_message(event.user_id, message)
        return False
    elif not sex:
        message = 'не хватает пола, введите ваш пол в формате --пол 1 или --пол 2, где 1 - женский, 2 - мужской'
        write_message(event.user_id, message)
        return False
    # if not relation:
    #     message = 'не хватает статуса, введите ваш статус'
    #     write_message(event.user_id, message)

    print(f'{age} возраст, {city} город, {sex} пол')  # это данные того, кто написал
    return True


def search_users(event, user_data):
    """поиск пользователей"""

    if not user_data:  # если пользователь ввёл сразу поиск, то данных сессии ещё нет
        user_data = get_user_data(event.user_id)

    data_is_complete = data_check(event, user_data)  # хватает ли данных для поиска

    if data_is_complete:
        message = 'данные в порядке, приступаю к поиску, немного подождите, покурите или попейте чайку пока'
        write_message(event.user_id, message)

        # САМОЕ ГЛАВНОЕ: искать ПРОТИВОПОЛОЖНЫЙ пол ))))))))))))))
        if user_data['sex'] == 1:
            sex_search = 2
        else:
            sex_search = 1

        request = session_personal.method('users.search',
                                          {
                                              'age_from': user_data['age'] - 1,
                                              'age_to': user_data['age'] + 1,
                                              'sex': sex_search,
                                              'city': user_data['city'],
                                              'status': 6,  # вот это статус "активный поиск"
                                              'count': 3,  # сколько юзеров искать
                                          }
                                          )

        q = session_db.query(Vkfinder.url).filter(Vkfinder.user_id == str(event.user_id)).all()
        result = [el[0] for el in q]  # список пользователей из базы для данного пользователя
        print(result, 'СПИСОК ЮЗЕРОВ')
        for person in request['items']:
            print(person)

            if not person['is_closed']:  # смысл идти ниже только если пользователь открыт
                link = f"vk.com/id{person['id']}"  # vk.com/id83915036
                if link not in result:  # если в базе такого нету, тогда ищем фоточки, и добавляем в базу

                    photos = get_photos(person['id'])
                    print(photos)
                    if photos:  # только если есть фоточки, иначе нафиг))
                        new = Vkfinder(user_id=str(event.user_id), url=link)
                        session_db.add(new)
                        write_message(event.user_id, 'очередной человек')
                        write_message(event.user_id, link)
                        for url in photos:
                            print(url, 'картиночка')
                            write_message(event.user_id, url)

        session_db.commit()


def get_photos(user_id):
    """получить 3 фоточки пользователя с максимальными лайками"""
    request = session_personal.method('photos.get',
                                      {
                                          'owner_id': user_id,
                                          'count': 200,
                                          'photo_sizes': 1,
                                          'extended': 1,
                                          'v': 5.131,
                                          'album_id': 'profile'
                                      })

    result = request['items']
    r = []
    for photo in result:
        like = photo['likes']['count']
        link = photo['sizes'][-1]['url']
        r.append([like, link])
    r.sort(reverse=True)
    urls = [el[1] for el in r[:3]]
    print(urls)
    return urls


def run_app():
    """основная функция запуска"""
    user_data = None
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            request = event.text.lower()  # КАЖДОЕ ВХОДЯЩЕЕ СООБЩЕНИЕ БОТУ

            # если пришло привет или -, а это означает добавка каких-то данных
            if request in ['начать', 'привет', 'здравствуй', 'hi'] or request[0] == '-':
                user_data = hello_and_init_search(event, request)
            elif request == 'поиск':
                search_users(event, user_data)
            else:
                write_message(event.user_id, 'не понял вашего сообщения')
