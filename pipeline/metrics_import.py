#!/usr/bin/env python3
"""LinkedIn analytics exports -> posts-log.csv (spec metrics-loop). Drop the XLSX/CSV files LinkedIn exports
(company page: Analytics > Content > Export; personal: post > View analytics > Export) into library/metrics/inbox/.
Each row is matched to a posts-log row by date (+/- 1 day) and the first 30 characters of the hook; impressions,
reactions, comments, reposts are written; matched files move to library/metrics/done/. Zero tokens."""
import csv, json, os, re, shutil, time, unicodedata
from datetime import datetime, timedelta
from common import CFG, LIB, read_csv, write_csv, log

INBOX, DONE = os.path.join(LIB, "metrics", "inbox"), os.path.join(LIB, "metrics", "done")
COLS = {"impressions": ["impressions", "impressionen"], "reactions": ["reactions", "reaktionen", "likes", "gefällt"], "comments": ["comments", "kommentare"],
        "reposts": ["reposts", "shares", "geteilt"], "clicks": ["clicks", "klicks"], "date": ["created date", "erstellungsdatum", "date", "datum", "post date"],
        "title": ["post title", "beitragstitel", "title", "titel", "commentary", "text"], "link": ["post link", "beitragslink", "link", "url"]}

def norm(s): return re.sub(r"\s+", " ", unicodedata.normalize("NFKD", (s or "")).encode("ascii", "ignore").decode().lower()).strip()

def tables(path):
    if path.lower().endswith((".xlsx", ".xlsm")):
        import openpyxl
        for ws in openpyxl.load_workbook(path, read_only=True, data_only=True).worksheets:
            yield ws.title, [[("" if v is None else str(v)) for v in row] for row in ws.iter_rows(values_only=True)]
    else:
        yield os.path.basename(path), list(csv.reader(open(path, newline="", encoding="utf-8-sig", errors="replace")))

def header_map(rows):
    for i, row in enumerate(rows[:40]):
        h = [norm(c) for c in row]
        if any("impression" in c for c in h):
            m = {}
            for key, names in COLS.items():
                for j, c in enumerate(h):
                    if any(n in c for n in names) and key not in m: m[key] = j
            return i, m
    return None, {}

def parse_date(s):
    for f in ("%Y-%m-%d", "%d.%m.%Y", "%m/%d/%Y", "%Y-%m-%d %H:%M:%S", "%d.%m.%Y %H:%M", "%b %d, %Y"):
        try: return datetime.strptime(s.strip()[:len(f) + 4], f).date()
        except ValueError: pass
    return None

def num(s):
    s = re.sub(r"[^\d]", "", s or ""); return s or ""

DOWNLOADS, SEEN = os.path.expanduser("~/Downloads"), os.path.join(LIB, "metrics", ".seen.json")

def scan_downloads():
    """LinkedIn exports land in ~/Downloads: a spreadsheet from the last 30 days with an impressions header is copied into
    the inbox once (name + mtime remembered); the original stays. Saves the step of moving the file by hand."""
    if not os.path.isdir(DOWNLOADS): return
    try: seen = json.load(open(SEEN))
    except (FileNotFoundError, json.JSONDecodeError): seen = {}
    for f in os.listdir(DOWNLOADS):
        p = os.path.join(DOWNLOADS, f)
        if f.startswith(".") or not f.lower().endswith((".xlsx", ".xlsm", ".csv")) or not os.path.isfile(p): continue
        key = f"{f}:{int(os.path.getmtime(p))}"
        if key in seen or time.time() - os.path.getmtime(p) > 30 * 86400 or os.path.getsize(p) > 20 * 1024 * 1024: continue
        seen[key] = 1
        try:
            if any(header_map(rows)[0] is not None for _, rows in tables(p)): shutil.copy2(p, os.path.join(INBOX, f)); log(f"Downloads: {f} looks like a LinkedIn export, taken into the inbox")
        except Exception as e: log(f"Downloads: {f} not readable: {str(e)[:80]}")
    json.dump(seen, open(SEEN, "w"))

def main():
    os.makedirs(INBOX, exist_ok=True); os.makedirs(DONE, exist_ok=True); scan_downloads()
    plog, lf = read_csv(CFG["posts_log"]); changed = 0
    for f in sorted(os.listdir(INBOX)):
        p = os.path.join(INBOX, f)
        if not os.path.isfile(p) or f.startswith("."): continue
        hits = 0
        for sheet, rows in tables(p):
            hi, m = header_map(rows)
            if hi is None or "impressions" not in m: continue
            for row in rows[hi + 1:]:
                if len(row) <= m["impressions"] or not num(row[m["impressions"]]): continue
                d = parse_date(row[m["date"]]) if "date" in m and m["date"] < len(row) else None
                title = norm(row[m["title"]])[:30] if "title" in m and m["title"] < len(row) else ""
                link = row[m["link"]] if "link" in m and m["link"] < len(row) else ""
                for l in plog:
                    ld = parse_date(l["date"]); near = d and ld and abs((d - ld).days) <= 1
                    same = title and norm(l["hook"])[:30] == title or (link and l.get("link") and link.strip() == l["link"].strip())
                    if same or (near and title and norm(l["hook"])[:15] == title[:15]):
                        for k in ("impressions", "reactions", "comments", "reposts"):
                            if k in m and m[k] < len(row) and num(row[m[k]]) and k in lf: l[k] = num(row[m[k]])
                        if link and not l.get("link"): l["link"] = link.strip()
                        l["note"] = f"metrics {datetime.now():%Y-%m-%d} from {f}. " + l.get("note", ""); hits += 1; changed += 1; break
        log(f"{f}: {hits} rows matched"); shutil.move(p, os.path.join(DONE, f))
    if changed: write_csv(CFG["posts_log"], plog, lf); log("posts-log.csv updated")

if __name__ == "__main__": main()
