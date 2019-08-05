"""module for search in vk"""
from datetime import datetime
from requests import post

def vk_search(__name_tag, link, access_token):
    """tag, link:'vk.com/...', access_token"""
    #объявление переменных, обрезание ссылки до короткого имени
    return_list = []
    __platform = 'VK'
    link = link[7:]
    #получение id по короткому имени
    payload = {"screen_name":link, "access_token":access_token, "v":"5.101"}
    response = post("https://api.vk.com/method/utils.resolveScreenName", data=payload)
    response_json = response.json()
    object_id = response_json["response"]["object_id"]
    object_type = response_json["response"]["type"]
    #у сообществ отрицательный id
    if object_type in ("group", "page"):
        object_id = -1*object_id
    #поиск записей по слову
    payload = {"owner_id":object_id, "query":__name_tag, "count":100}
    payload["access_token"] = access_token
    payload["v"] = "5.101"
    response = post("https://api.vk.com/method/wall.search", data=payload)
    response_json = response.json()
    for item in response_json["response"]["items"]:
    	#декодировка даты из unixtime в datetime
        __date_time = datetime.utcfromtimestamp(item["date"]).strftime("%H:%M %d.%m.%Y")
        #если это репост - получить текст из репостнутой записи
        if "copy_history" in item.keys():
            __content_message = item["copy_history"][0]["text"]
        else:
            __content_message = item["text"]
        return_list.append((__date_time, __platform, __name_tag, __content_message))
    return return_list
