import time
import re
import random
from datetime import datetime, timedelta

def sleep_between_requests(seconds):
     
    if isinstance(seconds, (tuple, list)):
        delay = random.uniform(seconds[0], seconds[1])
    else:
        delay = float(seconds)
    print(f"[utils] Durmiendo {delay:.2f} segundos...")
    time.sleep(delay)

def normalize_text(t: str):
    if not t:
        return ""
    return " ".join(t.lower().split())

def parse_hace_to_timedelta(text: str):
    if not text:
        return None
    text_low = text.lower()
    m = re.search(r'([0-9]+)\s*min', text_low)
    if m:
        return timedelta(minutes=int(m.group(1)))
    m = re.search(r'([0-9]+)\s*minuto', text_low)
    if m:
        return timedelta(minutes=int(m.group(1)))
    m = re.search(r'([0-9]+)\s*hora', text_low)
    if m:
        return timedelta(hours=int(m.group(1)))
    m = re.search(r'([0-9]+)\s*d[ií]a', text_low)
    if m:
        return timedelta(days=int(m.group(1)))
    if "hoy" in text_low:
        return timedelta(hours=0)
    return None

def within_last_24h(text_fecha: str) -> bool:
    td = parse_hace_to_timedelta(text_fecha)
    if td is None:
        return False
    return td <= timedelta(days=1)

def title_is_duplicate(title: str, seen_titles: set) -> bool:
    n = normalize_text(title)
    if n in seen_titles:
        return True
    seen_titles.add(n)
    return False
