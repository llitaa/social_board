#!/usr/bin/env python3
"""Fold pulled decisions into the truth on the Mac:
- post decisions -> content-plan.csv status (approved / change / skipped / posted) and posts-log.csv on posted;
  a text edited on the card (decision post with text) replaces the draft text, the old text stays as <id>.vN.txt
- scheduled rows whose slot has passed -> posted (LinkedIn published them itself; the board stops showing them)
- comment decisions -> library/log/comment-log.csv
- photo / upload / memo decisions -> library/log/board-events.csv (processed by photo_index / transcribe)
Idempotent: remembers the last processed line per decisions file in library/log/.applied.json
"""
import csv, glob, json, os, re, shutil
from datetime import datetime
from common import CFG, BOARD_LOCAL, LIB, USER, boards, profile, read_csv, write_csv, jload, jdump, log, resolve

STATE = os.path.join(LIB, "log", ".applied.json")
LOGDIR = os.path.join(LIB, "log")

def append(path, fields, row):
    new = not os.path.isfile(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if new: w.writeheader()
        w.writerow({k: row.get(k, "") for k in fields})

def write_edit(r, text, ts):
    """Anton's final text from the card: becomes the draft text; the previous one is kept as a version."""
    tp = resolve(r.get("caption_ref", ""))
    if not tp or not os.path.isfile(tp): return False
    old = open(tp, encoding="utf-8").read().strip()
    if old == text.strip(): return False
    base = os.path.splitext(tp)[0]; mp = base + ".json"
    meta = jload(mp, {"versions": []}); ver = len(meta.get("versions", [])) + 1
    shutil.copy2(tp, f"{base}.v{ver}.txt"); meta.setdefault("versions", []).append({"v": ver, "note": "edited on the card", "ts": ts})
    open(tp, "w", encoding="utf-8").write(text.strip() + "\n"); jdump(mp, meta)
    return True

def _naive(ts):
    """Decision timestamps come with and without a zone (server: +01:00, Mac: none): compare them as wall-clock time."""
    return datetime.fromisoformat(ts).replace(tzinfo=None)

def set_day(day):
    """The posting day of another person's board (setup step 9): users/<slug>/config.yaml slots.personal.days. Anton's board keeps its config."""
    if not USER or day not in ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"): return
    import yaml
    uc = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "users", USER, "config.yaml")
    cfg = (yaml.safe_load(open(uc)) or {}) if os.path.isfile(uc) else {}
    cfg.setdefault("slots", {}).setdefault("personal", {})["days"] = [day]
    yaml.safe_dump(cfg, open(uc, "w"), allow_unicode=True, sort_keys=False); log("posting day", day)

def promote_scheduled(plan, plog):
    """A post Anton scheduled in LinkedIn is posted once its slot has passed: the board must not show it as open."""
    now = datetime.now(); n = 0
    for r in plan:
        if r["status"] != "scheduled" or not r["channel"].startswith("linkedin"): continue
        p = (r.get("planned") or "").strip()
        if len(p) == 10: p += " 23:59"
        try: w = datetime.strptime(p[:16], "%Y-%m-%d %H:%M")
        except ValueError: continue
        if w <= now:
            r["status"] = "posted"; r["notes"] = f"[posted by LinkedIn schedule {w:%d.%m. %H:%M}] " + r.get("notes", ""); n += 1
            cid = "-".join(os.path.basename(r.get("caption_ref", "")).split("-")[0:3])
            for l in plog:
                if l["post_id"] == cid and not (l.get("note") or "").upper().startswith("POSTED"): l["note"] = f"POSTED (LinkedIn schedule) {w:%d.%m.%Y %H:%M}. " + (l.get("note") or "")
    return n

def situation_of(card, plan):
    """editorial.situation from the draft JSON of this card (S1, 01.11.2026); empty when the draft has none."""
    row = next((r for r in plan if r["id"] == (card or {}).get("plan_row")), None)
    tp = resolve(row.get("caption_ref", "")) if row else ""
    mp = os.path.splitext(tp)[0] + ".json" if tp else ""
    try: return str((json.load(open(mp, encoding="utf-8")).get("editorial") or {}).get("situation") or "")
    except Exception: return ""

