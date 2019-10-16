import vimeo

v = vimeo.VimeoClient(token='8f1f9178dcb0cb41d781c819152b6052')


def about_me():
    about = v.get('/me')
    return about


def pictures(video_id):
    url_str = '/videos/{0}/pictures'.format(video_id)
    response = v.get(url_str, params={"fields": "data,sizes,link"})
    
    if response.status_code == 200:
        data = response.json()
        return data['data'][0]['sizes'][2]['link']
    
    return None
