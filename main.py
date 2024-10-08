import socket
import json
from flask import Flask, request, jsonify, render_template
from config import RELAY_CONTROLLER_PORT, RELAY_CONTROLLER_IP
from config import FLASK_SERVER_PORT, FLASK_SERVER_IP

app = Flask(__name__)

def send_request_to_relay_controller(data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((RELAY_CONTROLLER_IP, RELAY_CONTROLLER_PORT))
        s.sendall(json.dumps(data).encode())
        response = s.recv(1024).decode()
        return json.loads(response)

@app.route('/')
def index():
    # Request current GPIO states from the relay controller
    response = send_request_to_relay_controller({"action": "get"})
    gpios = response.get("gpios", [])
    return render_template('index.html', gpios=gpios)

@app.route('/gpio', methods=['POST'])
def handle_gpio():
    data = request.json
    gpio = int(data.get('gpio'))
    state = data.get('state')

    # Forward the update request to the relay controller
    response = send_request_to_relay_controller({"action": "update", "gpio": gpio, "state": state})

    if response.get("status") == "success":
        print(f"GPIO {gpio} is {state}")
        return jsonify({'status': 'success', 'gpio': gpio, 'state': state})
    else:
        return jsonify({'status': 'error', 'message': response.get("message")}), 500

if __name__ == '__main__':
    app.run(host=FLASK_SERVER_IP, port=FLASK_SERVER_PORT, debug=True)
