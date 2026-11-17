// Modelo de nível de primeira ordem: G(s) = K/(tau*s + 1).
// Discretização exata com retenção de ordem zero:
// h[k+1] = a*h[k] + K*(1-a)*u[k], a = exp(-Ts/tau).
const K = 1;
const tau = 5; // segundos
const Ts = 1;  // segundo por mensagem de controle
const a = Math.exp(-Ts / tau);

if (msg.topic === "sensor") {
    // O cliente sensor fornece uma medida para inicializar/corrigir h[k].
    const h = Number(msg.payload);
    if (!Number.isFinite(h) || h < 0) {
        node.warn("Medida de nível inválida.");
        return null;
    }
    flow.set("nivel", h);
    // A inicialização não avança o tempo discreto.
    const saida = { payload: `${h.toFixed(3)}\n`, topic: "nivel", _session: flow.get("sensorSession") };
    return [saida._session ? saida : null, { payload: h, topic: "nível inicializado" }];
}

const u = Number(msg.payload);
if (!Number.isFinite(u) || u < 0) {
    node.warn("Controle inválido.");
    return null;
}
const h = Number(flow.get("nivel") ?? 0);
const proximo = a * h + K * (1 - a) * u;
flow.set("nivel", proximo);
flow.set("amostra", Number(flow.get("amostra") ?? 0) + 1);
const saida = { payload: `${proximo.toFixed(3)}\n`, topic: "nivel", _session: flow.get("sensorSession") };
return [saida._session ? saida : null,
        { payload: { k: flow.get("amostra"), u, h: proximo }, topic: "planta" }];
