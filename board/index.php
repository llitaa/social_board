<?php header('Cache-Control: no-store'); header('X-Robots-Tag: noindex, nofollow'); require __DIR__ . '/auth.php'; auth_gate(); $ME = auth_user(); ?>
<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Board">
<meta name="theme-color" content="#0f3a50">
<link rel="apple-touch-icon" href="icon.png">
<title>Board</title>
<style>
:root{--c:#20B8D0;--d:#0f3a50;--t:#1f2d3a;--m:#5a6b7a;--bg:#f2f9fb;--b:#d6e2ea;--tint:#BEF7FF;--warn:#fff4e0}
*{box-sizing:border-box}
html,body{margin:0;background:#f4f6f8;color:var(--t);font:16px/1.45 -apple-system,"Helvetica Neue",Arial,sans-serif;-webkit-text-size-adjust:100%}
header{position:sticky;top:0;z-index:5;background:#fff;border-bottom:2px solid var(--c);padding:env(safe-area-inset-top) 0 0}
.top{display:flex;align-items:center;justify-content:space-between;padding:10px 14px 6px;max-width:1240px;margin:0 auto}
.top h1{font-size:17px;margin:0;color:var(--d)}
.top .sub{font-size:12px;color:var(--m)}
.tabs{display:flex;max-width:1240px;margin:0 auto}
.tabs button{flex:1;border:0;background:none;padding:8px 0 10px;font-size:14px;color:var(--m);border-bottom:3px solid transparent;cursor:pointer}
.tabs button.on{color:var(--d);font-weight:600;border-bottom-color:var(--d)}
main{max-width:1240px;margin:0 auto;padding:12px 14px 90px;overflow-x:hidden}
.items{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.item{position:relative;border:1px solid var(--b);border-radius:12px;overflow:hidden;background:#fff;cursor:pointer;-webkit-user-select:none;user-select:none;-webkit-touch-callout:none;touch-action:pan-y}
.item img,.item .noimg{width:100%;aspect-ratio:1;object-fit:cover;display:block;background:#dfe6ea;pointer-events:none;-webkit-user-drag:none}
.item .st{position:absolute;right:8px;top:8px;width:12px;height:12px;border-radius:50%;border:2px solid #fff;box-shadow:0 0 0 1px rgba(0,0,0,.15)}
.item .handle{position:absolute;left:6px;top:6px;background:rgba(255,255,255,.9);color:var(--d);border-radius:6px;padding:2px 6px;font-size:13px;cursor:grab;display:none}
.item .meta{padding:8px 10px 0;font-size:12px;color:var(--m)}
.item .ex{padding:4px 10px 10px;font-size:13px;line-height:1.35;color:var(--t);display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.item.locked{opacity:.8}
.item.drag{z-index:5;box-shadow:0 10px 30px rgba(0,0,0,.3);transition:none}
body.dragging{-webkit-user-select:none;user-select:none}
.sheet{position:fixed;inset:0;background:rgba(15,58,80,.55);z-index:8;overflow:auto;-webkit-overflow-scrolling:touch;padding:8px 8px 100px}
.sheetin{max-width:1000px;margin:0 auto}
.sheetbar{position:sticky;top:0;z-index:2;display:flex;justify-content:space-between;align-items:center;background:#fff;border-radius:12px 12px 0 0;padding:8px 12px;border-bottom:1px solid var(--b);font-size:13px;color:var(--m)}
.sheet .card{margin:0;border-radius:0 0 12px 12px}
body.noscroll{overflow:hidden}
.rec,.recbar{z-index:9}
@media(min-width:960px){.items{grid-template-columns:repeat(4,1fr)}.item .handle{display:block}}
.tile{position:relative;aspect-ratio:1;border-radius:10px;overflow:hidden;background:#dfe6ea;cursor:pointer;-webkit-tap-highlight-color:transparent}
.tile img,.tile .noimg{width:100%;height:100%;object-fit:cover;display:block}
.tile .dy{position:absolute;left:5px;top:5px;font-size:11px;font-weight:700;background:rgba(255,255,255,.92);color:var(--d);border-radius:6px;padding:1px 5px}
.tile .st{position:absolute;right:6px;top:6px;width:11px;height:11px;border-radius:50%;border:2px solid #fff;box-shadow:0 0 0 1px rgba(0,0,0,.15)}
.tile span.co{position:absolute;left:5px;bottom:5px;font-size:11px;font-weight:800;background:var(--d);color:#fff;border-radius:6px;padding:1px 6px}
.tile .lk{position:absolute;right:5px;bottom:5px;font-size:10px;background:#0a66c2;color:#fff;border-radius:6px;padding:1px 5px}
.tile.locked{opacity:.75}
.tile .mv{position:absolute;left:0;right:0;bottom:0;display:flex;background:rgba(15,58,80,.85)}
.tile .mv button{flex:1;border:0;background:none;color:#fff;font-size:16px;padding:6px 0;cursor:pointer}
.tile .mv button:disabled{opacity:.25}
@media(min-width:960px){.tiles{grid-template-columns:repeat(8,1fr)}}
.card{border:1px solid var(--b);border-radius:12px;background:#fff;margin:0 0 14px;overflow:hidden;scroll-margin-top:104px}
input[type=datetime-local]{width:100%;border:1px solid var(--b);border-radius:8px;padding:9px;font:inherit;font-size:15px;background:#fff}
.imgtools{display:flex;gap:6px;padding:8px 14px 0;flex-wrap:wrap;align-items:center}
.lbl{display:inline-block;border:1px solid var(--d);background:#fff;color:var(--d);border-radius:6px;padding:5px 9px;font-size:13px;cursor:pointer}
.card.done{opacity:.6}
.who{display:flex;align-items:center;gap:10px;padding:12px 14px 0}
.ava{width:40px;height:40px;border-radius:50%;background:var(--d);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:15px;flex:0 0 40px}
.ava.co{border-radius:8px;background:var(--c)}
.who .n{font-weight:600;font-size:15px;line-height:1.2}
.who .s{font-size:12px;color:var(--m)}
.pill{display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;background:var(--bg);color:var(--d);border:1px solid var(--b);white-space:nowrap}
.pill.ok{background:var(--tint)}
.pill.li{background:#e8f1fb;border-color:#c6daf0;color:#1d4e89}
.pill.warn{background:var(--warn);border-color:#f3d9a4;color:#7a4b00}
.pill.todo{background:var(--d);color:#fff;border-color:var(--d)}
.txt{white-space:pre-wrap;font-size:15px;line-height:1.5;padding:10px 14px 4px}
.img{margin:8px 0 0;background:#000;position:relative}
.img.busy img{opacity:.35;filter:grayscale(.6)}
.spin{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;color:#fff;font-size:14px;font-weight:600;text-shadow:0 1px 6px rgba(0,0,0,.6)}
.spin i{width:44px;height:44px;border-radius:50%;border:4px solid rgba(255,255,255,.35);border-top-color:#fff;animation:sp .9s linear infinite}
@keyframes sp{to{transform:rotate(360deg)}}
.txt.busy{opacity:.45}
.img img{display:block;width:100%;height:auto;max-height:70vh;object-fit:contain}
.act{padding:12px 14px 14px;border-top:1px solid var(--b);background:#fff}
textarea,input[type=text],input[type=url],input[type=number],input[type=date],select{width:100%;border:1px solid var(--b);border-radius:8px;padding:9px;font:inherit;font-size:15px;background:#fff;min-width:0}
.pipe .r .row input{padding:6px;font-size:14px}
.grid.arch .ph img{opacity:.8}
.reasons.col{flex-direction:column}
.row{display:flex;gap:8px;margin-top:10px}
.row>*{flex:1}
button.b,a.b{border:1.5px solid var(--d);background:#fff;color:var(--d);border-radius:8px;padding:12px 10px;font:inherit;font-size:15px;font-weight:600;cursor:pointer;text-align:center;text-decoration:none}
button.b.p{background:var(--c);border-color:var(--c);color:#fff}
button.b.s{font-weight:400;color:var(--m);border-color:var(--b)}
button.sm,a.sm{display:inline-block;border:1px solid var(--d);background:#fff;color:var(--d);border-radius:6px;padding:5px 9px;font:inherit;font-size:13px;cursor:pointer;text-decoration:none}
button.sm.s,a.sm.s{color:var(--m);border-color:var(--b)}
.q{font-style:italic;color:var(--m);font-size:14px;margin:6px 0}
.note{background:var(--bg);border-left:3px solid var(--c);padding:6px 10px;margin:8px 14px 0;font-size:14px;border-radius:0 6px 6px 0}
.note.fail{background:var(--warn);border-color:#e0a030}
.draft{background:var(--bg);border-left:3px solid var(--c);padding:8px 10px;border-radius:0 6px 6px 0;margin:6px 0;white-space:pre-wrap;font-size:15px}
.reasons{display:none;gap:6px;margin-top:8px;flex-wrap:wrap}
.reasons.on{display:flex}
.empty{color:var(--m);text-align:center;padding:30px 10px}
h2{font-size:13px;text-transform:uppercase;letter-spacing:.04em;color:var(--m);margin:18px 0 8px;font-weight:600}
.compact{display:grid;grid-template-columns:72px minmax(0,1fr) auto;gap:4px 12px;padding:10px 14px;align-items:center}
.compact>div{min-width:0}
.compact .d{grid-column:1;grid-row:1;font-size:12px;color:var(--m);line-height:1.25}
.compact .h{grid-column:2;grid-row:1;font-size:14px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.compact .pills{grid-column:2;grid-row:2;display:flex;gap:4px;flex-wrap:wrap}
.compact .tools{grid-column:3;grid-row:1/3;display:flex;gap:6px}
.txt[contenteditable]{outline:none;border-radius:6px;margin:0 8px;padding:10px 6px 4px}
.txt[contenteditable]:focus{background:var(--bg);box-shadow:0 0 0 2px var(--c)}
.hint{font-size:12px;color:var(--m);padding:0 14px 6px}
.hist{font-size:13px;color:var(--m);padding:0 14px 8px;cursor:pointer;text-decoration:underline}
.old{white-space:pre-wrap;font-size:13px;color:var(--m);padding:6px 14px 10px;border-top:1px dashed var(--b)}
.pipe{border:1px solid var(--b);border-radius:12px;overflow:hidden;margin:0 0 12px;background:#fff}
.pipe .r{display:grid;grid-template-columns:62px minmax(0,1fr);gap:2px 10px;padding:8px 12px;border-top:1px solid var(--b);font-size:13px;align-items:start}
.pipe .r>div{min-width:0}
.pipe .r:first-child{border-top:0}
.pipe .r.link{cursor:pointer}
.pipe .r.link:hover{background:var(--bg)}
.pipe .r.today{background:var(--bg)}
.pipe .d{color:var(--m);white-space:nowrap;line-height:1.3}
.pipe .h{color:var(--t);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.pipe .n{color:var(--m);font-size:12px}
.pipe .pill{font-size:11px;padding:1px 7px;margin-right:4px}
.pipe{max-width:100%}.pipe .r>div{overflow:hidden}.pipe .row>*{min-width:0}.pipe button.sm,.pipe a.sm{white-space:normal;text-align:center}.mat{overflow-wrap:anywhere}
.more{font-size:13px;color:var(--m);padding:8px 12px;border-top:1px solid var(--b);cursor:pointer;background:#fff;width:100%;text-align:left;border-left:0;border-right:0;border-bottom:0}
.mat{font-size:13px;color:var(--m);padding:8px 12px;border-top:1px solid var(--b);line-height:1.6}
.shoot h3{font-size:14px;margin:14px 0 6px;color:var(--d);font-weight:600;display:flex;justify-content:space-between;align-items:center;gap:10px}
.shoot h3 span.t{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}
.grid .ph{position:relative;aspect-ratio:1;background:var(--bg);border-radius:6px;overflow:hidden}
.grid .ph img{width:100%;height:100%;object-fit:cover;display:block}
.grid .ph.sel{outline:3px solid var(--c);outline-offset:-3px}
.pact{position:sticky;bottom:0;z-index:3;background:#fff;margin:8px -4px 14px;padding:10px 12px;border:1px solid #d6e2ea;border-radius:10px;box-shadow:0 -2px 10px rgba(0,0,0,.06);font-size:13px;color:var(--d)}
.pact .row{margin-top:8px;display:flex;gap:8px;flex-wrap:wrap}
html,body{overflow-x:hidden}.q{min-width:0;overflow-wrap:anywhere}
.grid .ph .st{position:absolute;left:4px;bottom:4px;font-size:10px;background:rgba(255,255,255,.88);padding:1px 5px;border-radius:4px;color:var(--d);max-width:calc(100% - 8px);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.rec{position:fixed;right:14px;bottom:calc(14px + env(safe-area-inset-bottom));width:58px;height:58px;border-radius:50%;border:0;background:var(--d);color:#fff;font-size:0;box-shadow:0 4px 14px rgba(0,0,0,.25);z-index:6;cursor:pointer;-webkit-user-select:none;user-select:none;-webkit-touch-callout:none;touch-action:manipulation;-webkit-tap-highlight-color:transparent}
.rec::after{content:"";display:block;width:18px;height:18px;margin:0 auto;border-radius:50%;background:#fff}
.rec.on::after{border-radius:3px}
.rec.inline{position:static;width:46px;height:46px;flex:0 0 46px;box-shadow:0 2px 8px rgba(0,0,0,.2)}
button,.b,.sm,label.b{-webkit-user-select:none;user-select:none;-webkit-touch-callout:none;touch-action:manipulation;-webkit-tap-highlight-color:transparent}
.rec.on{background:#d33;animation:p 1s infinite}
.recbar{position:fixed;left:14px;right:86px;bottom:calc(16px + env(safe-area-inset-bottom));z-index:6;display:flex;align-items:center;gap:10px;background:#111;color:#fff;border-radius:999px;padding:8px 10px 8px 16px;font-size:14px;box-shadow:0 4px 14px rgba(0,0,0,.3)}
.recbar[hidden]{display:none}
.recbar .dot{width:10px;height:10px;border-radius:50%;background:#e33;animation:p 1s infinite;flex:0 0 auto}
.recbar .t{margin-left:auto;font-variant-numeric:tabular-nums;color:#ccc}
.recbar button{width:38px;height:38px;border-radius:50%;border:0;font-size:18px;cursor:pointer;flex:0 0 auto}
.recbar .x{background:#333;color:#fff}.recbar .ok{background:var(--c);color:#fff}
@media(min-width:960px){.recbar{left:auto;width:420px}}
@keyframes p{50%{transform:scale(1.08)}}
.b.rn.on{background:#c0392b;color:#fff;border-color:#c0392b}
.ask{position:fixed;left:14px;right:14px;bottom:calc(90px + env(safe-area-inset-bottom));z-index:10;background:#fff;border:2px solid var(--d);border-radius:12px;padding:14px;box-shadow:0 8px 30px rgba(0,0,0,.3);font-size:15px;line-height:1.4}
.ask[hidden]{display:none}
@media(min-width:960px){.ask{left:auto;right:28px;width:440px}}
.toast{position:fixed;left:50%;bottom:90px;transform:translateX(-50%);background:var(--d);color:#fff;padding:8px 14px;border-radius:999px;font-size:14px;opacity:0;transition:opacity .2s;z-index:7;pointer-events:none}
.toast.on{opacity:1}
.set{font-size:13px;color:var(--m);margin:16px 0 0}
.set input{width:70px;padding:4px 6px;font-size:14px}
.msg{border:1.5px solid var(--c);background:var(--bg);border-radius:10px;padding:12px;margin:0 0 12px}
.sys{border-radius:10px;padding:10px 12px;margin:0 0 12px;font-size:13px;background:var(--warn);border:1px solid #f3d9a4;color:#7a4b00}
.sys b{display:block;font-size:14px;color:#8a2a00}
.sys code{display:block;white-space:pre-wrap;font-size:12px;background:#fff;padding:6px 8px;border-radius:6px;margin:4px 0}
.sys.ok{background:#fff;border-color:var(--b);color:var(--m)}
@media(min-width:960px){
  main{max-width:1000px}
  .tabs button{font-size:15px}
  .card.full{display:grid;grid-template-columns:minmax(0,1fr) 300px}
  .card.full .post{min-width:0;border-right:1px solid var(--b)}
  .card.full .act{border-top:0;align-self:start}
  .img img{max-height:560px}
  .grid{grid-template-columns:repeat(6,1fr)}
}
.shr{position:absolute;width:32px;height:32px;border-radius:50%;border:0;background:rgba(255,255,255,.92);color:var(--m);display:flex;align-items:center;justify-content:center;cursor:pointer;padding:0;box-shadow:0 1px 3px rgba(0,0,0,.2)}
.shr.on{background:var(--c);color:#fff}
.item .shr{right:8px;top:8px}.grid .ph .shr{left:4px;top:4px;width:28px;height:28px}
.item .net{position:absolute;left:8px;top:8px;width:28px;height:28px;border-radius:50%;background:#01BC56;color:#fff;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center;border:2px solid #fff}
.item.net .handle{display:none}
.item.memo .noimg,.item.pub .noimg{display:flex;align-items:center;justify-content:center;color:var(--d)}
.item.pub{opacity:.6}
.fold{display:none}.fold.on{display:block}
.plus{width:36px;height:36px;border-radius:50%;border:0;background:var(--c);color:#fff;font-size:24px;line-height:36px;padding:0;cursor:pointer;flex:none}.team{padding:10px 0;border-top:1px solid var(--b)}.team:first-of-type{border-top:0}.team-h{display:flex;gap:10px;align-items:center}.chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:6px}.chip{border:1px solid var(--b);border-radius:999px;padding:3px 10px;font-size:13px}
.menu{width:40px;height:40px;border:0;background:none;display:flex;flex-direction:column;justify-content:center;gap:5px;padding:8px;cursor:pointer;flex:none}.menu span{display:block;height:2px;background:var(--d);border-radius:2px}
.top{gap:10px}.cb{border:0;background:none;display:flex;align-items:center;gap:4px;color:var(--d);font-size:14px;cursor:pointer;flex:none}.cb[hidden]{display:none}
.drawer{position:fixed;inset:0;z-index:20}.drawer[hidden]{display:none}.drawer .dbg{position:absolute;inset:0;background:rgba(15,58,80,.4)}
.drawer nav{position:absolute;left:0;top:0;bottom:0;width:260px;background:#fff;padding:calc(20px + env(safe-area-inset-top)) 0 20px;display:flex;flex-direction:column;box-shadow:4px 0 20px rgba(0,0,0,.15)}
.drawer nav a{padding:14px 22px;font-size:17px;color:var(--d);cursor:pointer;display:flex;justify-content:space-between;align-items:center}.drawer nav a b{color:var(--c)}
.item .ex{font-weight:600;-webkit-line-clamp:2}.meta .gap{display:inline-block;width:10px}.amber{color:#c77700}
.noimg.cover{display:flex;align-items:center;padding:14px;background:var(--tint);color:var(--d);font-weight:600;font-size:15px;line-height:1.3}
@media(max-width:959px){.sheet .act{position:sticky;bottom:0;z-index:1;box-shadow:0 -6px 16px rgba(0,0,0,.08)}}
.chips2{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}.chip2{border:1.5px solid var(--b);border-radius:999px;padding:9px 14px;font-size:15px;background:#fff;cursor:pointer;color:var(--t)}.chip2.on{border-color:var(--c);background:var(--tint);color:var(--d);font-weight:600}
.tcard{border:1.5px solid var(--b);border-radius:12px;padding:12px 14px;margin-top:10px;cursor:pointer;background:#fff}.tcard.on{border-color:var(--c);background:var(--tint)}.tcard b{display:block;margin-bottom:4px}.tcard span{font-size:14px;color:var(--t)}
.setup h2{margin:0 0 4px;text-transform:none;font-size:20px;letter-spacing:0;color:var(--d)}.setup .prog{font-size:12px;color:var(--m);margin:0 0 10px}.setup .q{margin:0 0 10px}.setup .nav{display:flex;gap:8px;margin-top:16px}.setup .nav .b{flex:1}
@media(max-width:959px){
  main{padding:12px 12px 120px}
  .sheet{padding:0 0 120px}.sheetin{max-width:none}.sheet .card{border-radius:0;border-left:0;border-right:0}
  .sheetbar{border-radius:0;padding:10px 12px 10px 16px;font-size:14px}
  .sheetbar .sm{width:40px;height:40px;border-radius:50%;padding:0;font-size:20px;line-height:40px;text-align:center;border-color:var(--b)}
  .rec{right:16px;bottom:calc(18px + env(safe-area-inset-bottom))}
  .act{padding:12px 16px calc(14px + env(safe-area-inset-bottom))}
}
</style>
</head>
<body>
<header>
 <div class="top"><button class="menu" onclick="drawer(true)" aria-label="Menü"><span></span><span></span><span></span></button><div style="flex:1;min-width:0"><h1><?= $ME ? htmlspecialchars($ME['name']) : 'Anton Lytvynenko' ?></h1><div class="sub" id="sub">lädt …</div></div><button class="cb" id="cbadge" onclick="showTab('comments')" hidden><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 5h16v11H8l-4 4z"/></svg><b id="cnum"></b></button><span id="clock" hidden></span></div>
</header>
<div class="drawer" id="drawer" hidden><div class="dbg" onclick="drawer(false)"></div><nav>
 <a onclick="nav('post')">Posts</a><a onclick="nav('comments')">Kommentare <b id="dnum"></b></a><a onclick="nav('photos')">Fotos</a><a onclick="nav('published')">Veröffentlicht</a><a onclick="nav('profile')"><?= $ME ? 'Profil' : 'Netzwerk' ?></a><?= $ME ? '<a onclick="logout()" style="margin-top:auto;color:var(--m)">Abmelden</a>' : '' ?>
</nav></div>
<main>
 <div id="content">
  <section id="post"></section>
  <section id="comments" hidden></section>
  <section id="photos" hidden></section>
  <section id="published" hidden></section>
  <section id="profile" hidden></section>
 </div>
 </main>
<button class="rec" id="rec" title="Aufnehmen">●</button>
<div class="recbar" id="recbar" hidden><span class="dot"></span><span id="recwhat">Aufnahme</span><span id="rectime" class="t">0:00</span><button class="x" onclick="stopRec(false)" title="verwerfen">✕</button><button class="ok" onclick="stopRec(true)" title="senden">✓</button></div>
<div class="ask" id="ask" hidden><div class="aq"></div><div class="row"><button class="b p ay" onclick="askYes()">Ja</button><button class="b s" onclick="askNo()">Nein</button></div></div>
<div class="toast" id="toast"></div>
<script>
const $=s=>document.querySelector(s), api='api.php';
let S=null, openCard=null, tab='post', expanded={}, showUsed=false, showAllUp=false, showAllPub=false, numEdit=null, extOpen=false;
let toastT=null;const toast=(m,ms=1800)=>{const t=$('#toast');t.textContent=m;t.classList.add('on');clearTimeout(toastT);toastT=setTimeout(()=>t.classList.remove('on'),ms)};
const post=async(o)=>{try{const r=await fetch(api,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(o)});if(r.status===401){location.reload();return {error:'login'}}return r.json()}catch(e){toast('keine Verbindung, nichts gesendet',4000);return {error:'offline'}}};
const WD=['So','Mo','Di','Mi','Do','Fr','Sa'];
const fmtSlot=s=>fmtDay(s)+' '+fmtTime(s);
const fmtDay=s=>{const d=new Date(s);return WD[d.getDay()]+' '+d.getDate()+'.'+(d.getMonth()+1)+'.'};
const fmtTime=s=>new Date(s).toLocaleTimeString('de-DE',{hour:'2-digit',minute:'2-digit'});
const fmtD=s=>s?new Date(s).toLocaleDateString('de-DE',{day:'2-digit',month:'2-digit'}):'';
const esc=s=>(s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const MANUAL=()=>(S&&S.health||{}).auto===false, LATER='sobald process.py auf dem Mac läuft';   // model work waits for the terminal (26.10.)
const STATUS={draft:'zu entscheiden',approved:'freigegeben',change:'wird überarbeitet',skipped:'verworfen',posted:'veröffentlicht',scheduled:'in LinkedIn geplant'};
let BUILD=null;
async function load(){let st;try{const r=await fetch(api+'?a=state&_='+Date.now());if(r.status===401){location.reload();return}st=await r.json()}catch(e){$('#sub').textContent='offline, letzter Stand';return} if(BUILD===null)BUILD=st.build; if(st.me){st.me.initials=(st.me.name||'').split(' ').slice(0,2).map(w=>w[0]||'').join('').toUpperCase()} const busy=(document.activeElement&&(document.activeElement.isContentEditable||/^(TEXTAREA|INPUT)$/.test(document.activeElement.tagName)))||(mr&&mr.state==='recording')||drag.id; if(st.build&&st.build!==BUILD&&!busy){location.reload();return} if(busy){S=st;return} S=st;render()}
function keepState(fn){const sh=document.querySelector('.sheet');const top=sh?sh.scrollTop:null;const vals={};document.querySelectorAll('textarea[id^="n-"],input[id^="u-"],input[id^="w-"],input[id^="m"],input[id^="x-"]').forEach(e=>{if(e.value&&e.value!==e.defaultValue)vals[e.id]=e.value});fn();for(const id in vals){const e=document.getElementById(id);if(e)e.value=vals[id]}const sh2=document.querySelector('.sheet');if(sh2&&top!==null)sh2.scrollTop=top}
function showTab(n){tab=n;document.querySelectorAll('.tabs button').forEach(x=>x.classList.toggle('on',x.dataset.t===n));['post','comments','photos','published','profile'].forEach(t=>{if($('#'+t))$('#'+t).hidden=t!==tab});history.replaceState(null,'','#'+n)}
document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>showTab(b.dataset.t));
if(['post','comments','photos'].includes(location.hash.slice(1))) showTab(location.hash.slice(1));
if(location.hash.startsWith('#post/')) openCard=location.hash.slice(6);   // deep link to one post: #post/li-post-14
const byHand=c=>c.status==='approved'&&new Date(c.slot)<new Date(S.now)&&!isAuto(c);   // approved, due, channel not connected: Anton posts it himself
const needs=c=>c.status==='draft'||(c.status==='change'&&c.failed)||byHand(c);
function drawer(on){$('#drawer').hidden=!on}
function nav(t){showTab(t);drawer(false)}
function render(){keepState(renderAll)}
function renderAll(){
  const open=S.cards.filter(needs).length, qOpen=S.queue.cards.filter(c=>!c.state).length;
  const hand=S.cards.filter(byHand).length;
  $('#sub').textContent=`${open-hand} zu entscheiden${hand?`, ${hand} selbst zu posten`:''}`;
  $('#cbadge').hidden=!qOpen; $('#cnum').textContent=qOpen||''; $('#dnum').textContent=qOpen||'';
  $('#clock').textContent=new Date(S.now).toLocaleTimeString('de-DE',{hour:'2-digit',minute:'2-digit'});
  renderPost(); renderComments(); renderPhotos(); renderPublished(); if($('#profile'))renderProfile();
}
function isAuto(c){const li=(S.health||{}).linkedin||{};return !!(li.connected&&(c.channel==='personal'||li.org))}
const PEND=180;   // a picture or note change is "busy" for 3 minutes; after that the Mac has not picked it up (asleep, offline) and the page says so instead of spinning
function pend(v){if(!v)return '';return (typeof v==='number'&&v>1e9&&Date.now()/1000-v<PEND)?'busy':'stale'}
function macSeen(){const H=S.health||{};return H.ts?'vor '+Math.round((new Date(S.now)-new Date(H.ts))/60000)+' min':'nie'}
let askFn=null;
let askNoFn=null;
function ask(q,yes,fn,no){askFn=fn;askNoFn=no||null;const b=$('#ask');b.querySelector('.aq').textContent=q;b.querySelector('.ay').textContent=yes;b.hidden=false}
function askNo(){const n=askNoFn;askFn=null;askNoFn=null;$('#ask').hidden=true;if(n)n()}
function askYes(){const f=askFn;askNoFn=null;askNo();if(f)f()}
function askPost(id){const c=S.cards.find(x=>x.id===id);if(!c)return;const page=c.channel==='company'?'der AlpiType-Seite':'deinem Profil';
  if(isAuto(c)) ask(`Jetzt auf ${page} posten? Geht in etwa 20 Sekunden raus und lässt sich von hier nicht zurückholen.`,'Ja, jetzt posten',()=>decide(id,'post'));
  else ask(`${c.channel==='company'?'Die Unternehmensseite':'Dein Profil'} ist nicht mit LinkedIn verbunden, nichts geht von selbst raus. Die Karte rückt nach oben und wartet auf dich: Text kopieren, Bild laden, in LinkedIn posten, dann „Als veröffentlicht markieren“. Weiter?`,'Ja, ich poste selbst',()=>decide(id,'post'))}
function askSchedule(id){const c=S.cards.find(x=>x.id===id);if(!c)return;const w=($('#w-'+id)||{}).value||'';if(w.length<16){toast('erst Datum und Uhrzeit wählen');return}
  ask(isAuto(c)?`Für ${fmtSlot(w)} planen? Geht dann von selbst raus.`:`Für ${fmtSlot(w)} planen? ${c.channel==='company'?'Die Unternehmensseite':'Dein Profil'} ist nicht verbunden: zu der Zeit rückt die Karte nach oben und du postest selbst.`,'Ja, planen',()=>decide(id,'schedule'))}
function askPosted(id){ask('Als veröffentlicht markieren? Die Karte verlässt das Board und erscheint unter „Veröffentlicht“. Nichts geht an LinkedIn.','Ja, markieren',()=>markPosted(id))}
function statusPill(c){const past=new Date(c.slot)<new Date(S.now), auto=isAuto(c);
  if(c.publish_error) return `<span class="pill warn">Veröffentlichen fehlgeschlagen: ${esc(c.publish_error.slice(0,80))}</span>`;
  if(c.status==='scheduled') return `<span class="pill li">Von dir in LinkedIn geplant</span>`;
  if(c.status==='change') return c.failed?`<span class="pill warn">Überarbeitung fehlgeschlagen, bitte neu entscheiden</span>`:`<span class="pill">Wird überarbeitet, etwa eine Minute</span>`;
  if(c.status==='approved') return past?(auto?`<span class="pill ok">Geht gerade raus</span>`:`<span class="pill todo">Wartet auf dich, du postest selbst</span>`):`<span class="pill ok">Geplant für ${fmtSlot(c.slot)}, ${auto?'geht von selbst raus':'du postest selbst'}</span>`;
  if(c.status==='posted') return `<span class="pill ok">Veröffentlicht</span>`+(c.url?` <a class="pill" href="${esc(c.url)}" target="_blank">in LinkedIn öffnen</a>`:'');
  if(c.status==='draft') return `<span class="pill todo">${c.updated?'Nach deiner Notiz überarbeitet, wartet auf dich':'Wartet auf dich'}</span>`;
  return `<span class="pill">${esc(STATUS[c.status]||c.status)}</span>`;
}
function extHtml(){const today=(S.now||'').slice(0,10);let h=`<button class="more" style="border:0;background:none;padding:10px 0" onclick="extOpen=!extOpen;render()">${extOpen?'schließen':'+ Post, den du selbst in LinkedIn veröffentlicht hast'}</button>`;
  if(extOpen) h+=`<div class="card" style="padding:12px"><div class="row" style="margin:0"><input type="date" id="x-date" value="${today}"><select id="x-ch"><option value="personal">Profil</option><option value="company">Unternehmensseite</option></select></div><input type="text" id="x-hook" placeholder="erste Zeile des Posts" style="margin-top:6px"><input type="url" id="x-url" placeholder="LinkedIn-Link (optional)" style="margin-top:6px"><div class="row" style="margin-top:6px"><button class="sm" onclick="addExternal()">eintragen</button></div></div>`;return h}
function isoWeek(s){const d=new Date(s);const t=new Date(Date.UTC(d.getFullYear(),d.getMonth(),d.getDate()));const day=t.getUTCDay()||7;t.setUTCDate(t.getUTCDate()+4-day);const y=t.getUTCFullYear();const w=Math.ceil(((t-Date.UTC(y,0,1))/86400000+1)/7);return y+'-W'+String(w).padStart(2,'0')}
async function saveVisits(){const r=await post({a:'profile_visits',week:$('#pv-week').value,visits:$('#pv-n').value});toast(r.ok?'gespeichert':'Fehler: '+(r.error||''));load()}
async function inbound(id,dec){const p=((S.pipeline||{}).inbound_proposed||[]).find(x=>x.id===id)||{};const r=await post({a:'inbound',id,decision:dec,date:p.date||'',source:p.source_hint||'website form',who:p.who||'',what:p.subject||'',qualified:'',next:''});toast(r.ok?(dec==='confirm'?'zu Gesprächen':'verworfen'):'Fehler: '+(r.error||''));load()}
async function saveNums(id){const v=k=>($('#m'+k+'-'+id)||{}).value||'';const r=await post({a:'metrics',post_id:id,impressions:v('i'),reactions:v('r'),comments:v('c')});toast(r.ok?'Zahlen gespeichert':'Fehler: '+(r.error||''));numEdit=null;load()}
async function addExternal(){const r=await post({a:'external',date:$('#x-date').value,channel:$('#x-ch').value,hook:$('#x-hook').value,url:$('#x-url').value});toast(r.ok?'unter Veröffentlicht eingetragen':'Fehler: '+(r.error||''),r.ok?2000:5000);if(r.ok)extOpen=false;load()}
function goCard(id){openCard=id;showTab('post');renderPost()}
function teamNames(c){const me=(S.me||{}).name||'Anton Lytvynenko';const n=new Set();if(c&&c.credit)n.add(c.credit);for(const g of netGroups())for(const m of (g.members||[]))if(m.name&&m.name!==me)n.add(m.name);return [...n]}
function namesIn(text,c){return teamNames(c).filter(n=>(text||'').includes(n))}
function boldNames(html,c){for(const n of namesIn(html,c))html=html.split(n).join('<b>'+n+'</b>');return html}
function postHtml(c){
  const who=c.channel==='company'?`<div class="ava co">A</div><div><div class="n">AlpiType</div><div class="s">Unternehmensseite, ${fmtSlot(c.slot)}${c.credit?', aus dem Netzwerk, von '+esc(c.credit):''}</div></div>`
                                 :`<div class="ava">${esc((S.me||{}).initials||'AL')}</div><div><div class="n">${esc((S.me||{}).name||'Anton Lytvynenko')}</div><div class="s">Profil, ${fmtSlot(c.slot)}${c.credit?', aus dem Netzwerk, von '+esc(c.credit):''}</div></div>`;
  const ed=needs(c);
  const imgTools=(ed||c.status==='approved')?`<div class="imgtools">${c.channel==='personal'?`<button class="sm s" onclick="decide('${c.id}','photo_next')">Nächstes Foto aus dem Pool</button>`:''}<label class="lbl">Anderes Bild hochladen<input type="file" accept="image/*" style="display:none" onchange="uploadFor('${c.id}',this)"></label><span class="hint" style="padding:0">ersetzt das Bild, der Text bleibt</span></div>`:'';
  return `<div class="who">${who}</div><div class="txt ${(c.status==='change'&&!c.failed&&!MANUAL())||pend(c.note_pending)==='busy'?'busy':''}" id="t-${c.id}" ${ed?'contenteditable="plaintext-only" spellcheck="false"':''}>${boldNames(esc(c.text),c)}</div>${namesIn(c.text,c).length?`<div class="hint">Name fett: in LinkedIn ein @ davor tippen und die Person auswählen, dann ist sie verlinkt. Von selbst geht das erst, wenn die Person ihr LinkedIn mit ihrem Board verbunden hat.</div>`:''}${c.image?`<div class="img ${pend(c.image_pending)==='busy'?'busy':''}"><img src="${esc(c.image.url)}" alt="">${pend(c.image_pending)==='busy'?'<div class="spin"><i></i><span>Bild wird getauscht …</span></div>':''}</div>`:''}${imgTools}`;
}
function systemHtml(){
  const H=S.health||{}; const seen=H.ts?Math.round((new Date(S.now)-new Date(H.ts))/60000):null; const issues=[...(H.issues||[])];
  if(seen===null) issues.unshift({what:'Mac',log:'noch kein Statusbericht',fix:'auf dem Mac: launchctl list | grep board-sync'});
  else if(seen>45) issues.unshift({what:'Mac',log:`letzter Lauf vor ${seen} min, Tipps warten auf dem Server`,fix:'Mac wecken; wenn wach: launchctl kickstart gui/501/com.alpitype.board-sync, dann library/log/board-sync.err'});
  const li=H.linkedin||{};
  const pd=H.pending||{}; const pl=Object.keys(pd).filter(k=>pd[k]).map(k=>pd[k]+' '+k).join(', ');
  if(!issues.length) return '';
  const pend=(S.memos||[]).length+S.cards.filter(c=>c.note_pending||(c.status==='change'&&!c.failed)).length;const bn=pend?`<div class="q" style="margin:0 0 8px;font-size:12px">${pend} Notiz${pend>1?"en":""} offen</div>`:"";
  return bn+issues.map(i=>`<div class="sys"><b>${esc(i.what)}${i.what.startsWith('one post')?'':' braucht dich'}${i.times>1?', '+i.times+' mal':''}</b>${esc(i.log||'')}<code>${esc(i.fix||'')}</code></div>`).join('');
}
const DOT={draft:'#e8a000',change:'#e8a000',approved:'#1a9c4a',scheduled:'#0a66c2',posted:'#999',skipped:'#999'};
function itemHtml(c){const locked=c.status==='scheduled';const hook=(c.text||'').split('\n')[0].replace(/\s*#\w+/g,'').trim();
  const state=needs(c)?'<span class="amber">entscheiden</span>':c.pillar==='network'&&c.credit?`von ${esc(initials(c.credit))}`:c.status==='approved'?'geplant':locked?'in LinkedIn':c.status==='change'?'wird überarbeitet':'';
  return `<div class="item ${locked?'locked':''} ${c.channel==='company'?'co':''} ${c.pillar==='network'?'net':''}" data-id="${c.id}" data-ch="${c.channel}">${c.image?`<img src="${esc(c.image.url)}" loading="lazy" draggable="false">`:`<div class="noimg cover">${esc(hook)}</div>`}<span class="st" style="background:${DOT[c.status]||'#999'}"></span>${c.pillar==='network'&&c.credit?`<span class="net" title="${esc(c.credit)}">${esc(initials(c.credit))}</span>`:''}${locked?'':'<span class="handle" title="drag to reorder">⋮⋮</span>'}<div class="meta"><b>${fmtDay(c.slot)}</b>${state?'<span class="gap"></span>'+state:''}</div><div class="ex">${esc(hook)}</div></div>`}
const MIC='<svg viewBox="0 0 24 24" width="30" height="30" fill="currentColor"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M6 11a6 6 0 0 0 12 0h-1.8a4.2 4.2 0 0 1-8.4 0zM11.1 17.5h1.8V21h-1.8z"/></svg>';
const PEOPLE='<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><circle cx="9" cy="8" r="3.2"/><path d="M3 18c0-3.3 2.7-5.5 6-5.5s6 2.2 6 5.5v1H3z"/><circle cx="16.5" cy="9" r="2.5"/><path d="M15.2 19v-1c0-1.6-.5-3-1.4-4.1 1-.6 1.9-.9 2.7-.9 2.6 0 4.5 1.7 4.5 4.5V19z"/></svg>';
const initials=n=>(n||'').split(' ').filter(Boolean).map(w=>w[0]).join('').slice(0,2).toUpperCase();
function shareBtn(id,shared,fn){return `<button class="shr ${shared?'on':''}" title="${shared?'für das Netzwerk freigegeben':'für das Netzwerk freigeben'}" onclick="event.stopPropagation();${fn}('${id}','${shared?'unshare':'share'}')">${PEOPLE}</button>`}
function memoTile(m){const dest=m.post?`wurde ${esc(m.post)}`:(m.topic?'wird ein Entwurf, sobald ein Foto frei ist':'wird ein Entwurf');const card=m.post&&S.cards.some(c=>c.id===m.post);
  return `<div class="item locked memo" data-id="${card?m.post:''}"><div class="noimg">${MIC}</div>${m.post?'':shareBtn(m.id,m.share==='network','memoShare')}<div class="meta"><b>Memo</b>, ${fmtDay(m.recorded)} ${fmtTime(m.recorded)}</div><div class="ex">${esc(m.words)} Wörter, ${dest}</div></div>`}
function pubTile(p){return `<div class="item locked pub" data-id="" ${p.link?`onclick="window.open('${esc(p.link)}','_blank')"`:''}><div class="noimg"></div><div class="meta"><b>${fmtDay(p.date)}</b>, veröffentlicht, ${p.channel==='company'?'Unternehmen':'Profil'}</div><div class="ex">${esc(p.hook)}</div></div>`}
function itemsHtml(){const cards=[...S.cards].sort((a,b)=>a.slot.localeCompare(b.slot));const P=S.pipeline||{};
  const memos=(P.memos||[]).filter(m=>['new','phrase'].includes(m.status)&&!m.post);
  const line=memos.length?`<div class="q" style="margin:0 0 10px;font-style:normal">${memos.length} Memo${memos.length===1?'':'s'} ${memos.length===1?'wartet':'warten'} auf ein freies Foto</div>`:'';
  if(!cards.length) return line+'<div class="empty">Noch nichts. Sprich ein Memo ein oder lade Fotos hoch.</div>';
  return line+`<div class="items" id="items">${cards.map(itemHtml).join('')}</div>`}
function renderPublished(){const el=$('#published');if(!el)return;const pub=((S.pipeline||{}).published)||[];
  el.innerHTML=(pub.length?'<div class="pipe">'+pub.map(p=>{const n=[p.impressions!==''&&p.impressions+' Impressionen',p.reactions!==''&&p.reactions+' Reaktionen',p.comments!==''&&p.comments+' Kommentare'].filter(Boolean).join(', ');
    return `<div class="r"><div class="d">${fmtDay(p.date)}</div><div>${p.link?`<a class="pill li" href="${esc(p.link)}" target="_blank" rel="noopener">in LinkedIn öffnen</a>`:''}<div class="h">${esc(p.hook)}</div>${n?`<div class="n">${esc(n)}</div>`:''}</div></div>`}).join('')+'</div>':'<div class="empty">noch nichts veröffentlicht</div>')+extHtml()}
async function memoShare(id,dec){if(dec==='share'&&!(await confirmShare('dieses Memo')))return;const r=await post({a:'memo_share',id,decision:dec});toast(r.ok?(dec==='share'?'für das Netzwerk freigegeben':'Freigabe zurückgezogen'):'Fehler: '+(r.error||''));load()}
function fullCardHtml(c){
  const past=new Date(c.slot)<new Date(S.now), act=needs(c), done=['posted','skipped'].includes(c.status);
  const self=`<div class="row"><button class="b s" onclick="$('#ps-${c.id}').classList.toggle('on')">Ich habe es selbst in LinkedIn gepostet</button></div>
        <div class="reasons col" id="ps-${c.id}"><input type="url" id="u-${c.id}" placeholder="LinkedIn-Link (optional)"><button class="b p" onclick="askPosted('${c.id}')">Als veröffentlicht markieren</button><div class="q" style="margin:0;font-size:12px">verlässt das Board, erscheint unter Veröffentlicht; das System postet nichts</div></div>`;
  const prop='';
  return `<div class="card full ${done?'done':''}" id="c-${c.id}"><div class="post">${postHtml(c)}${prop}
      ${c.note?`<div class="note ${c.failed?'fail':''}">${c.failed?'could not apply: ':(c.updated?'applied: ':'your note: ')}${esc(c.note)}</div>`:''}
      <div style="padding:8px 14px 12px;display:flex;gap:6px;flex-wrap:wrap;align-items:center">${statusPill(c)}${(c.status==='approved'&&!isAuto(c))?`<button class="sm s" onclick="copyText('${c.id}')">Text kopieren</button>${c.image?`<a class="sm s" href="${esc(c.image.final||c.image.url)}" download="${esc(c.id)}.jpg">Bild laden</a>`:''}`:''}${act?'':`<button class="sm s" onclick="openCard=null;renderPost()">Schließen</button>`}</div></div>
      <div class="act">
        ${byHand(c)?`<div class="q" style="margin:0 0 8px">1. Text kopieren, 2. Bild laden, 3. beides in LinkedIn posten, als ${c.channel==='company'?'AlpiType':'du selbst'}, 4. Als veröffentlicht markieren</div>
        <button class="b" style="width:100%" onclick="copyText('${c.id}')">Text kopieren</button>
        ${c.image?`<a class="b" style="display:block;margin-top:8px" href="${esc(c.image.final||c.image.url)}" download="${esc(c.id)}.jpg">Bild laden</a>`:''}
        <input type="url" id="u-${c.id}" placeholder="LinkedIn-Link (optional)" style="margin-top:12px"><button class="b p" style="width:100%;margin-top:6px" onclick="askPosted('${c.id}')">Als veröffentlicht markieren</button>
        <div class="row"><button class="b s" onclick="decide('${c.id}','unschedule')">Zurück zu entscheiden</button></div>
        <div class="q" style="margin:8px 0 0;font-size:13px">${c.channel==='company'?'die Unternehmensseite postet von selbst, sobald LinkedIn die Community Management API freigibt':(S.me?'LinkedIn-Verbindung für dein Board: mit Anton am Mac':'LinkedIn neu verbinden: pipeline/linkedin_auth.py')}</div>`
        :act?`<button class="b p" style="width:100%" onclick="askPost('${c.id}')">${isAuto(c)?'Jetzt posten':'Freigeben, selbst posten'}</button>
        ${isAuto(c)?'':`<div class="q" style="margin:4px 0 0;font-size:13px">${(c.channel==='company'?'Unternehmensseite':'Profil')+' ist nicht mit der API verbunden: die Karte rückt nach oben mit Text kopieren, Bild laden, Als veröffentlicht markieren'}</div>`}
        <textarea id="n-${c.id}" rows="3" placeholder="Notiz: was ändern, oder eine Regel für alle Posts" style="margin-top:12px"></textarea>
        <div class="row" style="margin-top:6px;align-items:center"><button class="b" style="flex:1" onclick="decide('${c.id}','change')">Post überarbeiten</button><button class="rec inline" id="rn-${c.id}" onclick="recNote('${c.id}')" title="Notiz sprechen"></button></div>
        <button class="more" style="border:0;background:none;padding:12px 0 0;text-align:left" onclick="$('#f-${c.id}').classList.toggle('on')">Mehr …</button><div class="fold" id="f-${c.id}">
        <input type="datetime-local" id="w-${c.id}" value="${esc(c.slot.slice(0,16))}" style="margin-top:8px">
        <button class="b" style="width:100%;margin-top:6px" onclick="askSchedule('${c.id}')">Planen</button>
        <div class="row"><button class="b s" onclick="skipPost('${c.id}')">Verwerfen</button></div>
        <div class="reasons" id="r-${c.id}"><button class="sm s" onclick="decide('${c.id}','skip','not the topic')">nicht das Thema</button><button class="sm s" onclick="decide('${c.id}','skip','not the form')">nicht die Form</button><button class="sm s" onclick="decide('${c.id}','skip','')">ohne Grund</button></div>${self}</div>`
        :c.status==='approved'?`${past?'':`<button class="b p" style="width:100%" onclick="askPost('${c.id}')">${isAuto(c)?'Jetzt posten':'Freigeben, selbst posten'}</button>`}<div class="row"><button class="b" onclick="decide('${c.id}','unschedule')">Planung aufheben</button></div><div class="q" style="margin:4px 0 0;font-size:13px">zurück zu entscheiden; nichts wird gepostet</div>${self}`
        :c.status==='scheduled'?`<div class="row"><button class="b" onclick="decide('${c.id}','unschedule')">Planung aufheben</button></div><div class="q" style="margin:4px 0 0;font-size:13px">den hast du in der LinkedIn-App geplant; das Board kommt nicht dran. Dort zuerst abbrechen, dann hier aufheben, und er kommt zurück zu entscheiden</div>${self}`
        :c.status==='change'?`<div class="q">wird mit deiner Notiz überarbeitet; kommt hierher zurück</div>`
        :`<div class="q">${esc(STATUS[c.status]||c.status)}</div>`}
      </div></div>`;
}
let drag={id:null};
function startDrag(){drag.active=true;drag.el.classList.add('drag');document.body.classList.add('dragging');if(navigator.vibrate)navigator.vibrate(15)}
function endDrag(send){clearTimeout(drag.timer);if(drag.active){drag.el.classList.remove('drag');drag.el.style.transform='';document.body.classList.remove('dragging');if(send)sendOrder()}drag={id:null}}
document.addEventListener('pointerdown',e=>{const it=e.target.closest('#items .item');if(!it||e.target.closest('button,a'))return;
  drag={id:it.dataset.id,ch:it.dataset.ch,el:it,x:e.clientX,y:e.clientY,active:false,timer:null};
  if(it.classList.contains('locked'))return;   // scheduled in LinkedIn: a tap opens it, dragging is off
  if(e.target.closest('.handle')){e.preventDefault();startDrag()}else drag.timer=setTimeout(startDrag,380)});
document.addEventListener('pointermove',e=>{if(!drag.id)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;
  if(!drag.active){if(Math.hypot(dx,dy)>10)endDrag(false);return}
  e.preventDefault();drag.el.style.transform=`translate(${dx}px,${dy}px) scale(1.04)`;
  drag.el.style.visibility='hidden';const under=document.elementFromPoint(e.clientX,e.clientY)?.closest('#items .item');drag.el.style.visibility='';
  if(under&&under!==drag.el&&under.dataset.ch===drag.ch&&!under.classList.contains('locked')&&Date.now()-(drag.last||0)>220){const r=under.getBoundingClientRect();
    if(Math.abs(e.clientX-(r.left+r.width/2))>r.width*.35||Math.abs(e.clientY-(r.top+r.height/2))>r.height*.35)return;   // swap only near the middle of the other item, not at its edge
    const items=[...document.querySelectorAll('#items .item')];const a=items.indexOf(drag.el),b=items.indexOf(under);
    const before=new Map(items.map(it=>[it,it.getBoundingClientRect()]));
    under.parentNode.insertBefore(drag.el,a<b?under.nextSibling:under);drag.last=Date.now();
    for(const it of items){if(it===drag.el)continue;const p=before.get(it),q=it.getBoundingClientRect();const ddx=p.left-q.left,ddy=p.top-q.top;if(ddx||ddy){it.style.transition='none';it.style.transform=`translate(${ddx}px,${ddy}px)`;requestAnimationFrame(()=>{it.style.transition='transform .22s ease';it.style.transform='';setTimeout(()=>it.style.transition='',240)})}}
    const q=drag.el.getBoundingClientRect(),p=before.get(drag.el);drag.x+=q.left-p.left;drag.y+=q.top-p.top;drag.el.style.transform=`translate(${e.clientX-drag.x}px,${e.clientY-drag.y}px) scale(1.04)`}},{passive:false});
document.addEventListener('pointerup',e=>{if(!drag.id)return;const was=drag.active;endDrag(was);if(!was&&e.target.closest('#items .item')&&!e.target.closest('button,a'))goCard(e.target.closest('.item').dataset.id)});
document.addEventListener('pointercancel',()=>endDrag(false));
document.addEventListener('touchmove',e=>{if(drag.id&&(drag.active||Math.hypot(e.touches[0].clientX-drag.x,e.touches[0].clientY-drag.y)<10))e.preventDefault()},{passive:false});
document.addEventListener('contextmenu',e=>{if(e.target.closest('#items .item'))e.preventDefault()});
async function sendOrder(){const items=[...document.querySelectorAll('#items .item')];const byCh={};for(const it of items){if(it.classList.contains('locked'))continue;(byCh[it.dataset.ch]=byCh[it.dataset.ch]||[]).push(it.dataset.id)}
  const before=[...S.cards].sort((a,b)=>a.slot.localeCompare(b.slot)).filter(c=>c.status!=='scheduled').map(c=>c.id);
  let n=0;for(const ch in byCh){const ids=byCh[ch];if(ids.length<2)continue;const prev=before.filter(id=>S.cards.find(c=>c.id===id).channel===ch);if(prev.join()===ids.join())continue;const r=await post({a:'decide',card_id:ids[0],decision:'order',order:ids});if(r.ok)n++}
  if(n){toast('Reihenfolge gespeichert, Slots neu verteilt');watchUntil=Date.now()+60000}load()}
let SU=null, suStep=0;
const SU_STEPS=['check','readers','goal','topics','tone','examples','day','photos','done'];
const DAYS=[['Mon','Montag'],['Tue','Dienstag'],['Wed','Mittwoch'],['Thu','Donnerstag'],['Fri','Freitag'],['Sat','Samstag'],['Sun','Sonntag']];
function suLoad(){if(SU)return;try{SU=JSON.parse(localStorage.getItem('su-'+((S.me||{}).slug||''))||'null')}catch(e){SU=null}SU=SU||{};suStep=SU._step||0}
function suSave(){SU._step=suStep;try{localStorage.setItem('su-'+((S.me||{}).slug||''),JSON.stringify(SU))}catch(e){}}
function suSet(k,v){SU[k]=v;suSave();renderPost()}
function suInput(k,el){SU[k]=el.value;suSave()}
function suToggle(k,v,single){const a=SU[k]||[];SU[k]=single?[v]:(a.includes(v)?a.filter(x=>x!==v):[...a,v]);suSave();renderPost()}
function suGo(d){suStep=Math.max(0,Math.min(SU_STEPS.length-1,suStep+d));suSave();renderPost();window.scrollTo(0,0)}
function chips(k,opts,single){const sel=SU[k]||[];return `<div class="chips2">${opts.map(o=>`<button class="chip2 ${sel.includes(o)?'on':''}" onclick="suToggle('${k}',${JSON.stringify(o).replace(/"/g,'&quot;')},${!!single})">${esc(o)}</button>`).join('')}</div>`}
function suNav(ok,last){return `<div class="nav">${suStep>0?`<button class="b s" onclick="suGo(-1)">Zurück</button>`:''}${last?`<button class="b p" onclick="confirmProfile()">Fertig, ersten Entwurf schreiben</button>`:`<button class="b p" ${ok?'':'disabled style="opacity:.4"'} onclick="suGo(1)">Weiter</button>`}</div>`}
function onboardingHtml(){
  const m=S.me||{}; suLoad();
  if(S.profile_pending) return `<div class="card setup" style="padding:16px"><h2>Deine Website wird gelesen</h2><div class="q">Das dauert ein bis zwei Minuten, die Seite aktualisiert sich von selbst. Erfunden wird nichts: was unklar bleibt, siehst du gleich als Liste.</div></div>`;
  if(!m.proposed) return `<div class="card setup" style="padding:16px"><h2>Hallo ${esc((m.name||'').split(' ')[0])}, kurz zu dir</h2><div class="q">Deine Website reicht für den Anfang. Das System liest sie und schlägt dir vor, wer deine Posts lesen soll und worüber du schreibst.</div>
    <label class="hint" style="padding:0">Deine Website</label><input type="text" id="su-web" value="${esc(SU.website||'')}" placeholder="firma.de" inputmode="url" oninput="suInput('website',this)">
    <label class="hint" style="padding:0;margin-top:10px;display:block">Dein LinkedIn-Profil (optional)</label><input type="text" id="su-li" value="${esc(SU.linkedin||'')}" placeholder="linkedin.com/in/…" inputmode="url" oninput="suInput('linkedin',this)">
    <label class="hint" style="padding:0;margin-top:10px;display:block">Wenn LinkedIn uns nicht reinlässt: dein Steckbrief, hier eingefügt (optional)</label><textarea id="su-words" rows="4" placeholder="Was du machst, für wen, was dir wichtig ist" oninput="suInput('words',this)">${esc(SU.words||'')}</textarea>
    <label class="lbl" style="margin-top:10px">Dokument anhängen (optional)<input type="file" id="su-doc" accept=".pdf,.txt,.md,.docx" style="display:none" onchange="$('#su-docname').textContent=this.files[0]?this.files[0].name:''"></label> <span id="su-docname" class="hint"></span>
    <div class="nav"><button class="b p" onclick="sendProfile()">Weiter</button></div><div class="q" style="margin:8px 0 0;font-size:13px">Nichts davon wird veröffentlicht.</div></div>`;
  const step=SU_STEPS[suStep], n=suStep+1, N=SU_STEPS.length; const prog=`<div class="prog">Schritt ${n} von ${N}</div>`;
  const T=v=>esc(v||''); let h='';
  if(step==='check'){h=`<h2>Stimmt das?</h2><div class="q">Aus deiner Website. Tipp auf eine Zeile, um sie zu ändern.</div>
    <label class="hint" style="padding:0">Name</label><div style="padding:6px 0 2px">${T(m.name)}</div>
    <label class="hint" style="padding:0;margin-top:8px;display:block">Was du machst</label><input type="text" value="${T(SU.role??m.role)}" oninput="suInput('role',this)">
    <label class="hint" style="padding:0;margin-top:8px;display:block">Firma</label><input type="text" value="${T(SU.company??m.company)}" oninput="suInput('company',this)">
    <label class="hint" style="padding:0;margin-top:8px;display:block">Was du anbietest</label><input type="text" value="${T(SU.offer??m.offer)}" oninput="suInput('offer',this)">
    ${(m.uncertain||[]).length?`<div class="note" style="margin:12px 0 0"><b>Unklar geblieben, kommt in keinen Post</b><ul style="margin:4px 0 0;padding-left:18px">${(m.uncertain||[]).map(u=>`<li>${esc(u)}</li>`).join('')}</ul></div>`:''}${suNav(true)}`}
  else if(step==='readers'){const opts=(m.audiences&&m.audiences.length?m.audiences:(m.audience||'').split(/;|,/).map(x=>x.trim()).filter(Boolean)).slice(0,6);
    h=`<h2>Wer soll deine Posts lesen?</h2><div class="q">Eins oder zwei. Für diese Person wird jeder Post geschrieben.</div>${chips('readers',opts)}
    <input type="text" value="${T(SU.readersX)}" placeholder="anders, in deinen Worten" style="margin-top:10px" oninput="suInput('readersX',this)">${suNav((SU.readers||[]).length||SU.readersX)}`}
  else if(step==='goal'){h=`<h2>Was soll der Leser danach tun?</h2><div class="q">Eins. Das Ende jedes Posts zielt darauf.</div>${chips('goal',['Beratungstermin buchen','Mir schreiben','Nur verstehen'],true)}
    <input type="text" value="${T(SU.goalX)}" placeholder="oder etwas anderes" style="margin-top:10px" oninput="suInput('goalX',this)">${suNav((SU.goal||[]).length||SU.goalX)}`}
  else if(step==='topics'){const opts=(m.topics||[]).slice(0,12); if(!SU.topics&&!SU._topicsInit){SU.topics=[...opts];SU._topicsInit=true;suSave()}
    h=`<h2>Worüber willst du schreiben?</h2><div class="q">Streich, was nicht passt. Ein Thema wird ein Post.</div>${chips('topics',opts)}
    <input type="text" value="${T(SU.topicsX)}" placeholder="ein eigenes Thema, in deinen Worten" style="margin-top:10px" oninput="suInput('topicsX',this)">
    <label class="hint" style="padding:0;margin-top:12px;display:block">Worüber nie (optional)</label><input type="text" value="${T(SU.avoid)}" placeholder="z. B. Preise, Konkurrenten" oninput="suInput('avoid',this)">${suNav((SU.topics||[]).length||SU.topicsX)}`}
  else if(step==='tone'){const ts=m.tone_samples||{};const cards=[['locker','Locker und direkt',ts.locker],['sachlich','Ruhig und sachlich',ts.sachlich],['persoenlich','Persönlich, erzählt',ts.persoenlich]];
    h=`<h2>Wie willst du klingen?</h2><div class="q">Drei Proben aus deinen Fakten. Tipp auf eine.</div>${cards.map(([k,l,sm])=>`<div class="tcard ${SU.register===k?'on':''}" onclick="SU.register='${k}';SU.toneLabel='${l}';suSave();renderPost()"><b>${l}</b><span>${esc(sm||'')}</span></div>`).join('')}${suNav(!!SU.register)}`}
  else if(step==='examples'){h=`<h2>Zwei, drei Posts, die dir gefallen</h2><div class="q">Deine oder fremde. Wir kopieren nichts, nur den Rhythmus. Optional.</div><textarea rows="8" placeholder="Posts hier einfügen, durch Leerzeilen getrennt" oninput="suInput('examples',this)">${T(SU.examples)}</textarea>${suNav(true)}`}
  else if(step==='day'){if(!SU.day){SU.day='Tue';suSave()}
    h=`<h2>An welchem Tag soll dein Post rausgehen?</h2><div class="q">Einer pro Woche. Du kannst ihn jederzeit ändern.</div><div class="chips2">${DAYS.map(([k,l])=>`<button class="chip2 ${SU.day===k?'on':''}" onclick="suSet('day','${k}')">${l}</button>`).join('')}</div>${suNav(true)}`}
  else if(step==='photos'){h=`<h2>Ein, zwei Fotos von dir oder deiner Arbeit</h2><div class="q">Ohne Foto geht es auch, dann nimmt der Post Text. Optional.</div>
    <form id="up"><label class="b p" style="display:block;text-align:center;border-radius:8px;padding:12px;background:var(--c);color:#fff;font-weight:600;cursor:pointer">+ Fotos hinzufügen<input type="file" name="photos[]" accept="image/*" multiple style="display:none" onchange="startUpload(this)"><input type="hidden" name="note" value=""><input type="checkbox" name="share" value="1" style="display:none"></label></form>
    ${SU.photos?`<div class="q" style="margin-top:8px">${SU.photos} Foto${SU.photos===1?'':'s'} hochgeladen</div>`:''}${suNav(true)}`}
  else {const readers=[...(SU.readers||[]),...(SU.readersX?[SU.readersX]:[])].join(', ');const goal=(SU.goal||[])[0]||SU.goalX||'';
    h=`<h2>Fertig</h2><div class="q">So schreibt das System deinen ersten Entwurf. Er kommt in etwa einer Minute, und nichts geht ohne dich raus.</div>
    <div class="note" style="margin:0"><b>Für</b> ${esc(readers)}<br><b>Ziel</b> ${esc(goal)}<br><b>Ton</b> ${esc(SU.toneLabel||'')}<br><b>Tag</b> ${esc((DAYS.find(d=>d[0]===SU.day)||[])[1]||'Dienstag')}<br><b>Themen</b> ${esc([...(SU.topics||[]),...(SU.topicsX?[SU.topicsX]:[])].slice(0,4).join(', '))}${(SU.topics||[]).length>4?' …':''}</div>${suNav(true,true)}`}
  return `<div class="card setup" style="padding:16px">${prog}${h}</div>`;
}
async function sendProfile(){suLoad();const fd=new FormData();fd.append('a','profile');fd.append('website',SU.website||'');fd.append('linkedin',SU.linkedin||'');fd.append('words',SU.words||'');const doc=$('#su-doc');if(doc&&doc.files[0])fd.append('doc',doc.files[0]);
  if(!(SU.website||SU.words||(doc&&doc.files[0]))){toast('Website, Steckbrief oder Dokument: mindestens eins');return}toast('gesendet …');let r={};try{r=await (await fetch(api,{method:'POST',body:fd})).json()}catch(e){r={error:'keine Verbindung'}}toast(r.ok?'angekommen, der Vorschlag kommt in ein bis zwei Minuten':'Fehler: '+(r.error||''),r.ok?4000:8000);watchUntil=Date.now()+300000;load()}
async function confirmProfile(){suLoad();const m=S.me||{};const readers=[...(SU.readers||[]),...(SU.readersX?[SU.readersX]:[])];const topics=[...(SU.topics||[]),...(SU.topicsX?[SU.topicsX]:[])];const goal=(SU.goal||[])[0]||SU.goalX||'';
  const r=await post({a:'profile_confirm',role:SU.role??m.role??'',company:SU.company??m.company??'',website:SU.website||m.website||'',offer:SU.offer??m.offer??'',audience:readers.join(', '),goal,topics,avoid:(SU.avoid||'').split(',').map(x=>x.trim()).filter(Boolean),tone:SU.toneLabel||m.tone||'',style:{register:SU.register==='persoenlich'?'':(SU.register||''),length:'mittel',question:'ja'},examples:SU.examples||'',linkedin:SU.linkedin||m.linkedin||'',day:SU.day||'Tue',facts:m.facts||''});
  toast(r.ok?'gespeichert, dein erster Entwurf kommt in etwa einer Minute':'Fehler: '+(r.error||''),4000);if(r.ok){try{localStorage.removeItem('su-'+(m.slug||''))}catch(e){}SU=null}watchUntil=Date.now()+300000;load()}
function renderPost(){
  const el=$('#post'); let h=systemHtml();
  if(S.me&&!S.me.confirmed){el.innerHTML=onboardingHtml();document.body.classList.remove('noscroll');return}   // onboarding first; the system line comes after the profile
  for(const m of (S.messages||[])){ if(m.answer) continue; h+=`<div class="msg"><div class="q" style="margin:0 0 6px">${esc(m.kind||'Frage')}</div><div style="white-space:pre-wrap">${esc(m.text)}</div><div class="row"><button class="b p" onclick="answer('${m.id}','yes')">Ja</button><button class="b" onclick="answer('${m.id}','no')">Nein</button><button class="b s" onclick="answer('${m.id}','later')">Später</button></div></div>`; }
  h+=itemsHtml();
  const oc=openCard&&S.cards.find(c=>c.id===openCard);
  if(openCard&&!oc) openCard=null;
  if(oc) h+=`<div class="sheet" onclick="if(event.target===this){openCard=null;renderPost()}"><div class="sheetin"><div class="sheetbar"><span>${fmtDay(oc.slot)}, ${fmtTime(oc.slot)}, ${esc(oc.channel)}</span><button class="sm" onclick="openCard=null;renderPost()" title="schließen" aria-label="schließen">✕</button></div>${fullCardHtml(oc)}</div></div>`;
  document.body.classList.toggle('noscroll',!!oc);
  el.innerHTML=h;
}
let watchUntil=0;
async function decide(id,dec,reason){
  const note=($('#n-'+id)||{}).value||'';
  if(dec==='change'&&!note.trim()){toast('erst schreiben, was sich ändern soll');return}
  const o={a:'decide',card_id:id,decision:dec,note:note,reason:reason||''};
  const el=$('#t-'+id), c=S.cards.find(x=>x.id===id);
  if((dec==='post'||dec==='schedule')&&el&&c&&el.isContentEditable&&el.innerText.trim()!==c.text.trim()) o.text=el.innerText.trim();
  if(dec==='schedule'){o.when=($('#w-'+id)||{}).value||'';if(o.when.length<16){toast('erst Datum und Uhrzeit wählen');return}}
  const r=await post(o); if(r.error==='offline')return;
  toast(r.ok?({post:isAuto(c)?'geht raus …':'freigegeben, selbst posten',schedule:'geplant',change:MANUAL()?'notiert, kommt '+LATER:'notiert, wird überarbeitet …',skip:'verworfen',unschedule:'zurück zu entscheiden',photo_next:'Foto wird getauscht …'}[dec]):'Fehler');
  if(dec==='change'||dec==='photo_next'||dec==='post') watchUntil=Date.now()+240000;
  if(dec==='post'){setTimeout(tick,3000);setTimeout(tick,20000)}load();
}
function skipPost(id){$('#r-'+id).classList.toggle('on')}
async function uploadFor(id,inp){const fd=new FormData();fd.append('a','upload');fd.append('card_id',id);for(const f of inp.files)fd.append('photos[]',f,f.name||'photo.jpg');toast('lädt hoch …');let r={};try{r=await (await fetch(api,{method:'POST',body:fd})).json()}catch(e){r={failed:[e.message||'Netzwerkfehler']}}toast(r.ok?'hochgeladen, das Bild wechselt in etwa 20 s':'Upload fehlgeschlagen: '+((r.failed||[])[0]||'keine Datei angekommen'),r.ok?4000:12000);watchUntil=Date.now()+240000;load()}
async function markPosted(id){const url=($('#u-'+id)||{}).value||'';const r=await post({a:'decide',card_id:id,decision:'posted',url});if(r.error==='offline')return;toast(r.ok?'als veröffentlicht eingetragen':'Fehler');load()}
async function copyText(id){const t=$('#t-'+id).textContent;try{await navigator.clipboard.writeText(t);toast('Text kopiert')}catch(e){const ta=document.createElement('textarea');ta.value=t;document.body.appendChild(ta);ta.select();document.execCommand('copy');ta.remove();toast('Text kopiert')}}
async function answer(id,a){await post({a:'answer',id,answer:a});toast('notiert');load()}
async function logout(){await post({a:'logout'});location.reload()}
async function saveSettings(){const r=await post({a:'settings',expiry:$('#s-exp').value});toast(r.ok?'gespeichert':'Fehler');load()}
function renderComments(){
  const el=$('#comments'); const cs=S.queue.cards; let h='';
  const open=cs.filter(c=>!c.state);
  if(!cs.length) h='<div class="empty">Heute keine Kommentarkarten.</div>';
  for(const c of cs){
    const st=c.state?`<span class="pill">${esc(c.state)}</span>`:(c.kept?'<span class="pill ok">bis morgen behalten</span>':'');
    h+=`<div class="card ${c.state?'done':''}" style="padding:12px">
      <div class="q" style="margin:0;display:flex;justify-content:space-between"><span><b>${esc(c.who)}</b>${c.company?', '+esc(c.company):''}</span><span>${esc(c.kind||'Kommentar')}</span></div>
      <div class="q">${esc(c.why)}</div>
      ${c.first_line?`<div class="q">„${esc(c.first_line)}“</div>`:''}
      <div class="draft" id="d-${c.id}">${esc(c.draft)}</div>
      ${st}
      ${c.state?'':`<div class="row"><a class="b" href="${esc(c.url)}" target="_blank" rel="noopener" onclick="qdec('${c.id}','used',null,true)">${c.kind==='message'?'Profil öffnen':'Post öffnen'}</a><button class="b" onclick="copyDraft('${c.id}')">Kopieren</button><button class="b s" onclick="$('#qr-${c.id}').classList.toggle('on')">Überspringen</button></div>
      <div class="reasons" id="qr-${c.id}"><button class="sm s" onclick="qdec('${c.id}','skip','not the topic')">nicht das Thema</button><button class="sm s" onclick="qdec('${c.id}','skip','not the author')">nicht der Autor</button><button class="sm s" onclick="qdec('${c.id}','skip','')">ohne Grund</button>${c.kept?'':`<button class="sm s" onclick="qdec('${c.id}','keep')">Behalten</button>`}</div>`}
    </div>`;
  }
  if(open.length) h+=`<div class="row"><button class="b s" onclick="clearAll()">Alle leeren</button></div><div class="q" style="text-align:center">unberührte Karten verschwinden um ${esc(S.queue.expiry)}</div>`;
  el.innerHTML=h;
}
async function qdec(id,dec,reason,silent){await post({a:'queue',card_id:id,decision:dec,reason:reason||''});if(!silent){toast(dec);load()}else setTimeout(load,1500)}
async function copyDraft(id){const t=$('#d-'+id).textContent;try{await navigator.clipboard.writeText(t)}catch(e){}toast('Kommentar kopiert')}
async function clearAll(){await post({a:'queue',decision:'clear'});toast('geleert');load()}
let selPhoto=null;
function photoCell(p,s){const lab=(p.share==='network'?'geteilt, ':'')+(p.owner?'von '+p.owner+', ':'')+(p.status==='used'?(p.used_in||'benutzt')+(p.free_from?', frei ab '+fmtD(p.free_from):''):p.status==='new'?'neu':fmtD(s.date));
  return `<div class="ph ${selPhoto===p.id?'sel':''}" onclick="selPhoto=selPhoto==='${p.id}'?null:'${p.id}';renderPhotos()"><img src="${esc(p.thumb||p.url)}" loading="lazy">${(p.status==='new'||p.owner)?'':shareBtn(p.id,p.share==='network','pdec')}<span class="st">${esc(lab)}</span></div>`}
function actionBar(cells){const c=cells.find(x=>x.p.id===selPhoto);if(!c)return '';const {p,s}=c;
  return `<div class="pact"><div>${fmtD(s.date)}, ${esc(p.scene||s.label||'')}${p.status==='used'?', benutzt in '+esc(p.used_in||'')+(p.free_from?', frei ab '+fmtD(p.free_from):''):''}</div><div class="row">${p.status==='new'?'':`<button class="sm s" onclick="pdec('${s.id}','hold')">diese Serie nicht nutzen</button><button class="sm s" onclick="pdec('${p.id}','use_friday')">Freitagspost</button>`}<button class="sm s" onclick="pdec('${p.id}','delete')">löschen</button><button class="sm" onclick="selPhoto=null;renderPhotos()">schließen</button></div>
</div>`}
function networkHtml(){
  const net=netGroups(),inv=S.invites||[];
  const members=g=>g.members.length?g.members.map(x=>`<span class="chip">${esc(x.name)}${(x.shared||x.texts)?` <span style="color:var(--m)">${[x.shared?x.shared+' Fotos':'',x.texts?x.texts+' Texte':''].filter(Boolean).join(', ')}</span>`:''}</span>`).join(''):'<span style="color:var(--m);font-size:13px">noch niemand sonst</span>';
  const teams=net.map(g=>`<div class="team"><div class="team-h"><b style="flex:1">${esc(g.group)}</b>${net.length>1?`<button class="sm s" onclick="team('leave','${esc(g.group)}')">verlassen</button>`:''}<button class="plus" title="Jemanden einladen" onclick="inviteForm('${esc(g.group)}')">+</button></div><div class="chips">${members(g)}</div></div>`).join('');
  const invH=inv.length?`<div style="margin-top:10px;font-size:13px;color:var(--m)">Eingeladen: ${inv.slice().reverse().map(x=>`${esc(x.name)} (${esc(x.team)}, ${fmtD(x.ts)}, ${esc(x.state||'')})`).join(', ')}</div>`:'';
  return `<div class="card" style="padding:16px"><h2 style="margin:0 0 6px">Teams</h2>${teams}<div class="team-h" style="margin-top:12px"><span style="flex:1;color:var(--m);font-size:14px">Neues Team</span><button class="plus" title="Neues Team" onclick="teamForm()">+</button></div><div id="inv-box"></div>${invH}
    ${S.me?`<label style="display:flex;gap:8px;align-items:center;margin-top:14px;font-size:14px"><input type="checkbox" id="pf-share" style="width:auto;margin:0" ${(S.me||{}).share_default?'checked':''}> Neue Fotos standardmäßig für das Netzwerk freigeben</label>`:''}</div>`;
}
function netGroups(){return Array.isArray(S.network)?S.network:((S.network||{}).groups||[])}
function inviteForm(team){const net=netGroups().map(g=>g.group);const opts=net.map(g=>`<option value="${esc(g)}"${g===team?' selected':''}>${esc(g)}</option>`).join('')+`<option value="__new"${net.length?'':' selected'}>neues Team …</option>`;
  $('#inv-box').innerHTML=`<div class="msg" style="margin-top:10px"><div class="q" style="margin:0 0 6px">Wen lädst du ein?</div><input type="text" id="inv-name" placeholder="Vor- und Nachname"><div class="row" style="flex-wrap:wrap;align-items:center;font-size:14px"><span>Team</span><select id="inv-team" style="width:auto" onchange="$('#inv-new').style.display=this.value==='__new'?'':'none'">${opts}</select><input type="text" id="inv-new" placeholder="Name des neuen Teams (z. B. bni-starnberg)" style="${net.length?'display:none;':''}flex:1;min-width:180px"><span>Sprache</span><select id="inv-lang" style="width:auto"><option value="de">deutsch</option><option value="en">englisch</option></select></div><div class="row"><button class="b p" onclick="invite()">Board anlegen</button><button class="b s" onclick="$('#inv-box').innerHTML=''">Abbrechen</button></div></div>`;$('#inv-name').focus()}
function teamForm(){$('#inv-box').innerHTML=`<div class="msg" style="margin-top:10px"><div class="q" style="margin:0 0 6px">Neues Team: Kleinbuchstaben, Ziffern, Bindestrich. Du bist dann drin und kannst Leute einladen.</div><input type="text" id="team-name" placeholder="z. B. bni-starnberg oder firma-vertrieb"><div class="row"><button class="b p" onclick="team('join',$('#team-name').value)">Team anlegen</button><button class="b s" onclick="$('#inv-box').innerHTML=''">Abbrechen</button></div></div>`;$('#team-name').focus()}
async function team(doIt,name){if(doIt==='leave'&&!confirm(`Team ${name} verlassen? Du bekommst von dort nichts mehr vorgeschlagen.`))return;const r=await post({a:'team',do:doIt,team:name});toast(r.ok?(doIt==='leave'?'Team verlassen':'Team angelegt, du bist drin'):'Fehler: '+(r.error||''),4000);if(r.ok){$('#inv-box').innerHTML='';load()}}
async function invite(){const name=$('#inv-name').value.trim();let team=$('#inv-team').value;if(team==='__new')team=$('#inv-new').value.trim();if(!name||!team){toast('Name und Team');return}
  const r=await post({a:'invite',name,team,lang:$('#inv-lang').value});if(!r.ok){toast('Fehler: '+(r.error||''),6000);return}
  const t=r.text;$('#inv-box').innerHTML=`<div class="msg" style="margin-top:10px;border-color:#01BC56"><div class="q" style="margin:0 0 6px">Board für <b>${esc(name)}</b> im Team <b>${esc(r.team)}</b> angelegt. Schick das jetzt, das Startpasswort siehst du nur einmal:</div><pre id="inv-text" style="white-space:pre-wrap;font:inherit;font-size:14px;background:#fff;border:1px solid var(--b);border-radius:8px;padding:10px;margin:0">${esc(t)}</pre><div class="row" style="flex-wrap:wrap"><a class="b p" style="text-decoration:none" href="https://wa.me/?text=${encodeURIComponent(t)}" target="_blank">Per WhatsApp</a><a class="b s" style="text-decoration:none" href="mailto:?subject=${encodeURIComponent('Dein Board')}&body=${encodeURIComponent(t)}">Per Mail</a><button class="b s" onclick="copyInv()">Kopieren</button>${navigator.share?`<button class="b s" onclick="navigator.share({text:$('#inv-text').textContent})">Teilen …</button>`:''}</div></div>`;load()}
async function copyInv(){const t=$('#inv-text').textContent;try{await navigator.clipboard.writeText(t);toast('kopiert')}catch(e){toast('markieren und kopieren')}}
function profileHtml(){
  const m=S.me||{},T=v=>esc(v||''),st=m.style||{};
  const L=(t,id,v,rows)=>`<label class="hint" style="padding:0;margin-top:10px;display:block">${t}</label>`+(rows?`<textarea id="${id}" rows="${rows}">${T(v)}</textarea>`:`<input type="text" id="${id}" value="${T(v)}">`);
  const sel=(id,v,opts)=>`<select id="${id}" style="width:auto">${opts.map(([k,l])=>`<option value="${k}"${(v||'')===k?' selected':''}>${l}</option>`).join('')}</select>`;
  return networkHtml()+`
  <div class="card" style="padding:16px"><h2 style="margin:0 0 4px">Über dich</h2><div class="q" style="margin:0">Daraus baut das System jeden Entwurf. Was hier nicht steht, darf es nicht behaupten.</div>
    ${L('Was du machst','pf-role',m.role)}<div class="row" style="margin-top:0"><div style="flex:1">${L('Firma','pf-company',m.company)}</div><div style="flex:1">${L('Website','pf-website',m.website)}</div></div>
    ${L('Wer deine Posts lesen soll','pf-audience',m.audience)}${L('Was der Leser danach tun soll','pf-goal',m.goal)}${L('Was hängen bleiben soll','pf-offer',m.offer)}${L('Dein LinkedIn-Profil','pf-linkedin',m.linkedin)}
    <div class="row" style="flex-wrap:wrap;align-items:center;font-size:14px;margin-top:10px"><span>Posttag</span>${sel('pf-day',m.day||'Tue',[['Mon','Montag'],['Tue','Dienstag'],['Wed','Mittwoch'],['Thu','Donnerstag'],['Fri','Freitag'],['Sat','Samstag'],['Sun','Sonntag']])}</div></div>
  <div class="card" style="padding:16px"><h2 style="margin:0 0 4px">Themen</h2><div class="q" style="margin:0">Eine Zeile je Thema. Ein neues Thema wird beim nächsten Lauf zu einem Entwurf. Was unter „nie“ steht, kommt in keinem Post vor.</div>
    ${L('Worüber du schreiben willst','pf-topics',(m.topics||[]).join('\n'),6)}${L('Worüber nie','pf-avoid',(m.avoid||[]).join('\n'),3)}</div>
  <div class="card" style="padding:16px"><h2 style="margin:0 0 4px">Ton</h2><div class="q" style="margin:0">Drei Regler statt Prompt. Beispielposts, die dir gefallen, lernt das System als Rhythmus, kopiert aber nichts.</div>
    <div class="row" style="flex-wrap:wrap;align-items:center;font-size:14px"><span>Haltung</span>${sel('pf-register',st.register,[['','wie es passt'],['locker','locker'],['sachlich','sachlich']])}<span>Länge</span>${sel('pf-length',st.length||'mittel',[['kurz','kurz'],['mittel','mittel'],['lang','lang']])}<span>Frage am Ende</span>${sel('pf-question',st.question||'ja',[['ja','ja'],['nein','nein']])}</div>
    ${L('In deinen Worten: wie du klingen willst','pf-tone',m.tone)}${L('Zwei, drei Posts, die dir gefallen (deine oder fremde), durch Leerzeilen getrennt','pf-examples',m.examples,8)}</div>
  <div class="card" style="padding:16px"><h2 style="margin:0 0 4px">Fakten</h2><div class="q" style="margin:0">Eine Zeile je Fakt: Leistungen, Orte, Jahre, typische Kunden ohne Namen, belegte Ergebnisse. Nur was hier steht, darf ein Post nutzen.</div>${L('','pf-facts',m.facts,12)}</div>
  <div class="row" style="position:sticky;bottom:8px;margin-top:4px"><button class="b p" onclick="saveProfile()">Profil speichern</button></div>
  <div class="card" style="padding:16px;margin-top:14px"><h2 style="margin:0 0 4px">Zugang</h2><div class="row" style="margin-top:6px;flex-wrap:wrap"><input type="password" id="pw1" placeholder="neues Passwort, mindestens 10 Zeichen" style="flex:1;min-width:200px;border:1px solid var(--b);border-radius:8px;padding:9px;font:inherit;font-size:15px"><button class="b s" onclick="changePassword()">Passwort ändern</button><button class="b s" onclick="logout()">Abmelden</button></div></div>`;
}
let profileDirty=false;
function renderProfile(){const el=$('#profile');if($('#inv-box')&&$('#inv-box').innerHTML)return;   // an invitation in progress: never overwrite the one-time password
  if(!S.me){el.innerHTML=networkHtml()+`<div class="q" style="margin:10px 2px">Deine Fakten kommen aus dem Lebenslauf und dem Firmenkontext auf dem Mac, nicht von hier.</div>`;return}
  if(!S.me.confirmed){el.innerHTML=networkHtml()+`<div class="card" style="padding:16px"><div class="q" style="margin:0">Dein Profil erscheint hier, sobald es bestätigt ist. Das geht im Tab Posts.</div></div>`;return}
  if(profileDirty&&el.dataset.slug===S.me.slug)return;   // never overwrite what the person is typing
  el.innerHTML=profileHtml();el.dataset.slug=S.me.slug;el.querySelectorAll('input,textarea,select').forEach(x=>x.addEventListener('input',()=>profileDirty=true))}
async function saveProfile(){const v=id=>($('#'+id)||{}).value||'';const r=await post({a:'profile_save',role:v('pf-role'),company:v('pf-company'),website:v('pf-website'),audience:v('pf-audience'),offer:v('pf-offer'),topics:v('pf-topics'),avoid:v('pf-avoid'),tone:v('pf-tone'),examples:v('pf-examples'),facts:v('pf-facts'),goal:v('pf-goal'),linkedin:v('pf-linkedin'),day:v('pf-day'),style:{register:v('pf-register'),length:v('pf-length'),question:v('pf-question')},share_default:$('#pf-share').checked});
  profileDirty=false;toast(r.ok?'gespeichert, gilt ab dem nächsten Entwurf':'Fehler: '+(r.error||''),4000);load()}
async function changePassword(){const p=$('#pw1').value;if(p.length<10){toast('mindestens 10 Zeichen');return}const r=await post({a:'password',new:p});toast(r.ok?'Passwort geändert':'Fehler: '+(r.error||''),4000);if(r.ok)$('#pw1').value=''}
function renderPhotos(){
  const el=$('#photos'); const sm=S.photos.summary||{}; const shoots=S.photos.shoots||[]; const cut=new Date(Date.now()-30*86400000).toISOString().slice(0,10);
  const byId={}; for(const s of shoots) for(const p of (s.photos||[])) byId[p.id]={p,s};
  let h=`<form id="up" style="margin-bottom:10px"><label class="b p" style="display:block;text-align:center;border-radius:8px;padding:12px;background:var(--c);color:#fff;font-weight:600;cursor:pointer">+ Fotos hinzufügen<input type="file" name="photos[]" accept="image/*" multiple style="display:none" onchange="startUpload(this)"></label><input type="text" name="note" placeholder="Notiz zu diesen Fotos (optional)" style="margin-top:8px"><label style="display:flex;gap:8px;align-items:center;margin-top:8px;font-size:14px"><input type="checkbox" name="share" value="1" style="width:auto;margin:0" ${(S.me||{}).share_default?"checked":""}> für das Netzwerk freigeben</label></form>`;
  // 1. the photos already on planned posts, in slot order; tap opens the post
  const next=[...S.cards].sort((a,b)=>a.slot.localeCompare(b.slot)).filter(c=>c.photo&&byId[c.photo]).map(c=>({c,...byId[c.photo]}));
  h+=`<h2>Auf den nächsten Posts, ${next.length}</h2>`;
  h+=next.length?`<div class="grid">${next.map(x=>`<div class="ph" onclick="goCard('${x.c.id}')"><img src="${esc(x.p.thumb||x.p.url)}" loading="lazy"><span class="st">${fmtDay(x.c.slot)}, ${x.c.channel==='company'?'Unternehmen':'Profil'}</span></div>`).join('')}</div>`:'<div class="q">noch kein Poolfoto auf einem geplanten Post</div>';
  // 2. new: uploaded or shot in the last 30 days and still available
  const cells=[]; for(const p of S.pending) cells.push({p:{id:p.id,url:p.url,status:'new',scene:''},s:{id:'',date:p.ts.slice(0,10),label:'hochgeladen, wartet auf den Mac'}});
  for(const s of shoots) for(const p of (s.photos||[])) if(p.eligible&&s.date>=cut) cells.push({p,s});
  h+=`<h2>Neu, ${cells.length}</h2>`;
  h+=cells.length?`<div class="grid">${cells.map(c=>photoCell(c.p,c.s)).join('')}</div>`:'<div class="q">nichts Neues: Fotos aus der Kamerarolle hinzufügen, die Originale bleiben auf dem Handy</div>';
  // 3. archive: the older pool, used and held photos; hidden by default
  const arch=[]; for(const s of shoots) for(const p of (s.photos||[])) if(!(p.eligible&&s.date>=cut)) arch.push({p,s});
  const avail=arch.filter(x=>x.p.eligible).length;
  h+=`<h2>Archiv, ${arch.length}</h2><div class="q" style="margin:0 0 8px">${avail} frei, ${sm.used||0} benutzt</div>`;
  if(arch.length) h+=`<div class="row" style="margin:0 0 8px"><button class="sm s" onclick="showUsed=!showUsed;renderPhotos()">${showUsed?'Archiv ausblenden':'Archiv zeigen'}</button></div>`;
  if(showUsed) h+=`<div class="grid arch">${arch.map(c=>photoCell(c.p,c.s)).join('')}</div>`;
  h+=actionBar(cells.concat(showUsed?arch:[]));
  if(S.memos.length) h+=`<div class="set">Memos, die auf den Mac warten: ${S.memos.length}</div>`;
  el.innerHTML=h;
}
async function startUpload(inp){if(SU&&S.me&&!S.me.confirmed){SU.photos=(SU.photos||0)+inp.files.length;suSave()}const files=[...inp.files],note=$('#up').note.value,shareIt=$('#up').share.checked,B=3;let ok=0,failed=[];
  for(let i=0;i<files.length;i+=B){const fd=new FormData();fd.append('a','upload');fd.append('note',note);if(shareIt)fd.append('share','1');for(const f of files.slice(i,i+B))fd.append('photos[]',f,f.name||'photo.jpg');
    const mb=(files.slice(i,i+B).reduce((a,f)=>a+f.size,0)/1048576).toFixed(1);toast(`lädt ${Math.min(i+B,files.length)} von ${files.length} hoch (${mb} MB) …`,60000);
    let r=null;for(let t=0;t<2&&!r;t++){try{const res=await fetch(api,{method:'POST',body:fd});r=await res.json()}catch(e){if(t)failed.push(`${files.slice(i,i+B).map(f=>f.name).join(', ')}: ${e.message||'Netzwerkfehler'}`)}}
    if(r){ok+=(r.saved||[]).length;failed.push(...(r.failed||[]))}}
  inp.value='';toast(failed.length?`${ok} von ${files.length} hochgeladen, fehlgeschlagen: ${failed.slice(0,3).join(', ')}`:`${ok} hochgeladen, der Mac holt sie in spätestens 10 Minuten${shareIt?', dann sind sie freigegeben':''}`,failed.length?12000:4000);load()}
function confirmShare(what){return new Promise(res=>ask(`${what} für das Netzwerk freigeben? Die anderen im Team können daraus einen Post machen, mit deinem Namen drunter. Zurückziehen geht jederzeit.`,'Ja, freigeben',()=>res(true),()=>res(false)))}
async function pdec(id,dec){if(dec==='share'&&!(await confirmShare('dieses Foto')))return;const r=await post({a:'photo',id,decision:dec});toast(r.ok?({mark_used:'als benutzt markiert',hold:'zurückgehalten',use_friday:'für Freitag geplant',delete:'gelöscht',share:'freigegeben, gilt nach dem nächsten Lauf',unshare:'Freigabe zurückgezogen'}[dec]):'Fehler');load()}
// --- Record
let mr=null,chunks=[],t0=0,recCard=null;
// one recorder for both: the round button (memo or phrase) and "Record a note" on a card. While it runs, a bar at the
// bottom shows the time with ✕ discard and ✓ send (nothing leaves the phone before ✓); the round button also sends.
let recDiscard=false,recTimer=null;
async function startRec(cardId){
  if(mr&&mr.state==='recording')return;
  try{const st=await navigator.mediaDevices.getUserMedia({audio:true});const mime=MediaRecorder.isTypeSupported('audio/mp4')?'audio/mp4':(MediaRecorder.isTypeSupported('audio/webm')?'audio/webm':'');mr=new MediaRecorder(st,mime?{mimeType:mime}:{});chunks=[];t0=Date.now();recCard=cardId||null;recDiscard=false;
    mr.ondataavailable=e=>chunks.push(e.data);
    mr.onstop=()=>{st.getTracks().forEach(t=>t.stop());clearInterval(recTimer);$('#recbar').hidden=true;$('#rec').classList.remove('on');const b=recCard&&document.getElementById('rn-'+recCard);if(b)b.classList.remove('on');
      const cid=recCard,sec=Math.round((Date.now()-t0)/1000);recCard=null;
      if(recDiscard||sec<1){toast('Aufnahme verworfen');return}
      sendMemo(new Blob(chunks,{type:mr.mimeType||'audio/mp4'}),mr.mimeType||'audio/mp4',sec,cid)};
    mr.start();$('#rec').classList.add('on');const b=cardId&&document.getElementById('rn-'+cardId);if(b)b.classList.add('on');
    $('#recwhat').textContent=cardId?'Notiz zu diesem Post':'Memo oder Satz für einen Post';$('#rectime').textContent='0:00';$('#recbar').hidden=false;
    recTimer=setInterval(()=>{const s=Math.round((Date.now()-t0)/1000);$('#rectime').textContent=Math.floor(s/60)+':'+String(s%60).padStart(2,'0')},500);
  }catch(e){toast('Mikrofon nicht verfügbar: '+(e.name||e))}
}
function stopRec(send){if(!(mr&&mr.state==='recording'))return;recDiscard=!send;mr.stop()}
async function recNote(id){if(mr&&mr.state==='recording'){stopRec(true);return}startRec(id)}
$('#rec').onclick=()=>{if(mr&&mr.state==='recording'){stopRec(true);return}startRec(null)};
async function sendMemo(blob,mime,seconds,cardId){const fd=new FormData();fd.append('a','memo');fd.append('audio',blob,'memo');fd.append('mime',mime);fd.append('seconds',String(seconds));if(cardId)fd.append('card_id',cardId);toast(cardId?'Notiz wird gesendet …':'Memo wird gespeichert …');let r={};try{r=await (await fetch(api,{method:'POST',body:fd})).json()}catch(e){r={}}toast(r.ok?(cardId?'Notiz gesendet, der Post wird in etwa einer Minute überarbeitet':(MANUAL()?'Memo gespeichert, wird ein Post '+LATER:'Memo gespeichert, wird auf dem Mac ein Post oder ein Satz')):'Aufnahme fehlgeschlagen',4000);if(cardId)watchUntil=Date.now()+240000;load();return r}
async function tick(){try{const r=await (await fetch(api+'?a=tick&_='+Date.now())).json();if((r.published||[]).length){toast('veröffentlicht');load()}}catch(e){}}
load(); setInterval(load,60000); setInterval(tick,60000);
setInterval(()=>{if(document.activeElement&&document.activeElement.isContentEditable)return; if(S&&(Date.now()<watchUntil||S.profile_pending||S.cards.some(c=>(c.status==='change'&&!c.failed&&!MANUAL())||pend(c.image_pending)==='busy'||pend(c.note_pending)==='busy')))load()},5000);
</script>
</body>
</html>
