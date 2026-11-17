"""Cliente TCP do sensor: define o nível medido e recebe a saída da planta."""

import argparse
import math
import socket
import threading


def receber(sock: socket.socket) -> None:
    try:
        with sock.makefile("r", encoding="utf-8", newline="\n") as entrada:
            for linha in entrada:
                print(f"\n[planta] {linha.strip()}", flush=True)
    except OSError as erro:
        print(f"\n[conexão encerrada] {erro}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host", help="IP privado da EC2 do Node-RED")
    parser.add_argument("--porta", type=int, default=5001)
    args = parser.parse_args()

    try:
        with socket.create_connection((args.host, args.porta), timeout=10) as sock:
            sock.settimeout(None)
            print(f"Conectado a {args.host}:{args.porta}. Digite uma medida de nível ou 'sair'.")
            sock.sendall(b"HELLO\n")  # registra esta conexão no fluxo Node-RED
            leitor = threading.Thread(target=receber, args=(sock,), daemon=True)
            leitor.start()
            while True:
                try:
                    texto = input("nível medido > ").strip()
                except (EOFError, KeyboardInterrupt):
                    break
                if texto.lower() in {"sair", "exit", "q"}:
                    break
                try:
                    valor = float(texto)
                    if not math.isfinite(valor) or valor < 0:
                        raise ValueError
                except ValueError:
                    print("Informe um número finito maior ou igual a zero (use ponto decimal).")
                    continue
                try:
                    sock.sendall(f"{valor}\n".encode("utf-8"))
                except OSError as erro:
                    print(f"Falha ao enviar: {erro}")
                    break
    except OSError as erro:
        parser.exit(1, f"Não foi possível conectar: {erro}\n")


if __name__ == "__main__":
    main()
