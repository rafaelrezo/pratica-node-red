"""Gera o fluxo importável do Node-RED a partir do código em planta.js."""

import json
from pathlib import Path


BASE = Path(__file__).resolve().parent
planta = (BASE / "planta.js").read_text(encoding="utf-8")
sensor = '''const texto = String(msg.payload).trim();
flow.set("sensorSession", msg._session);
if (texto.toUpperCase() === "HELLO") return null;
if (!/^(?:\\d+\\.?\\d*|\\.\\d+)$/.test(texto)) {
    node.warn("Sensor: envie um número >= 0 ou HELLO.");
    return null;
}
msg.topic = "sensor";
msg.payload = Number(texto);
return msg;'''
atuador = '''const texto = String(msg.payload).trim();
if (!/^(?:\\d+\\.?\\d*|\\.\\d+)$/.test(texto)) {
    node.warn("Atuador: envie um número >= 0.");
    return null;
}
msg.topic = "atuador";
msg.payload = Number(texto);
return msg;'''

nodes = [
    {"id":"aba_pratica","type":"tab","label":"Prática TCP - planta de nível","disabled":False,"info":"Cada comando u avança um passo de Ts=1 s."},
    {"id":"tcp_sensor","type":"tcp in","z":"aba_pratica","name":"Servidor sensor :5001","server":"server","host":"","port":"5001","datamode":"stream","datatype":"utf8","newline":"\\n","topic":"","trim":False,"base64":False,"tls":"","x":170,"y":100,"wires":[["parse_sensor"]]},
    {"id":"parse_sensor","type":"function","z":"aba_pratica","name":"Medida / HELLO","func":sensor,"outputs":1,"timeout":0,"noerr":0,"initialize":"","finalize":"","libs":[],"x":390,"y":100,"wires":[["planta"]]},
    {"id":"tcp_atuador","type":"tcp in","z":"aba_pratica","name":"Servidor atuador :5002","server":"server","host":"","port":"5002","datamode":"stream","datatype":"utf8","newline":"\\n","topic":"","trim":False,"base64":False,"tls":"","x":170,"y":220,"wires":[["parse_atuador"]]},
    {"id":"parse_atuador","type":"function","z":"aba_pratica","name":"Validar u","func":atuador,"outputs":1,"timeout":0,"noerr":0,"initialize":"","finalize":"","libs":[],"x":390,"y":220,"wires":[["planta"]]},
    {"id":"inject_u","type":"inject","z":"aba_pratica","name":"Forçar u = 10","props":[{"p":"payload"},{"p":"topic","vt":"str"}],"repeat":"","crontab":"","once":False,"onceDelay":0.1,"topic":"atuador","payload":"10","payloadType":"num","x":170,"y":310,"wires":[["planta"]]},
    {"id":"inject_h","type":"inject","z":"aba_pratica","name":"Forçar h = 0","props":[{"p":"payload"},{"p":"topic","vt":"str"}],"repeat":"","crontab":"","once":False,"onceDelay":0.1,"topic":"sensor","payload":"0","payloadType":"num","x":170,"y":370,"wires":[["planta"]]},
    {"id":"planta","type":"function","z":"aba_pratica","name":"Planta de nível G(z)","func":planta,"outputs":2,"timeout":0,"noerr":0,"initialize":"","finalize":"","libs":[],"x":650,"y":180,"wires":[["tcp_resposta"],["debug_planta"]]},
    {"id":"tcp_resposta","type":"tcp out","z":"aba_pratica","name":"Saída ao sensor","host":"","port":"","beserver":"reply","base64":False,"end":False,"tls":"","x":900,"y":140,"wires":[]},
    {"id":"debug_planta","type":"debug","z":"aba_pratica","name":"Amostra k, u, h","active":True,"tosidebar":True,"console":False,"tostatus":False,"complete":"payload","targetType":"msg","statusVal":"","statusType":"auto","x":900,"y":220,"wires":[]},
]
(BASE / "fluxo-node-red.json").write_text(json.dumps(nodes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
