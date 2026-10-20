<?php header('Cache-Control: no-store'); header('X-Robots-Tag: noindex, nofollow'); ?>
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
textarea,input[type=text],input[type=url]{width:100%;border:1px solid var(--b);border-radius:8px;padding:9px;font:inherit;font-size:15px;background:#fff}
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
.toast{position:fixed;left:50%;bottom:90px;transform:translateX(-50%);background:var(--d);color:#fff;padding:8px 14px;border-radius:999px;font-size:14px;opacity:0;transition:opacity .2s;z-index:7;pointer-events:none}
.toast.on{opacity:1}
.set{font-size:13px;color:var(--m);margin:16px 0 0}
.set input{width:70px;padding:4px 6px;font-size:14px}
.msg{border:1.5px solid var(--c);background:var(--bg);border-radius:10px;padding:12px;margin:0 0 12px}
.sys{border-radius:10px;padding:10px 12px;margin:0 0 12px;font-size:13px;background:var(--warn);border:1px solid #f3d9a4;color:#7a4b00}
.sys b{display:block;font-size:14px;color:#8a2a00}
.sys code{display:block;white-space:pre-wrap;font-size:12px;background:#fff;padding:6px 8px;border-radius:6px;margin:4px 0}
.sys.ok{background:#fff;border-color:var(--b);color:var(--m)}
#side{display:none}
@media(min-width:960px){
  main{display:grid;grid-template-columns:minmax(0,1fr) 330px;gap:28px;align-items:start}
  #side{display:block;position:sticky;top:92px;order:2}
  #content{order:1}
  #inline-pipe{display:none}
  .tabs button{font-size:15px}
  .card.full{display:grid;grid-template-columns:minmax(0,1fr) 300px}
  .card.full .post{min-width:0;border-right:1px solid var(--b)}
  .card.full .act{border-top:0;align-self:start}
  .img img{max-height:560px}
  .grid{grid-template-columns:repeat(6,1fr)}
}
</style>
</head>
<body>
<header>
 <div class="top"><div><h1>Board</h1><div class="sub" id="sub">lädt …</div></div><div class="sub" id="clock"></div></div>
 <div class="tabs"><button class="on" data-t="post">Post</button><button data-t="comments">Comments</button><button data-t="photos">Photos</button></div>
</header>
<main>
 <div id="content">
  <section id="post"></section>
  <section id="comments" hidden></section>
  <section id="photos" hidden></section>
 </div>
 <aside id="side"></aside>
</main>
<button class="rec" id="rec" title="Record">●</button>
<div class="recbar" id="recbar" hidden><span class="dot"></span><span id="recwhat">recording</span><span id="rectime" class="t">0:00</span><button class="x" onclick="stopRec(false)" title="discard">✕</button><button class="ok" onclick="stopRec(true)" title="send">✓</button></div>
<div class="toast" id="toast"></div>
<script>
const $=s=>document.querySelector(s), api='api.php';
let S=null, tab='post', expanded={}, showUsed=false, showAllUp=false, showAllPub=false;
let toastT=null;const toast=(m,ms=1800)=>{const t=$('#toast');t.textContent=m;t.classList.add('on');clearTimeout(toastT);toastT=setTimeout(()=>t.classList.remove('on'),ms)};
const post=async(o)=>{const r=await fetch(api,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(o)});return r.json()};
const fmtSlot=s=>{const d=new Date(s);return d.toLocaleDateString('de-DE',{weekday:'short',day:'2-digit',month:'2-digit'})+' · '+d.toLocaleTimeString('de-DE',{hour:'2-digit',minute:'2-digit'})};
const fmtDay=s=>new Date(s).toLocaleDateString('de-DE',{weekday:'short',day:'2-digit',month:'2-digit'});
const fmtTime=s=>new Date(s).toLocaleTimeString('de-DE',{hour:'2-digit',minute:'2-digit'});
const fmtD=s=>s?new Date(s).toLocaleDateString('de-DE',{day:'2-digit',month:'2-digit'}):'';
const esc=s=>(s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const STATUS={draft:'to decide',approved:'approved',change:'being updated',skipped:'skipped',posted:'posted',scheduled:'scheduled in LinkedIn'};
let BUILD=null;
async function load(){const st=await (await fetch(api+'?a=state&_='+Date.now())).json(); if(BUILD===null)BUILD=st.build; const busy=(document.activeElement&&(document.activeElement.isContentEditable||/^(TEXTAREA|INPUT)$/.test(document.activeElement.tagName)))||(mr&&mr.state==='recording'); if(st.build&&st.build!==BUILD&&!busy){location.reload();return} if(document.activeElement&&document.activeElement.isContentEditable){S=st;return} S=st;render()}
function showTab(n){tab=n;document.querySelectorAll('.tabs button').forEach(x=>x.classList.toggle('on',x.dataset.t===n));['post','comments','photos'].forEach(t=>$('#'+t).hidden=t!==tab);history.replaceState(null,'','#'+n)}
document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>showTab(b.dataset.t));
if(['post','comments','photos'].includes(location.hash.slice(1))) showTab(location.hash.slice(1));
const byHand=c=>c.status==='approved'&&new Date(c.slot)<new Date(S.now)&&!isAuto(c);   // approved, due, channel not connected: Anton posts it himself
const needs=c=>c.status==='draft'||(c.status==='change'&&c.failed)||byHand(c);
function render(){
  const open=S.cards.filter(needs).length, qOpen=S.queue.cards.filter(c=>!c.state).length;
  const hand=S.cards.filter(byHand).length;
  $('#sub').textContent=`${open-hand} to decide${hand?` · ${hand} to post by hand`:''} · ${qOpen} comment${qOpen===1?'':'s'} · until ${S.queue.expiry}`;
  $('#clock').textContent=new Date(S.now).toLocaleTimeString('de-DE',{hour:'2-digit',minute:'2-digit'});
  $('#side').innerHTML=renderPipeline(); renderPost(); renderComments(); renderPhotos();
}
function isAuto(c){const li=(S.health||{}).linkedin||{};return !!(li.connected&&(c.channel==='personal'||li.org))}
function statusPill(c){
  const past=new Date(c.slot)<new Date(S.now);
  if(c.status==='scheduled') return `<span class="pill li">scheduled in LinkedIn · ${fmtTime(c.slot)}</span>`;
  const auto=isAuto(c);
  if(c.status==='change') return c.failed?`<span class="pill warn">update failed · decide again</span>`:`<span class="pill warn">being updated · about a minute</span>`;
  if(c.status==='scheduled') return `<span class="pill li">scheduled by you in the LinkedIn app · ${fmtSlot(c.slot)}</span>`;
  if(c.status==='approved') return past?(auto?`<span class="pill ok">posting now …</span>`:`<span class="pill todo">waits for you: post it by hand</span> <span class="pill warn">${c.channel==='company'?'company page':'profile'} not connected to the API</span>`):auto?`<span class="pill ok">scheduled · posts itself ${fmtSlot(c.slot)}</span>`:`<span class="pill ok">scheduled ${fmtSlot(c.slot)}</span> <span class="pill warn">${c.channel==='company'?'company page not connected: you post it then':'LinkedIn not connected: you post it then'}</span>`;
  if(c.status==='draft') return (c.updated?`<span class="pill ok">updated per your note</span> `:'')+(c.image_pending?`<span class="pill warn">image being changed · about 20 s</span> `:'')+(c.note_pending?`<span class="pill warn">voice note on its way · about a minute</span> `:'')+`<span class="pill todo">to decide</span>`;
  return `<span class="pill">${esc(STATUS[c.status]||c.status)}</span>`;
}
function renderPipeline(){
  const P=S.pipeline||{upcoming:[],published:[]}; const today=(S.now||'').slice(0,10);
  const up=showAllUp?P.upcoming:P.upcoming.slice(0,8), pub=showAllPub?P.published:P.published.slice(0,5);
  let h='<h2>Next</h2><div class="pipe">';
  for(const u of up){
    const link=S.cards.some(c=>c.id===u.id);
    h+=`<div class="r ${link?'link':''} ${u.when.slice(0,10)===today?'today':''}" ${link?`onclick="goCard('${u.id}')"`:''}>
      <div class="d">${fmtDay(u.when)}<br>${fmtTime(u.when)}</div>
      <div><span class="pill ${u.status==='scheduled'?'li':u.status==='approved'?'ok':u.status==='draft'?'todo':u.status==='change'?'warn':''}">${esc(u.status==='scheduled'?'LinkedIn (you)':u.status==='draft'?'decide':u.status==='change'?'updating':u.status==='approved'?'scheduled':u.status)}</span><span class="pill">${esc(u.channel)}${u.pillar?' · '+esc(u.pillar):''}</span><div class="h">${esc(u.hook)}</div></div></div>`;
  }
  if(!up.length) h+='<div class="r"><div class="d"></div><div class="h">drafts arrive with the next run</div></div>';
  if(P.upcoming.length>8) h+=`<button class="more" onclick="showAllUp=!showAllUp;render()">${showAllUp?'less':'all '+P.upcoming.length}</button>`;
  const mat=P.material||{}; const mk=Object.keys(mat);
  if(mk.length) h+=`<div class="mat">material: ${mk.map(k=>esc(k)+' '+mat[k]).join(' · ')}${(P.memos||[]).some(m=>m.status==='new')?' · memo waiting':''}</div>`;
  h+='</div><h2>Published</h2><div class="pipe">';
  for(const p of pub){
    const n=[p.impressions&&p.impressions+' imp',p.reactions&&p.reactions+' react',p.comments&&p.comments+' comm'].filter(Boolean).join(' · ');
    h+=`<div class="r"><div class="d">${fmtDay(p.date)}</div><div><span class="pill">${esc(p.channel)}</span><div class="h">${esc(p.hook)}</div><div class="n">${esc(n)||'numbers missing'}</div></div></div>`;
  }
  if(!pub.length) h+='<div class="r"><div class="d"></div><div class="h">—</div></div>';
  if(P.published.length>5) h+=`<button class="more" onclick="showAllPub=!showAllPub;render()">${showAllPub?'less':'all '+P.published.length+' posts'}</button>`;
  if((P.featured||[]).length) h+=`<div class="mat">Featured on your profile should be: ${P.featured.map(f=>esc(f.hook.slice(0,50))+' ('+f.impressions+' imp)').join(' · ')}</div>`;
  else if(P.metrics_missing) h+=`<div class="mat">no numbers for ${P.metrics_missing} posts yet: export them from LinkedIn into library/metrics/inbox, or wait for the API</div>`;
  return h+'</div>';
}
function goCard(id){const el=document.getElementById('c-'+id);if(!el)return;expanded[id]=true;renderPost();showTab('post');document.getElementById('c-'+id).scrollIntoView({behavior:'smooth',block:'start'})}
function postHtml(c){
  const who=c.channel==='company'?`<div class="ava co">A</div><div><div class="n">AlpiType</div><div class="s">company page · ${esc(c.lang)} · ${fmtSlot(c.slot)}${c.pillar?' · '+esc(c.pillar):''}</div></div>`
                                 :`<div class="ava">AL</div><div><div class="n">Anton Lytvynenko</div><div class="s">personal · ${esc(c.lang)} · ${fmtSlot(c.slot)}${c.pillar?' · '+esc(c.pillar):''}</div></div>`;
  const ed=needs(c);
  const imgTools=(ed||c.status==='approved')?`<div class="imgtools">${c.channel==='personal'?`<button class="sm s" onclick="decide('${c.id}','photo_next')">Next photo from the pool</button>`:''}<label class="lbl">Upload another image<input type="file" accept="image/*" style="display:none" onchange="uploadFor('${c.id}',this)"></label><span class="hint" style="padding:0">replaces the picture, text stays</span></div>`:'';
  return `<div class="who">${who}</div><div class="txt ${(c.status==='change'&&!c.failed)||c.note_pending?'busy':''}" id="t-${c.id}" ${ed?'contenteditable="plaintext-only" spellcheck="false"':''}>${esc(c.text)}</div>${ed?'<div class="hint">tap the text to change a word; Post takes what you see</div>':''}${c.image?`<div class="img ${c.image_pending?'busy':''}"><img src="${esc(c.image.url)}" alt="">${c.image_pending?'<div class="spin"><i></i><span>replacing the picture …</span></div>':''}</div>`:'<div class="q" style="padding:0 14px 10px">no image</div>'}${imgTools}`;
}
function systemHtml(){
  const H=S.health||{}; const seen=H.ts?Math.round((new Date(S.now)-new Date(H.ts))/60000):null; const issues=[...(H.issues||[])];
  if(seen===null) issues.unshift({what:'Mac',log:'no health report yet',fix:'check launchctl list | grep board-sync on the Mac'});
  else if(seen>45) issues.unshift({what:'Mac',log:`last run ${seen} min ago, presses wait on the server`,fix:'wake the Mac; if awake: launchctl kickstart gui/501/com.alpitype.board-sync, then library/log/board-sync.err'});
  const li=H.linkedin||{};
  if(!issues.length) return `<div class="sys ok">system ok · last run ${seen} min ago · ${H.slots_planned||0} posts planned · ${H.topics_unused||0} topics left · ${H.rules_learned||0} preferences learned · $${H.month_cost_usd||0} this month · LinkedIn ${li.connected?'connected until '+fmtD(li.expires)+(li.org?' incl. company page':' (personal only)'):'not connected: approved posts you copy and post yourself'}</div>`;
  return issues.map(i=>`<div class="sys"><b>${esc(i.what)}${i.what.startsWith('one post')?'':' needs a fix'}${i.times>1?' · '+i.times+' times':''}</b>${esc(i.log||'')}<code>${esc(i.fix||'')}</code></div>`).join('');
}
function renderPost(){
  const el=$('#post'); let h=systemHtml();
  for(const m of (S.messages||[])){ if(m.answer) continue; h+=`<div class="msg"><div class="q" style="margin:0 0 6px">${esc(m.kind||'question')}</div><div style="white-space:pre-wrap">${esc(m.text)}</div><div class="row"><button class="b p" onclick="answer('${m.id}','yes')">Yes</button><button class="b" onclick="answer('${m.id}','no')">No</button><button class="b s" onclick="answer('${m.id}','later')">Later</button></div></div>`; }
  const cards=[...S.cards].sort((a,b)=>(needs(a)?0:1)-(needs(b)?0:1)||a.slot.localeCompare(b.slot));
  if(!cards.some(needs)) h+='<div class="empty">Nothing to decide. New drafts appear here as soon as a slot opens.</div>';
  for(const c of cards){
    const past=new Date(c.slot)<new Date(S.now), act=needs(c), done=['posted','skipped'].includes(c.status);
    if(!act&&!expanded[c.id]){
      const manual=c.status==='approved'&&!isAuto(c);
      const tools=`<div class="tools">${manual?`<button class="sm s" onclick="copyText('${c.id}')">Copy</button>${c.image?`<a class="sm s" href="${esc(c.image.final||c.image.url)}" download="${esc(c.id)}.jpg">Image</a>`:''}`:''}<button class="sm s" onclick="expanded['${c.id}']=true;renderPost()">Show</button></div>`;
      h+=`<div class="card ${done?'done':''}" id="c-${c.id}"><div class="compact"><div class="d">${fmtDay(c.slot)}<br>${fmtTime(c.slot)}</div><div class="h"><b>${esc(c.channel)}</b> · ${esc(c.text.split('\n')[0])}</div>${tools}<div class="pills">${statusPill(c)}</div></div><div hidden id="t-${c.id}">${esc(c.text)}</div></div>`;
      continue;
    }
    h+=`<div class="card full ${done?'done':''}" id="c-${c.id}"><div class="post">${postHtml(c)}
      ${c.note?`<div class="note ${c.failed?'fail':''}">${c.failed?'could not apply: ':(c.updated?'applied: ':'your note: ')}${esc(c.note)}</div>`:''}
      <div style="padding:8px 14px 12px;display:flex;gap:6px;flex-wrap:wrap;align-items:center">${statusPill(c)}${c.versions?`<span class="pill">v${c.versions+1}</span>`:''}${(c.status==='approved'&&!isAuto(c))?`<button class="sm s" onclick="copyText('${c.id}')">Copy text</button>${c.image?`<a class="sm s" href="${esc(c.image.final||c.image.url)}" download="${esc(c.id)}.jpg">Download image</a>`:''}`:''}${act?'':`<button class="sm s" onclick="expanded['${c.id}']=false;renderPost()">Hide</button>`}</div></div>
      <div class="act">
        ${byHand(c)?`<div class="q" style="margin:0 0 8px">1. Copy text · 2. Download image · 3. post both in LinkedIn as ${c.channel==='company'?'AlpiType':'yourself'} · 4. Mark posted</div>
        <button class="b" style="width:100%" onclick="copyText('${c.id}')">Copy text</button>
        ${c.image?`<a class="b" style="display:block;margin-top:8px" href="${esc(c.image.final||c.image.url)}" download="${esc(c.id)}.jpg">Download image</a>`:''}
        <input type="url" id="u-${c.id}" placeholder="LinkedIn post URL (optional)" style="margin-top:12px"><button class="b p" style="width:100%;margin-top:6px" onclick="markPosted('${c.id}')">Mark posted</button>
        <div class="row"><button class="b s" onclick="decide('${c.id}','unschedule')">Back to decide</button></div>
        <div class="q" style="margin:8px 0 0;font-size:13px">${c.channel==='company'?'the company page posts itself once LinkedIn grants the Community Management API (docs/linkedin-setup.md, step 6)':'reconnect LinkedIn: pipeline/linkedin_auth.py'}</div>`
        :act?`<button class="b p" style="width:100%" onclick="decide('${c.id}','post')">${isAuto(c)?'Post now':'Post now · by hand'}</button>
        <div class="q" style="margin:4px 0 0;font-size:13px">${isAuto(c)?'goes out within about 20 seconds':(c.channel==='company'?'company page':'profile')+' is not connected to the API: the card comes to the top with Copy text, Download image and Mark posted'}</div>
        <input type="datetime-local" id="w-${c.id}" value="${esc(c.slot.slice(0,16))}" style="margin-top:12px">
        <button class="b" style="width:100%;margin-top:6px" onclick="decide('${c.id}','schedule')">Schedule</button>
        <textarea id="n-${c.id}" rows="3" placeholder="Note for this post: what to change, or a rule for all posts (immer …, nie …)" style="margin-top:12px"></textarea>
        <div class="row" style="margin-top:6px"><button class="b" style="flex:1" onclick="decide('${c.id}','change')">Update the post</button><button class="b s rn" id="rn-${c.id}" onclick="recNote('${c.id}')">● Record a note</button></div>
        <div class="q" style="margin:4px 0 0;font-size:13px">typed or spoken: applied in about a minute, the post comes back here to decide; a general remark becomes a rule for all posts</div>
        <div class="row"><button class="b s" onclick="skipPost('${c.id}')">Drop</button></div>
        <div class="q" style="margin:4px 0 0;font-size:13px">removes this post for good; the slot gets a new draft</div>
        <div class="reasons" id="r-${c.id}"><button class="sm s" onclick="decide('${c.id}','skip','not the topic')">not the topic</button><button class="sm s" onclick="decide('${c.id}','skip','not the form')">not the form</button><button class="sm s" onclick="decide('${c.id}','skip','')">no reason</button></div>`
        :c.status==='approved'?`${past?'':`<button class="b p" style="width:100%" onclick="decide('${c.id}','post')">${isAuto(c)?'Post now':'Post now · by hand'}</button>`}<div class="row"><button class="b" onclick="decide('${c.id}','unschedule')">Unschedule</button></div><div class="q" style="margin:4px 0 0;font-size:13px">back to decide; nothing is posted</div>`
        :c.status==='scheduled'?`<div class="row"><button class="b" onclick="decide('${c.id}','unschedule')">Unschedule</button></div><div class="q" style="margin:4px 0 0;font-size:13px">you scheduled this one in the LinkedIn app; the board cannot reach it. Cancel it there first, then press Unschedule here and it comes back to decide</div>`
        :c.status==='change'?`<div class="q">being rewritten with your note; it comes back here to decide</div>`
        :`<div class="q">${esc(STATUS[c.status]||c.status)}</div>`}
      </div></div>`;
  }
  h+=`<div id="inline-pipe">${renderPipeline()}</div>`;
  h+=`<div class="set">Settings · comments expire at <input type="text" id="s-exp" value="${esc(S.settings.expiry)}"> <button class="sm s" onclick="saveSettings()">save</button></div>`;
  el.innerHTML=h;
}
let watchUntil=0;
async function decide(id,dec,reason){
  const note=($('#n-'+id)||{}).value||'';
  if(dec==='change'&&!note.trim()){toast('write what to change first');return}
  const o={a:'decide',card_id:id,decision:dec,note:note,reason:reason||''};
  const el=$('#t-'+id), c=S.cards.find(x=>x.id===id);
  if((dec==='post'||dec==='schedule')&&el&&c&&el.isContentEditable&&el.innerText.trim()!==c.text.trim()) o.text=el.innerText.trim();
  if(dec==='schedule'){o.when=($('#w-'+id)||{}).value||'';if(o.when.length<16){toast('pick date and time first');return}}
  const r=await post(o);
  toast(r.ok?({post:isAuto(c)?'posting …':'approved · post it yourself',schedule:'scheduled',change:'noted · updating …',skip:'dropped',unschedule:'back to decide',photo_next:'changing the photo …'}[dec]):'error');
  if(dec==='change'||dec==='photo_next'||dec==='post') watchUntil=Date.now()+240000;
  load();
}
function skipPost(id){$('#r-'+id).classList.toggle('on')}
async function uploadFor(id,inp){const fd=new FormData();fd.append('a','upload');fd.append('card_id',id);for(const f of inp.files)fd.append('photos[]',f,f.name||'photo.jpg');toast('uploading …');let r={};try{r=await (await fetch(api,{method:'POST',body:fd})).json()}catch(e){r={failed:[e.message||'network error']}}toast(r.ok?'uploaded · the picture changes in about 20 s':'upload failed: '+((r.failed||[])[0]||'no file arrived'),r.ok?4000:12000);watchUntil=Date.now()+240000;load()}
async function markPosted(id){const url=($('#u-'+id)||{}).value||'';const r=await post({a:'decide',card_id:id,decision:'posted',url});toast(r.ok?'logged as posted':'error');load()}
async function copyText(id){const t=$('#t-'+id).textContent;try{await navigator.clipboard.writeText(t);toast('text copied')}catch(e){const ta=document.createElement('textarea');ta.value=t;document.body.appendChild(ta);ta.select();document.execCommand('copy');ta.remove();toast('text copied')}}
async function answer(id,a){await post({a:'answer',id,answer:a});toast('noted');load()}
async function saveSettings(){const r=await post({a:'settings',expiry:$('#s-exp').value});toast(r.ok?'saved':'error');load()}
function renderComments(){
  const el=$('#comments'); const cs=S.queue.cards; let h='';
  const open=cs.filter(c=>!c.state);
  if(!cs.length) h='<div class="empty">No comment cards today.</div>';
  for(const c of cs){
    const st=c.state?`<span class="pill">${esc(c.state)}</span>`:(c.kept?'<span class="pill ok">kept until tomorrow</span>':'');
    h+=`<div class="card ${c.state?'done':''}" style="padding:12px">
      <div class="q" style="margin:0;display:flex;justify-content:space-between"><span><b>${esc(c.who)}</b>${c.company?' · '+esc(c.company):''}</span><span>${esc(c.kind||'comment')}</span></div>
      <div class="q">${esc(c.why)}</div>
      ${c.first_line?`<div class="q">„${esc(c.first_line)}“</div>`:''}
      <div class="draft" id="d-${c.id}">${esc(c.draft)}</div>
      ${st}
      ${c.state?'':`<div class="row"><a class="b" href="${esc(c.url)}" target="_blank" rel="noopener" onclick="qdec('${c.id}','used',null,true)">${c.kind==='message'?'Open profile':'Open post'}</a><button class="b" onclick="copyDraft('${c.id}')">Copy</button><button class="b s" onclick="$('#qr-${c.id}').classList.toggle('on')">Skip</button></div>
      <div class="reasons" id="qr-${c.id}"><button class="sm s" onclick="qdec('${c.id}','skip','not the topic')">not the topic</button><button class="sm s" onclick="qdec('${c.id}','skip','not the author')">not the author</button><button class="sm s" onclick="qdec('${c.id}','skip','')">no reason</button>${c.kept?'':`<button class="sm s" onclick="qdec('${c.id}','keep')">Keep</button>`}</div>`}
    </div>`;
  }
  if(open.length) h+=`<div class="row"><button class="b s" onclick="clearAll()">Clear all</button></div><div class="q" style="text-align:center">untouched cards vanish at ${esc(S.queue.expiry)}</div>`;
  el.innerHTML=h;
}
async function qdec(id,dec,reason,silent){await post({a:'queue',card_id:id,decision:dec,reason:reason||''});if(!silent){toast(dec);load()}else setTimeout(load,1500)}
async function copyDraft(id){const t=$('#d-'+id).textContent;try{await navigator.clipboard.writeText(t)}catch(e){}toast('comment copied')}
async function clearAll(){await post({a:'queue',decision:'clear'});toast('cleared');load()}
let selPhoto=null;
function photoCell(p,s){const lab=p.status==='used'?(p.used_in||'used')+(p.free_from?' · free '+fmtD(p.free_from):''):p.status==='new'?'new':fmtD(s.date);
  return `<div class="ph ${selPhoto===p.id?'sel':''}" onclick="selPhoto=selPhoto==='${p.id}'?null:'${p.id}';renderPhotos()"><img src="${esc(p.thumb||p.url)}" loading="lazy"><span class="st">${esc(lab)}</span></div>`}
function actionBar(cells){const c=cells.find(x=>x.p.id===selPhoto);if(!c)return '';const {p,s}=c;
  return `<div class="pact"><div>${fmtD(s.date)} · ${esc(p.scene||s.label||'')}${p.status==='used'?' · used in '+esc(p.used_in||'')+(p.free_from?', free from '+fmtD(p.free_from):''):''}</div><div class="row">${p.status==='new'?'':`<button class="sm s" onclick="pdec('${s.id}','hold')">don't use this shoot</button><button class="sm s" onclick="pdec('${p.id}','use_friday')">Friday post</button>`}<button class="sm s" onclick="pdec('${p.id}','delete')">delete</button><button class="sm" onclick="selPhoto=null;renderPhotos()">close</button></div></div>`}
function renderPhotos(){
  const el=$('#photos'); const sm=S.photos.summary||{};
  let h=`<form id="up" style="margin-bottom:10px"><label class="b p" style="display:block;text-align:center;border-radius:8px;padding:12px;background:var(--c);color:#fff;font-weight:600;cursor:pointer">+ Add photos<input type="file" name="photos[]" accept="image/*" multiple style="display:none" onchange="startUpload(this)"></label><input type="text" name="note" placeholder="note for these photos (optional)" style="margin-top:8px"></form>`;
  h+=`<div class="q" style="margin:0 0 10px"><b>${sm.eligible||0}</b> available · ${sm.used||0} used${sm.next_free?' (next free '+fmtD(sm.next_free)+')':''} · ${sm.hold||0} held back · the system picks; tap a photo for options</div>`;
  const shoots=S.photos.shoots||[]; const cells=[];
  for(const p of S.pending) cells.push({p:{id:p.id,url:p.url,status:'new',scene:''},s:{id:'',date:p.ts.slice(0,10),label:'uploaded, waiting for the Mac'}});
  for(const s of shoots) for(const p of (s.photos||[])) if(p.eligible) cells.push({p,s});
  h+=`<div class="grid">${cells.map(c=>photoCell(c.p,c.s)).join('')}</div>`;
  if(!cells.length) h+='<div class="empty">No photo available right now. Add photos from the camera roll; originals stay on the phone.</div>';
  const rest=[];for(const s of shoots) for(const p of (s.photos||[])) if(!p.eligible) rest.push({p,s});
  if(rest.length){h+=`<div class="row" style="margin-top:12px"><button class="sm s" onclick="showUsed=!showUsed;renderPhotos()">${showUsed?'hide used and held':'used and held · '+rest.length}</button></div>`; if(showUsed) h+=`<div class="grid" style="margin-top:8px">${rest.map(c=>photoCell(c.p,c.s)).join('')}</div>`}
  h+=actionBar(cells.concat(showUsed?rest:[]));
  if(S.memos.length) h+=`<div class="set">memos waiting for the Mac: ${S.memos.length}</div>`;
  el.innerHTML=h;
}
async function startUpload(inp){const files=[...inp.files],note=$('#up').note.value,B=3;let ok=0,failed=[];
  for(let i=0;i<files.length;i+=B){const fd=new FormData();fd.append('a','upload');fd.append('note',note);for(const f of files.slice(i,i+B))fd.append('photos[]',f,f.name||'photo.jpg');
    const mb=(files.slice(i,i+B).reduce((a,f)=>a+f.size,0)/1048576).toFixed(1);toast(`uploading ${Math.min(i+B,files.length)} of ${files.length} (${mb} MB) …`,60000);
    let r=null;for(let t=0;t<2&&!r;t++){try{const res=await fetch(api,{method:'POST',body:fd});r=await res.json()}catch(e){if(t)failed.push(`${files.slice(i,i+B).map(f=>f.name).join(', ')}: ${e.message||'network error'}`)}}
    if(r){ok+=(r.saved||[]).length;failed.push(...(r.failed||[]))}}
  inp.value='';toast(failed.length?`${ok} of ${files.length} uploaded · failed: ${failed.slice(0,3).join(' · ')}`:`${ok} uploaded · the Mac fetches them within 10 minutes`,failed.length?12000:4000);load()}
async function pdec(id,dec){const r=await post({a:'photo',id,decision:dec});toast(r.ok?({mark_used:'marked used',hold:'held back',use_friday:'planned for Friday',delete:'deleted'}[dec]):'error');load()}
// --- Record
let mr=null,chunks=[],t0=0,recCard=null;
// one recorder for both: the round button (memo or phrase) and "Record a note" on a card. While it runs, a bar at the
// bottom shows the time with ✕ discard and ✓ send (nothing leaves the phone before ✓); the round button also sends.
let recDiscard=false,recTimer=null;
async function startRec(cardId){
  if(mr&&mr.state==='recording')return;
  try{const st=await navigator.mediaDevices.getUserMedia({audio:true});const mime=MediaRecorder.isTypeSupported('audio/mp4')?'audio/mp4':(MediaRecorder.isTypeSupported('audio/webm')?'audio/webm':'');mr=new MediaRecorder(st,mime?{mimeType:mime}:{});chunks=[];t0=Date.now();recCard=cardId||null;recDiscard=false;
    mr.ondataavailable=e=>chunks.push(e.data);
    mr.onstop=()=>{st.getTracks().forEach(t=>t.stop());clearInterval(recTimer);$('#recbar').hidden=true;$('#rec').classList.remove('on');const b=recCard&&document.getElementById('rn-'+recCard);if(b){b.textContent='● Record a note';b.classList.remove('on')}
      const cid=recCard,sec=Math.round((Date.now()-t0)/1000);recCard=null;
      if(recDiscard||sec<1){toast('recording discarded');return}
      sendMemo(new Blob(chunks,{type:mr.mimeType||'audio/mp4'}),mr.mimeType||'audio/mp4',sec,cid)};
    mr.start();$('#rec').classList.add('on');const b=cardId&&document.getElementById('rn-'+cardId);if(b){b.textContent='■ recording';b.classList.add('on')}
    $('#recwhat').textContent=cardId?'note for this post':'memo or phrase for a post';$('#rectime').textContent='0:00';$('#recbar').hidden=false;
    recTimer=setInterval(()=>{const s=Math.round((Date.now()-t0)/1000);$('#rectime').textContent=Math.floor(s/60)+':'+String(s%60).padStart(2,'0')},500);
  }catch(e){toast('microphone not available: '+(e.name||e))}
}
function stopRec(send){if(!(mr&&mr.state==='recording'))return;recDiscard=!send;mr.stop()}
async function recNote(id){if(mr&&mr.state==='recording'){stopRec(true);return}startRec(id)}
$('#rec').onclick=()=>{if(mr&&mr.state==='recording'){stopRec(true);return}startRec(null)};
async function sendMemo(blob,mime,seconds,cardId){const fd=new FormData();fd.append('a','memo');fd.append('audio',blob,'memo');fd.append('mime',mime);fd.append('seconds',String(seconds));if(cardId)fd.append('card_id',cardId);toast(cardId?'sending your note …':'saving memo …');let r={};try{r=await (await fetch(api,{method:'POST',body:fd})).json()}catch(e){r={}}toast(r.ok?(cardId?'note sent · the post is updated in about a minute':'memo saved · becomes a post or a phrase on the Mac'):'recording failed',4000);if(cardId)watchUntil=Date.now()+240000;load();return r}
load(); setInterval(load,60000);
setInterval(()=>{if(document.activeElement&&document.activeElement.isContentEditable)return; if(S&&(Date.now()<watchUntil||S.cards.some(c=>(c.status==='change'&&!c.failed)||c.image_pending||c.note_pending)))load()},5000);
</script>
</body>
</html>
