import configparser
import os
import requests
import smtplib

# Config. Expected format:

# [SETTINGS]
# sender = <sender email @ mail.com>
# password = <sender password>
# receiver = <receiver email>
# limit = <floating point value>
#
# [TRIGGER]
# triggered = <no, or yes if the script has been triggered>

configfile = os.path.expanduser('~/.config/cln.py/config.ini')
config = configparser.ConfigParser()
config.read(configfile)

settings = config['SETTINGS']
trigger  = config['TRIGGER']['triggered']

# We want to stop further runs of this script until further notice, if it has been triggered.
if trigger != 'yes':

    # Check price.
    api = 'https://api.coindesk.com/v1/bpi/currentprice/usd.json'
    response = requests.get(api)
    json = response.json()
    price = float(json['bpi']['USD']['rate_float'])

    # If limit was hit, send mail.
    limit = float(settings['limit'])
    if price >= limit:

        # Set trigger.
        config['TRIGGER'] = { 'triggered': 'yes' }
        with open(configfile, 'w') as conf:
            config.write(conf)

        # Build message.
        sender   = settings['sender']
        receiver = settings['receiver']
        password = settings['password']
        subject  = f'Bitcoin Limit Break ${limit:.2f}'
        body     = f'Bitcoin has hit ${price:.2f}'
        message  = f"""\
From: {sender}
To: {receiver}
Subject: {subject}

{body}
"""
        # Send mail.
        smtp = smtplib.SMTP_SSL('smtp.mail.com', 465)
        smtp.ehlo()
        smtp.login(sender, password)
        smtp.sendmail(sender, receiver, message)
        smtp.quit()

