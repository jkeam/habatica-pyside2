# Habitica Pyside2
Habitica pyside2 client.

## Prerequisites
1.  Python 3.6 or greater
2.  Create config

For a Linux or Mac, create `~/.config/habitipy/config` with permissions `600`, replacing with your own login and password.

```
[habitipy]
url = https://habitica.com
login = 5081fb11-d96a-41b6-b917-43abc1a634bd
password = ff4fa769-d623-417c-8981-1fb0d6eea501
show_numbers = y
show_style = wide
```

For a windows machine, in your current directory create an `.env` file. This workaround exists because the [habitipy(https://github.com/ASMfreaK/habitipy) module does a `600` permission check on the config file in a non-Windows friendly way.

```
URL = https://habitica.com
LOGIN = 5081fb11-d96a-41b6-b917-43abc1a634bd
PASSWORD = ff4fa769-d623-417c-8981-1fb0d6eea501
SHOW_NUMBERS = y
SHOW_STYLE = wide
```

## Running
1.  Install deps - `pip -r ./requirements.txt`
2.  Running app - `python ./app.py`
