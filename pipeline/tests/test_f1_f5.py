"""Checks for the 31.10.2026 fixes: F3 banned client names, F4 metrics matching, F1 editorial keys in the prompt tail. Run: python3 pipeline/tests/test_f1_f5.py"""
import os, sys, csv, tempfile, datetime as dt
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import rules_check, metrics_import as mi, editorial

ok = True
def t(name, cond):
    global ok; ok &= bool(cond); print(("PASS" if cond else "FAIL"), name)

# F3: every cluster name is rejected on both channels; an anonymised sentence passes the name check
base = "Ein Halbleiterhersteller hat uns 2024 eine Aufgabe gegeben. " * 12 + "Was ist bei Ihnen?"
for name in ["ZAMM", "Bogner", "Fixmer", "Promeda", "Hundt", "Kurzke", "Blauth", "Ponholzer", "Debuxx", "haussoft", "facilioo", "onOffice", "Immobilienvisionäre"]:
    v = rules_check.check(base.replace("Ein Halbleiterhersteller", f"Bei {name}"), "company")
    t(f"F3 rejects {name}", any(name.lower()[:5] in x.lower() for x in v))
t("F3 anonymised text passes the name rules", not [x for x in rules_check.check(base, "company") if x.startswith("\\b")])

# F4: matching order and ambiguity
plog = [{"post_id": "li-post-11", "channel": "linkedin", "date": "2026-10-19", "hook": "Dieses Schiff fährt noch? Legacy-Code auch?", "link": ""},
        {"post_id": "li-comp-12", "channel": "linkedin-company", "date": "2026-10-27", "hook": "A machine raises an alarm at 2:40 in the morning.", "link": ""},
        {"post_id": "li-post-32", "channel": "linkedin", "date": "2026-10-28", "hook": "Oracle behalten oder auf PostgreSQL wechseln?", "link": "https://www.linkedin.com/feed/update/urn:li:share:1/"}]
d = dt.date
t("F4 link wins", mi.pick(plog, d(2026, 1, 1), "", "https://www.linkedin.com/feed/update/urn:li:share:1")[0]["post_id"] == "li-post-32")
t("F4 title match", mi.pick(plog, None, mi.norm("Dieses Schiff fährt noch? Legacy-Code auch?")[:30], "")[0]["post_id"] == "li-post-11")
t("F4 exact date, no title (personal export)", mi.pick(plog, d(2026, 10, 19), "", "")[0]["post_id"] == "li-post-11")
amb = mi.pick(plog, d(2026, 10, 27), "", "")           # 27.10. company and 28.10. personal are within +/-1 day of each other
t("F4 exact date beats +-1 day", amb[0] and amb[0]["post_id"] == "li-comp-12")
amb2 = mi.pick(plog, d(2026, 10, 26), "", "")          # 26.10.: nothing exact; 27.10. within a day -> one candidate -> ok
t("F4 +-1 day with a single candidate", amb2[0] and amb2[0]["post_id"] == "li-comp-12")
plog2 = plog + [{"post_id": "li-post-99", "channel": "linkedin", "date": "2026-10-27", "hook": "Something else", "link": ""}]
r = mi.pick(plog2, d(2026, 10, 27), "", "")
t("F4 two posts on one day without channel -> ambiguous, not guessed", r[0] is None and "ambiguous" in r[1])
t("F4 channel hint resolves it", mi.pick(plog2, d(2026, 10, 27), "", "", "company")[0]["post_id"] == "li-comp-12")
r2 = mi.pick(plog, d(2026, 10, 27), "", "", "personal")   # no personal post on 27.10.; the 28.10. personal post is the only one within a day
t("F4 wrong channel never matches (falls to the personal post a day later)", r2[0] is not None and r2[0]["post_id"] == "li-post-32")
t("F4 channel hint from file name", mi.channel_hint("Content_AlpiType_company_2026.xlsx", "Sheet1") == "company" and mi.channel_hint("export.csv", "Top posts") == "")

# F4: a synthetic personal export (URL, date, numbers; no title) goes through the header mapper
with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="") as f:
    w = csv.writer(f); w.writerow(["Post URL", "Post publish date", "Impressions", "Reactions", "Comments", "Reposts"]); w.writerow(["https://x/1", "10/19/2026", "1200", "14", "3", "1"])
hi, m = mi.header_map(list(csv.reader(open(f.name))))
t("F4 header map finds link/date/impressions/reposts", hi == 0 and all(k in m for k in ("link", "date", "impressions", "reposts")))
os.unlink(f.name)

# F1: prompt tail carries the three editorial keys
t("F1 editorial keys", all(k in editorial.EDITORIAL_JSON for k in ("reader", "insight", "discussion_reason")))

# ---- 01.11.2026: S1 situation key, S4 proposal parsing, S5 weekly line with empty values
import health, mail_watch, re as _re
t("S1 situation in editorial JSON", '"situation"' in editorial.EDITORIAL_JSON)
body = 'Neuer Lead: Email: someone@example.com Seite: kontakt UTM: {"utm_source":"linkedin","utm_medium":"post"} IP: 1.2.3.4'
who = _re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", body)[0]; page = _re.search(r"Seite:\s*([\w-]+)", body)[1]; utm = _re.search(r'"utm_source":"([^"]*)"', body)[1]
t("S4 lead mail fields parsed", who == "someone@example.com" and page == "kontakt" and utm == "linkedin")
rows = health.weekly(4)
t("S5 four weekly rows", len(rows) == 4 and all(k in rows[0] for k in ("week", "posts", "comments", "visits", "contacts", "linkedin", "qualified")))
t("S5 missing comments stay empty, not zero", all(r["comments"] == "" or isinstance(r["comments"], int) for r in rows) and not any(r["comments"] == 0 and r["posts"] == 0 for r in rows))
print("ALL PASS (incl. S1/S4/S5)" if ok else "SOME FAILED"); sys.exit(0 if ok else 1)
