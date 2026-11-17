# Prompts para gerar os esquemas

Use os prompts abaixo em um gerador de imagens ou em uma ferramenta de diagramas. Para material didático, confira os rótulos e as direções das setas antes de usar a imagem: geradores de imagens podem errar texto técnico. Os arquivos `figuras/*.png` incluídos nesta pasta já representam estes esquemas.

## 1. Arquitetura entre as duas EC2

> Crie um esquema técnico vetorial, horizontal, em português, fundo branco, proporção 16:7, para uma apostila universitária de Engenharia de Controle e Automação. Use três blocos grandes, alinhados da esquerda para a direita: “Computador do aluno” (VS Code e navegador), “EC2 A — clientes Python” (`sensor.py` e `atuador.py`) e “EC2 B — Node-RED” (dois servidores TCP e planta de nível). Mostre uma seta SSH do computador para a EC2 A. Mostre o acesso ao editor Node-RED da EC2 B por um túnel SSH identificado como `localhost:1880`. Da EC2 A para a EC2 B, desenhe uma seta `TCP 5001 — medida h` saindo de `sensor.py` e outra `TCP 5002 — controle u` saindo de `atuador.py`. Da EC2 B de volta para `sensor.py`, desenhe uma seta `TCP 5001 — saída h`. Indique que as EC2 se comunicam por IP privado. Tipografia sans-serif grande e legível, cores azul para infraestrutura, verde-azulado para sensor e laranja para atuador. Setas sem cruzamentos, rótulos exatamente como especificados, sem elementos decorativos, sem sensores físicos, sem PID implementado.

## 2. Fluxo de nós do Node-RED

> Crie um diagrama de fluxo técnico vetorial, horizontal, em português, fundo branco, proporção 16:8, para uma apostila. À esquerda, duas entradas em linhas separadas: `TCP in sensor :5001` → `Validar medida / HELLO` e `TCP in atuador :5002` → `Validar u`. Ambas as linhas convergem no bloco central `Planta discreta`, cuja equação é `h[k+1] = a h[k] + K(1-a)u[k]`. Abaixo, dois nós `inject`: `Forçar h = 0` e `Forçar u = 10`, ambos conectados ao bloco central. À direita da planta, duas saídas: `TCP out — resposta ao sensor :5001` e `Debug — k, u, h`. Use setas com direção inequívoca. A medida h inicializa/corrige o estado; cada comando u avança uma amostra. Tipografia sans-serif grande e legível, caixas arredondadas discretas, sensor em verde-azulado, atuador em laranja e planta em azul. Não acrescente realimentação PID nem hardware físico.

## 3. Modelo discreto de nível (opcional)

> Crie um esquema de blocos de controle discreto, em português, fundo branco, proporção 16:6. À esquerda, a entrada `u[k]` (controle enviado pelo atuador). No centro, um bloco `Planta de nível: G(z) = K(1-a)z^-1 / (1-a z^-1)`, com `K=1`, `a=exp(-1/5)` e período de amostragem `Ts=1 s`. À direita, a saída `h[k+1]` enviada ao cliente sensor. Abaixo do bloco, mostre a equação `h[k+1] = a h[k] + K(1-a)u[k]`. Use setas da esquerda para a direita, texto matemático correto, sem bloco PID, sem tanque físico e sem elementos decorativos. Estilo vetorial didático e legível em página A4.
