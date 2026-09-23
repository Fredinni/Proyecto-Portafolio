#!/usr/bin/env python3
"""Initialize the isolated DVWA lab database once; never reset existing data."""
import http.cookiejar
import re
import subprocess
import sys
import urllib.parse
import urllib.request


def tables():
    command = [
        "docker", "exec", "kronos-dmz-db-1", "sh", "-c",
        'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mariadb -uroot -N -e "SHOW TABLES IN dvwa"',
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=20)
    if result.returncode:
        raise RuntimeError("DVWA database is not reachable")
    return set(result.stdout.split())


if {"users", "guestbook"} <= tables():
    print("DVWA_DB_ALREADY_INITIALIZED")
    sys.exit(0)
if tables():
    raise RuntimeError("DVWA database contains partial/unexpected tables; no reset attempted")

opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
)
url = "http://192.168.20.50/setup.php"
with opener.open(url, timeout=15) as response:
    html = response.read().decode("utf-8", "replace")
match = re.search(r"name=['\"]user_token['\"]\s+value=['\"]([a-f0-9]+)['\"]", html)
if not match:
    raise RuntimeError("DVWA setup token not found")
payload = urllib.parse.urlencode({
    "create_db": "Create / Reset Database", "user_token": match.group(1)
}).encode()
with opener.open(urllib.request.Request(url, data=payload), timeout=60) as response:
    response.read()
if not {"users", "guestbook"} <= tables():
    raise RuntimeError("DVWA setup POST did not create expected tables")
print("DVWA_DB_INITIALIZED; credentials and application login require separate validation")
