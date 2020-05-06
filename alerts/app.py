import json

from pathlib import Path
import textwrap

from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_caching import Cache
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Email, To, Content, Mail

app = Flask(__name__)
app.config.from_mapping({
    'DEBUG': True,
    'API_KEY': Path('/run/secrets/sendgrid_api_key').read_text(),
    'MAIL_FROM': Email(Path('/run/config/mail_from').read_text()),
    'MAIL_TO': To(Path('/run/config/mail_to').read_text()),
    'CYCLE_LENGTH': timedelta(hours=3),
    'CACHE_TYPE': 'simple',
})
cache = Cache(app)
cache.set('last_notification', datetime(1900, 1, 1))

sg = SendGridAPIClient(api_key=app.config['API_KEY'])

STATUS_MAP = {
    'ok': 'idle',
    'info': 'running'
}
MAIL_TEMPLATE = textwrap.dedent('''\
    Softener status is: {status}
    
    Detail:
    
    {detail}
''')

@app.route("/", methods=["POST"])
def notify():
    now = datetime.utcnow()
    if request.content_type == 'application/json' and '_message' in getattr(request, 'json', {}):
        status = STATUS_MAP.get(request.json.get('_level'), 'unknown')
        if cache.get('last_notification') >= (now - app.config['CYCLE_LENGTH']):
            app.logger.info(f'The last notification was less than a cycle ago ({cache.get("last_notification")})')
            return 'Too soon'
        try:
            content = Content(
                'text/plain',
                MAIL_TEMPLATE.format(status=status, detail=json.dumps(request.json, indent=4))
            )
            mail = Mail(
                app.config['MAIL_FROM'],
                app.config['MAIL_TO'],
                'Softener Status',
                content
            )
            app.logger.info(f'Sending notification to: {app.config["MAIL_TO"].email}')
            response = sg.client.mail.send.post(request_body=mail.get())
            cache.set('last_notification', now)
            return response.body, response.status_code
        except Exception as err:
            return err
    else:
        return '', 204

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, use_reloader=False, use_evalex=False, port=80)
