# Pandora Auto Refresh Token
A simple script to refresh your PandoraNext token(both share token and pool token) automatically.

# Usage
1. Install python3 and pip3
2. Install dependencies: `pip3 install -r requirements.txt`
3. Add your credentials to `credentials.txt`
4. Add your pool token to `pool_token.txt` if you have one or leave it blank
5. Add the script to crontab:
    ```shell
    crontab -e
    ```
    Add the following line to the end of the file:
    ```crontab
    0 0 * * 1 python3 /path/to/pandora-auto-refresh-token/refresh.py
    ```
    This will run the script every Monday at 00:00. You can change the time to whatever you want. It only refresh session_token when necessary so you don't need to worry about the quota limit.

# Credits
- [PandoraNext](https://github.com/pandora-next/deploy)