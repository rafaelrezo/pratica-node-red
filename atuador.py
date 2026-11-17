"""Cliente TCP do atuador: envia amostras de controle para o Node-RED."""

import argparse
import math
import socket


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host", help="IP privado da EC2 do Node-RED")
    parser.add_argument("--porta", type=int, default=5002)
    args = parser.parse_args()

    try:
        with socket.create_connection((args.host, args.porta), timeout=10) as sock:
            print(f"Conectado a {args.host}:{args.porta}. Cada valor aplica um passo de 1 s; 'sair' encerra.")
            while True:
                try:
                    texto = input("controle u > ").strip()
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
                    print(f"u={valor:g} enviado")
                except OSError as erro:
                    print(f"Falha ao enviar: {erro}")
                    break
    except OSError as erro:
        parser.exit(1, f"Não foi possível conectar: {erro}\n")


if __name__ == "__main__":
    main()
