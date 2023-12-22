import requests
import os

base_url = 'http://192.168.2.2:8081/pandoraproxy1'

headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}


def remove_s(file_path: str) -> None:
    if os.path.exists(file_path):
        os.remove(file_path)


def get_session_token(username: str, password: str) -> str:
    data = {
        'username': username,
        'password': password
    }
    response = requests.request('POST', base_url + '/api/auth/login', headers=headers, data=data)

    if 'session_token' in response:
        return response.session_token + '\n'

    # to keep credentials.txt and session_tokens.txt aligned
    return '\n'


def get_access_token(session_token: str) -> str:
    data = {
        'session_token': session_token
    }
    response = requests.request('POST', base_url + '/api/auth/session', headers=headers, data=data)

    if 'access_token' in response:
        return response.access_token
    
    # get access token failed, which means session token may be expired
    with open('session_tokens.txt', 'r') as file:
        session_tokens = file.readlines()

    for index, token in enumerate(session_tokens):
        if token == session_token:
            _ , username, password = credentials[index].split(',', 2)
            new_token = get_session_token(username, password)
            session_tokens[index] = new_token
            break

    remove_s('session_tokens.txt')
    with open('session_tokens.txt', 'w') as file:
        file.writelines(session_tokens)

    data = {
        'session_token': new_token.replace('\n', '')
    }
    response = requests.request('POST', base_url + '/api/auth/session', headers=headers, data=data)

    if 'access_token' in response:
        return response.access_token

    # give it up
    return ''


def get_share_token(unique_name: str, access_token: str) -> str:
    data = {
        'unique_name': unique_name,
        'access_token': access_token,
        'site_limit': '',
        'expires_in': 0,
        'show_conversations': 'false',
        'show_userinfo': 'false'
    }
    response = requests.request('POST', base_url + '/api/token/register', headers=headers, data=data)

    if 'token_key' in response:
        return response.token_key + '\n'
    
    return '\n'


def update_pool_token(pool_token: str, share_tokens: list) -> str:
    data = {
        'share_tokens': ''.join(share_tokens),
        'pool_token': pool_token
    }

    requests.request('POST', base_url + '/api/pool/update', headers=headers, data=data)


def get_session_tokens() -> None:
    session_tokens = []
    for line in credentials:
        if(line != ''):
            _ , username, password = line.split(',', 2)
            session_tokens.append(get_session_token(username, password))

    remove_s('session_tokens.txt')

    with open('session_tokens.txt', 'w') as file:
        file.writelines(session_tokens)


def refresh():
    if not os.path.exists('credentials.txt'):
        return

    with open('credentials.txt', 'r') as file:
        global credentials
        credentials = file.readlines()

    if not os.path.exists('session_tokens.txt'):
        get_session_tokens()

    with open('session_tokens.txt', 'r') as file:
        session_tokens = file.readlines()

    access_tokens = []
    for session_token in session_tokens:
        if session_token != '':
            access_tokens.append(get_access_token(session_token))
    
    share_tokens = []
    for index, access_token in enumerate(access_tokens):
        unique_name, _ = credentials[index].split(',', 2)
        if access_token != '':
            share_tokens.append(get_share_token(unique_name, access_token))

    remove_s('share_tokens.txt')
    with open('share_tokens.txt', 'w') as file:
        file.writelines(share_tokens)

    if not os.path.exists('pool_token.txt'):
        return

    with open('pool_token.txt', 'r') as file:
        pool_token = file.readline()

    if pool_token != '':
        update_pool_token(pool_token, share_tokens)


if __name__ == '__main__':
    refresh()