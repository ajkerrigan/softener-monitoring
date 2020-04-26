import json

from pathlib import Path

from flask import Flask, request, jsonify
from flask_sendgrid import SendGrid

app = Flask(__name__)
app.config['SENDGRID_API_KEY'] = Path('/run/secrets/sendgrid_api_key').read_text()
app.config['SENDGRID_DEFAULT_FROM'] = Path('/run/config/mail_from').read_text()
mail = SendGrid(app)

STATUS_MAP = {
    'ok': 'idle',
    'info': 'running'
}

@app.route("/", methods=["POST"])
def notify():
    if request.content_type == 'application/json' and '_message' in request.json:
        status = STATUS_MAP.get(request.json.get('_level'), 'unknown')
        try:
            mail.send_email(
                to_email=[{'email':Path('/run/config/mail_to').read_text()}],
                subject='Softener Status',
                text=f'Softener status is: {status}\n\nDetail:\n\n{json.dumps(request.json, indent=4)}'
            )
            return jsonify(request.json)
        except Exception as err:
            print(err)
    else:
        return '', 204

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