def main():
    os.makedirs(LOGDIR, exist_ok=True)
    done = jload(STATE, {})
    plan, pf = read_csv(CFG["content_plan"]); plog, lf = read_csv(CFG["posts_log"])
    cards = {c["id"]: c for c in jload(os.path.join(BOARD_LOCAL, "cards.json"), [])}
    changed_plan = changed_log = False; last_ts = jload(os.path.join(BOARD_LOCAL, "applied.json"), {}).get("until", "")
    files = [(os.path.basename(f), f) for f in sorted(glob.glob(os.path.join(BOARD_LOCAL, "decisions", "*.jsonl")))] + \
            [("local/" + os.path.basename(f), f) for f in sorted(glob.glob(os.path.join(BOARD_LOCAL, "decisions-local", "*.jsonl")))]   # voice notes transcribed on the Mac
    for key, f in files:
        lines = open(f, encoding="utf-8").read().splitlines()
        start = done.get(key, 0); ok_upto = start
        for ln in lines[start:]:
            try: d = json.loads(ln)
            except json.JSONDecodeError: break   # a half-written last line: stop here, read it again next run
            ok_upto += 1
            t = d.get("type")
            try: last_ts = d["ts"] if not last_ts or _naive(d.get("ts", "")) > _naive(last_ts) else last_ts
            except (ValueError, KeyError): pass
            if t == "post":
                cid = d["card_id"]; card = cards.get(cid, {})
                if not card:   # the card left cards.json (aged off, renamed): find the plan row by the same id derivation cards.py uses
                    for r in plan:
                        if r.get("caption_ref") and "-".join(os.path.basename(r["caption_ref"]).split("-")[0:3]) == cid: card = {"plan_row": r["id"], "status": r["status"]}; break
                if d["decision"] == "order":   # the listed cards take their existing slots in the new sequence (rows Anton scheduled in LinkedIn are never moved)
                    ids = [x for x in d.get("order", []) if x in cards and cards[x].get("status") != "scheduled"]
                    byrow = {x: next((r for r in plan if r["id"] == cards[x].get("plan_row")), None) for x in ids}
                    ids = [x for x in ids if byrow[x] and byrow[x].get("planned")]
                    free = sorted(byrow[x]["planned"] for x in ids)
                    for i, x in enumerate(ids):
                        if byrow[x]["planned"] != free[i]: byrow[x]["planned"] = free[i]; byrow[x]["notes"] = f"[board {d['ts'][:16]} reordered to {free[i]}] " + byrow[x].get("notes", ""); changed_plan = True
                    append(os.path.join(LOGDIR, "post-decisions.csv"), ["ts", "card_id", "decision", "option", "note", "reason", "url", "edited", "when"], {**d, "note": " ".join(ids)}); continue
                status = {"post": "approved", "schedule": "approved", "change": "change", "skip": "skipped", "posted": "posted", "unschedule": "draft", "photo_next": None}.get(d["decision"], "")
                if status == "": continue
                for r in plan:
                    if r["id"] == card.get("plan_row"):
                        if status: r["status"] = status
                        if d["decision"] == "post": r["planned"] = d["ts"][:16].replace("T", " ")          # Post now: the row's slot is now, publish.py takes it in this run
                        if d["decision"] == "schedule" and d.get("when"): r["planned"] = d["when"][:16].replace("T", " ")
                        if d["decision"] == "unschedule": r["notes"] = f"[board {d['ts'][:16]} unscheduled] " + r.get("notes", "")
                        if d["decision"] == "photo_next": r["notes"] = f"[board {d['ts'][:16]} photo: next] " + r.get("notes", "")
                        if d.get("note"): r["notes"] = f"[board {d['ts'][:16]} {d['decision']}: {d['note']}] " + r.get("notes", "")
                        if d.get("reason"): r["notes"] = f"[board skip: {d['reason']}] " + r.get("notes", "")
                        if d.get("text") and status in ("approved", "posted") and write_edit(r, d["text"], d["ts"]): r["notes"] = f"[board {d['ts'][:16]} edited on the card] " + r.get("notes", ""); d["edited"] = "yes"
                        changed_plan = True
                if status == "posted":
                    hit = False; sit = situation_of(card, plan)
                    for r in plog:
                        if r["post_id"] == cid:
                            r["note"] = f"POSTED via {d.get('via', 'board')} {d['ts'][:10]}. " + r.get("note", "")
                            if d.get("url"): r["link"] = d["url"]
                            if sit and not r.get("situation"): r["situation"] = sit
                            changed_log = hit = True
                    if not hit:   # drafts have no posts-log row yet: create it (21.10.: server-published posts were invisible to metrics and featured)
                        row = next((r for r in plan if r["id"] == card.get("plan_row")), None)
                        if row:
                            tp = resolve(row.get("caption_ref", "")); hook = open(tp, encoding="utf-8").readline().strip()[:120] if tp and os.path.isfile(tp) else ""
                            plog.append({"date": (row.get("planned") or d["ts"])[:10], "channel": row["channel"], "post_id": cid, "hook": hook, "type": row.get("format", ""), "language": row.get("language", ""),
                                         "link": d.get("url", ""), "situation": sit, "note": f"POSTED via {d.get('via', 'board')} {d['ts'][:10]}"}); changed_log = True
                if card and status: card["status"] = status
                append(os.path.join(LOGDIR, "post-decisions.csv"), ["ts", "card_id", "decision", "option", "note", "reason", "url", "edited", "when"], d)
            elif t == "comment":
                append(os.path.join(LOGDIR, "comment-log.csv"), ["ts", "card_id", "decision", "reason"], d)
            elif t == "external":   # a post Anton published in LinkedIn himself, logged on the board: Published is complete only with it
                pid = d.get("post_id") or f"li-ext-{d['ts'][:10].replace('-', '')}"
                if not any(r["post_id"] == pid for r in plog):
                    plog.append({"date": d.get("date") or d["ts"][:10], "channel": "linkedin-company" if d.get("channel") == "company" else "linkedin", "post_id": pid,
                                 "hook": (d.get("hook") or "")[:120], "link": d.get("url", ""), "note": f"POSTED by Anton in LinkedIn, logged on the board {d['ts'][:16].replace('T', ' ')}"}); changed_log = True
                append(os.path.join(LOGDIR, "board-events.csv"), ["ts", "type", "id", "decision", "files", "file", "note", "answer", "expiry", "review", "card_id"], {**d, "id": pid, "note": d.get("hook", "")})
            elif t == "metrics":   # numbers Anton typed on the board for one published post
                for r in plog:
                    if r["post_id"] == d.get("post_id"):
                        for k in ("impressions", "reactions", "comments"):
                            if d.get(k) not in (None, ""): r[k] = str(d[k])
                        r["note"] = f"metrics board {d['ts'][:16].replace('T', ' ')}. " + (r.get("note") or ""); changed_log = True
                append(os.path.join(LOGDIR, "board-events.csv"), ["ts", "type", "id", "decision", "files", "file", "note", "answer", "expiry", "review", "card_id"],
                       {**d, "id": d.get("post_id", ""), "note": " ".join(f"{k}={d[k]}" for k in ("impressions", "reactions", "comments") if d.get(k) not in (None, ""))})
            elif t == "profile_visits":   # S3: weekly sum of profile visits, typed by Anton on the board (no names, no attribution)
                pw = os.path.expanduser(CFG.get("profile_weekly", "~/dev/campaign/profile-weekly.csv"))
                rows, f = read_csv(pw) if os.path.isfile(pw) else ([], ["week", "visits", "entered_at"])
                rows = [r for r in rows if r.get("week") != d.get("week")] + [{"week": d.get("week", ""), "visits": str(d.get("visits", "")), "entered_at": d["ts"][:16]}]
                rows.sort(key=lambda r: r.get("week", "")); write_csv(pw, rows, f or ["week", "visits", "entered_at"]); log("profile visits", d.get("week"), d.get("visits"))
            elif t == "inbound":   # S4: a proposed contact (lead mail from alpitype.de) confirmed into inbound-log or dropped; the source is what the form said
                st = jload(os.path.join(LIB, "inbound", "state.json"), {}); st[d.get("id", "")] = {"state": d.get("decision"), "ts": d["ts"]}; jdump(os.path.join(LIB, "inbound", "state.json"), st)
                if d.get("decision") == "confirm":
                    ib = os.path.expanduser(CFG.get("inbound_log", "~/dev/campaign/inbound-log.csv"))
                    rows, f = read_csv(ib) if os.path.isfile(ib) else ([], ["date", "source", "who", "what", "qualified", "next"])
                    rows.append({"date": (d.get("date") or d["ts"])[:10], "source": d.get("source") or "website form", "who": d.get("who", ""), "what": d.get("what", ""), "qualified": d.get("qualified", ""), "next": d.get("next", "")})
                    write_csv(ib, rows, f or ["date", "source", "who", "what", "qualified", "next"]); log("inbound confirmed", d.get("who"))
            elif t == "profile_confirm":   # onboarding: the person corrected and confirmed the profile proposal -> facts for drafts, positioning, inventory (onboard.py)
                pf = os.path.join(LIB, "profile.json"); pr = jload(pf, {})
                for k in ("role", "company", "website", "audience", "offer", "goal", "tone", "facts", "words", "examples", "linkedin"):
                    if k in d: pr[k] = str(d[k])[:6000]
                for k in ("topics", "avoid"):
                    if k in d: pr[k] = [str(x)[:160] for x in (d[k] if isinstance(d[k], list) else str(d[k]).splitlines()) if str(x).strip()][:20]
                if isinstance(d.get("style"), dict): pr["style"] = {k: str(v)[:20] for k, v in d["style"].items() if k in ("register", "length", "question")}
                if d.get("day"): pr["day"] = str(d["day"])[:3]; set_day(pr["day"])
                pr["confirmed"] = True; pr["confirmed_at"] = d["ts"][:16]; jdump(pf, pr); jdump(os.path.join(BOARD_LOCAL, "profile.json"), pr)
                import onboard; onboard.write_facts(pr); log("profile confirmed")
            elif t == "profile_save":   # Mein Profil (04.11.): the person changed facts, topics, tone or sharing default; new topics go straight into the inventory, no model call
                pf = os.path.join(LIB, "profile.json"); pr = jload(pf, {}); before = [x.strip().lower() for x in pr.get("topics", [])]
                for k in ("role", "company", "website", "audience", "offer", "goal", "tone", "facts", "words", "examples", "linkedin"):
                    if k in d: pr[k] = str(d[k])[:8000]
                if d.get("day"): pr["day"] = str(d["day"])[:3]; set_day(pr["day"])
                for k in ("topics", "avoid"):
                    if k in d: pr[k] = [str(x).strip()[:160] for x in (d[k] if isinstance(d[k], list) else str(d[k]).splitlines()) if str(x).strip()][:20]
                if isinstance(d.get("style"), dict): pr["style"] = {k: str(v)[:20] for k, v in d["style"].items() if k in ("register", "length", "question")}
                if "share_default" in d: pr["share_default"] = bool(d["share_default"])
                pr["saved_at"] = d["ts"][:16]; jdump(pf, pr); jdump(os.path.join(BOARD_LOCAL, "profile.json"), pr)
                if pr.get("confirmed"):
                    import onboard; onboard.write_facts(pr)
                    new = [x for x in pr.get("topics", []) if x.strip().lower() not in before]
                    if new:
                        import inventory as inv_
                        rows = inv_.load(); have = {r["topic"].lower() for r in rows}
                        for x in new:
                            if x.lower() in have: continue
                            rows.append({"id": f"t{len(rows) + 1:03d}", "pillar": "case", "channel": "personal", "topic": x[:80], "angle": x[:300], "source": "profile: Themen, selbst eingetragen", "tags": "", "status": "unused", "used_in": "", "added": d["ts"][:10]})
                        inv_.save(rows); log(f"profile: {len(new)} topic(s) added to the inventory")
                log("profile saved")
            elif t == "proposal":   # shared material of another board offered on a card (match.py): a photo (key = card id) or a thought from a post, website or memo (key = card id + "#t"); accept = on the card / as a sentence in the text, with a credit line; decline = remembered
                key = d.get("card_id", ""); cid = key.split("#")[0]
                pf = os.path.join(BOARD_LOCAL, "proposals.json"); props = jload(pf, {}); p = props.get(key, {})
                p["state"] = "accept" if d.get("decision") == "accept" else "decline"; p["decided"] = d["ts"][:16]; props[key] = p; jdump(pf, props)
                if p["state"] == "accept" and p.get("kind") == "text":
                    try:
                        pr_ = next((r for r in plan if r.get("caption_ref") and "-".join(os.path.basename(r["caption_ref"]).split("-")[0:3]) == cid), None)
                        tp = resolve(pr_.get("caption_ref", "")) if pr_ else ""; txt = open(tp, encoding="utf-8").read().rstrip() if tp and os.path.isfile(tp) else ""
                        line = (p.get("line") or "").strip(); credit = f"Gedanke von {p.get('owner_name', '')}" + (f": {p['url']}" if p.get("url") else "")
                        if pr_ and txt and line and line not in txt:
                            m = re.search(r"(\n\s*#\w[\w\s#]*)$", txt); body = txt[:m.start()].rstrip() if m else txt; tail = txt[m.start():].lstrip("\n") if m else ""
                            write_edit(pr_, body + "\n\n" + line + "\n\n" + credit + ("\n" + tail if tail else "\n"), d["ts"])
                            pr_["notes"] = f"[board {d['ts'][:16]} shared text {p.get('item', '')} von {p.get('owner_name', '')}] " + pr_.get("notes", ""); changed_plan = True
                            ob = boards().get(p.get("owner", ""), {})
                            if ob: append(os.path.join(ob["lib"], "log", "shared-uses.csv"), ["ts", "photo", "used_by", "used_by_name", "card"], {"ts": d["ts"][:16], "photo": "Text: " + (p.get("title") or "")[:60], "used_by": USER or "anton", "used_by_name": profile()["name"], "card": cid})
                            log("text proposal accepted", cid, p.get("item"))
                    except Exception as e: log("text proposal accept failed", repr(e)[:300])
                elif p["state"] == "accept" and p.get("file") and os.path.isfile(p["file"]):
                    try:
                        import photo_index as ph
                        row = ph.ingest(p["file"], note=f"von {p.get('owner_name', '')}", status="ready", copy=True, src="shared")
                        if not row: row = next((x for x in ph.read_index() if os.path.basename(x["file"]) == os.path.basename(p["file"])), None)
                        pr_ = next((r for r in plan if r.get("caption_ref") and "-".join(os.path.basename(r["caption_ref"]).split("-")[0:3]) == cid), None)
                        if row and pr_:
                            rows = ph.read_index()
                            for x in rows:
                                if x["id"] == row["id"]: x["owner"] = p.get("owner", ""); x["share"] = ""
                            ph.write_index(rows)
                            ph.set_card_image(pr_, row, f"Foto von {p.get('owner_name', '')}")
                            tp = resolve(pr_.get("caption_ref", "")); txt = open(tp, encoding="utf-8").read().rstrip() if tp and os.path.isfile(tp) else ""
                            credit = f"Foto: {p.get('owner_name', '')}"
                            if txt and credit not in txt:
                                m = re.search(r"(\n\s*#\w[\w\s#]*)$", txt); new = (txt[:m.start()].rstrip() + "\n\n" + credit + "\n" + txt[m.start():].lstrip("\n")) if m else txt + "\n\n" + credit + "\n"
                                write_edit(pr_, new, d["ts"])
                            pr_["notes"] = f"[board {d['ts'][:16]} shared photo {row['id']} von {p.get('owner_name', '')}] " + pr_.get("notes", ""); changed_plan = True
                            ob = boards().get(p.get("owner", ""), {})
                            if ob: append(os.path.join(ob["lib"], "log", "shared-uses.csv"), ["ts", "photo", "used_by", "used_by_name", "card"], {"ts": d["ts"][:16], "photo": row["id"], "used_by": USER or "anton", "used_by_name": profile()["name"], "card": cid})
                            log("proposal accepted", cid, row["id"])
                    except Exception as e: log("proposal accept failed", repr(e)[:300])
            elif t == "memo_share":   # a memo offered to the other boards (04.11.): memos/index.csv share = network; match.py reads it
                mf = os.path.join(LIB, "memos", "index.csv"); mrows, mfields = read_csv(mf)
                mfields = list(mfields) + (["share"] if "share" not in mfields else [])
                for m in mrows:
                    m.setdefault("share", "")
                    if m.get("id") == d.get("id"): m["share"] = "network" if d.get("decision") == "share" else ""
                write_csv(mf, mrows, mfields); log("memo share", d.get("id"), d.get("decision"))
            elif t in ("photo", "upload", "memo", "settings", "answer", "profile", "profile_save", "invite", "team"):
                append(os.path.join(LOGDIR, "board-events.csv"), ["ts", "type", "id", "decision", "files", "file", "note", "answer", "expiry", "review", "card_id"],
                       {**d, "files": ",".join(d.get("files", []) or [])})
        done[key] = ok_upto
    if promote_scheduled(plan, plog): changed_plan = changed_log = True
    if changed_plan: write_csv(CFG["content_plan"], plan, pf); log("content-plan.csv updated")
    if changed_log: write_csv(CFG["posts_log"], plog, lf); log("posts-log.csv updated")
    jdump(os.path.join(BOARD_LOCAL, "cards.json"), list(cards.values()))
    # everything up to the newest applied decision is now in the CSVs; the board drops overlay entries older than this
    if last_ts: jdump(os.path.join(BOARD_LOCAL, "applied.json"), {"until": last_ts, "at": datetime.now().isoformat(timespec="seconds")})
    jdump(STATE, done); log("decisions applied", "until", last_ts or "-")

if __name__ == "__main__": main()
