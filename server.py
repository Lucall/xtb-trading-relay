from flask import Flask, request, jsonify
import requests
import json
import websocket

app = Flask(__name__)

# Configuración XTB (se moverá a variables de entorno en Render)
XTB_API_URL = "wss://ws.xtb.com/demo"   # Usa /real si tu cuenta es real
XTB_USER = "TU_USUARIO"
XTB_PASS = "TU_PASSWORD"

def xtb_login():
    ws = websocket.create_connection(XTB_API_URL)
    login_payload = {
        "command": "login",
        "arguments": {
            "userId": XTB_USER,
            "password": XTB_PASS
        }
    }
    ws.send(json.dumps(login_payload))
    response = ws.recv()
    return json.loads(response), ws

@app.route("/signal", methods=["POST"])
def signal():
    data = request.json
    action = data.get("action")   # "buy" o "sell"
    symbol = data.get("symbol", "EURUSD")
    volume = data.get("volume", 0.01)  # microlote por defecto

    login_res, ws = xtb_login()
    if not login_res.get("status"):
        return jsonify({"error": "Login failed", "details": login_res}), 400

    trade_payload = {
        "command": "tradeTransaction",
        "arguments": {
            "tradeTransInfo": {
                "cmd": 0 if action == "buy" else 1,
                "symbol": symbol,
                "volume": volume,
                "type": 0
            }
        }
    }

    ws.send(json.dumps(trade_payload))
    response = ws.recv()
    ws.close()
    return jsonify({"result": json.loads(response)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
