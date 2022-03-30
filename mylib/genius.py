import requests


def perform_get_operation(operation_type, params=None, data=None, json=None):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0",
        "Content-Type": "application/json",
        "Host": "api.genius.com",
        "Accept": "application/json",
        "Authorization": "Bearer FepQl9yYwF_hjGHYB_LyddQ9K4vUOsVk76OIpspr4FQrcai_77rIXpDsDxGKrJGo"
    }

    response = requests.get(
        f"https://api.genius.com/{operation_type}", 
        params=params, 
        data=data, json=json,
        headers=headers
    )

    return response.json()


def search_lyrics_api(search_title, search_artist=None):
    result_list = []
    if search_artist:
        search_title = f"{search_title},{search_artist}"

    response_dict = perform_get_operation("search", params={"q": search_title.replace(",", " ")})
    response_status = response_dict["meta"]["status"]

    if response_status== 200:
        title, artist = search_title.split(",")
        for response_result in response_dict["response"]["hits"]:

            if artist in response_result["result"]["artist_names"] and title in response_result["result"]["title"]:
                result_list.append(response_result["result"])
    
        return {
            "search_result": result_list,
            "status": response_status
        }
    
    return {
        "search_result": result_list,
        "status": response_status
    }


def get_song_embedded_link(song_id):
    response_dict = perform_get_operation(f"songs/{song_id}")
    response_status = response_dict["meta"]["status"]

    return {
        "status": response_status,
        "artist_names": response_dict["response"]["song"].get("artist_names", None),
        "embed_content": response_dict["response"]["song"].get("embed_content", None),
        "full_title": response_dict["response"]["song"].get("full_title", None),
        "title": response_dict["response"]["song"].get("title", None),
        "url": response_dict["response"]["song"].get("url", None)
    }


for item in search_lyrics_api("Time", search_artist="宇多田ヒカル").get("search_result"):

    print(get_song_embedded_link(item["id"]))
        
