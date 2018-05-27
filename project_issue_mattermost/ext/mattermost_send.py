# -*- coding: utf-8 -*-

# THIS MUST BE RUN WITH PYTHON3
# The syntax when running:
# python3 mattermost_send.py {dict with variables}

import sys
from ast import literal_eval
from mattermostdriver import Driver
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Get variables
# TODO: A lot of validation here
file_name = sys.argv[0]
vars_str = sys.argv[1]

try:
    # Your program can't have any bugs when you wrap everything in try-block!
    vars = literal_eval(vars_str)
    mm_driver = Driver({
        'url': vars['url'],
        'login_id': vars['login_id'],
        'password': vars['password'],
        'scheme': vars['scheme'],
        'port': int(vars['port']),
        'basepath': vars['basepath'],
        'verify': vars['verify'],
        'timeout': 2,
    })

    mm_driver.login()

    channel_id = mm_driver.api['channels'].get_channel_by_name_and_team_name(vars['team'], vars['channel'])['id']

    mm_driver.api['posts'].create_post(options={
        'channel_id': channel_id,
        'message': vars['message'],
    })

except Exception as e:
    print(e)
