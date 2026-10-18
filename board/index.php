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
:root{--c:#20B8D0;--d:#0f3a50;--t:#1f2d3a;--m:#5a6b7a;--bg:#f2f9fb;--b:#d6e2ea;--tint:#BEF7FF}
*{box-sizing:border-box}
html,body{margin:0;background:#fff;color:var(--t);font:16px/1.45 -apple-system,"Helvetica Neue",Arial,sans-serif;-webkit-text-size-adjust:100%}
header{position:sticky;top:0;z-index:5;background:#fff;border-bottom:2px solid var(--c);padding:env(safe-area-inset-top) 0 0}
.top{display:flex;align-items:center;justify-content:space-between;padding:10px 14px 6px}
.top h1{font-size:17px;margin:0;color:var(--d)}
.top .sub{font-size:12px;color:var(--m)}
.tabs{display:flex}
.tabs button{flex:1;border:0;background:none;padding:8px 0 10px;font-size:14px;color:var(--m);border-bottom:3px solid transparent}
.tabs button.on{color:var(--d);font-weight:600;border-bottom-color:var(--d)}
main{max-width:720px;margin:0 auto;padding:12px 14px 40px}
.card{border:1px solid var(--b);border-radius:10px;padding:12px;margin:0 0 12px;background:#fff}
.card.done{opacity:.55}
.meta{font-size:12px;color:var(--m);display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap}
.pill{display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;background:var(--bg);color:var(--d);border:1px solid var(--b)}
.pill.ok{background:var(--tint)}
.img{position:relative;margin:10px 0;border-radius:8px;overflow:hidden;background:var(--bg)}
.img img{display:block;width:100%;height:auto;max-height:60vh;object-fit:contain}
.imgbar{display:flex;gap:6px;flex-wrap:wrap;margin:6px 0}
.txt{white-space:pre-wrap;font-size:15px;line-height:1.5;margin:8px 0}
.opt{display:flex;gap:6px;margin:8px 0}
.opt button{padding:4px 12px;border-radius:999px;border:1px solid var(--b);background:#fff;color:var(--m)}
.opt button.on{background:var(--d);color:#fff;border-color:var(--d)}
textarea,input[type=text],input[type=url]{width:100%;border:1px solid var(--b);border-radius:8px;padding:8px;font:inherit;font-size:15px}
.row{display:flex;gap:8px;margin-top:10px}
.row>*{flex:1}
button.b{border:1.5px solid var(--d);background:#fff;color:var(--d);border-radius:8px;padding:11px 10px;font:inherit;font-size:15px;font-weight:600}
button.b.p{background:var(--c);border-color:var(--c);color:#fff}
button.b.s{font-weight:400;color:var(--m);border-color:var(--b)}
button.sm{border:1px solid var(--d);background:#fff;color:var(--d);border-radius:6px;padding:5px 9px;font:inherit;font-size:13px}
button.sm.s{color:var(--m);border-color:var(--b)}
.q{font-style:italic;color:var(--m);font-size:14px;margin:6px 0}
.draft{background:var(--bg);border-left:3px solid var(--c);padding:8px 10px;border-radius:0 6px 6px 0;margin:6px 0;white-space:pre-wrap;font-size:15px}
.reasons{display:none;gap:6px;margin-top:8px}
.reasons.on{display:flex}
.empty{color:var(--m);text-align:center;padding:30px 10px}
.shoot h3{font-size:14px;margin:14px 0 6px;color:var(--d)}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}
.grid .ph{position:relative;aspect-ratio:1;background:var(--bg);border-radius:6px;overflow:hidden}
.grid .ph img{width:100%;height:100%;object-fit:cover;display:block}
.grid .ph .st{position:absolute;left:4px;bottom:4px;font-size:10px;background:rgba(255,255,255,.85);padding:1px 5px;border-radius:4px;color:var(--d)}
.grid .ph.used{opacity:.4}
.rec{position:fixed;right:14px;bottom:calc(14px + env(safe-area-inset-bottom));width:58px;height:58px;border-radius:50%;border:0;background:var(--d);color:#fff;font-size:22px;box-shadow:0 4px 14px rgba(0,0,0,.25);z-index:6}
.rec.on{background:#d33;animation:p 1s infinite}
@keyframes p{50%{transform:scale(1.08)}}
.toast{position:fixed;left:50%;bottom:90px;transform:translateX(-50%);background:var(--d);color:#fff;padding:8px 14px;border-radius:999px;font-size:14px;opacity:0;transition:opacity .2s;z-index:7;pointer-events:none}
.toast.on{opacity:1}
.set{font-size:13px;color:var(--m);margin:16px 0 0}
.set input{width:70px;padding:4px 6px;font-size:14px}
.msg{border:1.5px solid var(--c);background:var(--bg);border-radius:10px;padding:12px;margin:0 0 12px}
@media(min-width:720px){.tabs button{font-size:15px}.txt{font-size:16px}}
</style>
</head>
<body>
<header>
 <div class="top"><div><h1>Board</h1><div class="sub" id="sub">lädt …</div></div><div class="sub" id="clock"></div></div>
 <div class="tabs"><button class="on" data-t="post">Post</button><button data-t="comments">Comments</button><button data-t="photos">Photos</button></div>
</header>
<main>
 <section id="post"></section>
 <section id="comments" hidden></section>
 <section id="photos" hidden></section>
</main>
<button class="rec" id="rec" title="Record">●</button>
<div class="toast" id="toast"></div>
<script>
const $=s=>document.querySelector(s), api='api.php';
let S=null, tab='post', optSel={}, recState=null;
const toast=m=>{const t=$('#toast');t.textContent=m;t.classList.add('on');setTimeout(()=>t.classList.remove('on'),1800)};
const post=async(o)=>{const r=await fetch(api,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(o)});return r.json()};
const fmtSlot=s=>{const d=new Date(s);return d.toLocaleDateString('de-DE',{weekday:'short',day:'2-digit',month:'2-digit'})+' · '+d.toLocaleTimeString('de-DE',{hour:'2-digit',minute:'2-digit'})};
const esc=s=>(s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
async function load(){S=await (await fetch(api+'?a=state&_='+Date.now())).json();render()}
function showTab(n){tab=n;document.querySelectorAll('.tabs button').forEach(x=>x.classList.toggle('on',x.dataset.t===n));['post','comments','photos'].forEach(t=>$('#'+t).hidden=t!==tab);history.replaceState(null,'','#'+n)}
document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>showTab(b.dataset.t));
if(['post','comments','photos'].includes(location.hash.slice(1))) showTab(location.hash.slice(1));
function render(){
  const open=S.cards.filter(c=>!['posted','skipped'].includes(c.status)).length, qOpen=S.queue.cards.filter(c=>!c.state).length;
  $('#sub').textContent=`${open} post${open===1?'':'s'} · ${qOpen} comment${qOpen===1?'':'s'} · until ${S.queue.expiry}`;
  $('#clock').textContent=new Date(S.now).toLocaleTimeString('de-DE',{hour:'2-digit',minute:'2-digit'});
  renderPost(); renderComments(); renderPhotos();
}
function renderPost(){
  const el=$('#post'); let h='';
  for(const m of (S.messages||[])){ if(m.answer) continue; h+=`<div class="msg"><div class="meta"><span>${esc(m.kind||'question')}</span></div><div class="txt">${esc(m.text)}</div><div class="row"><button class="b p" onclick="answer('${m.id}','yes')">Yes</button><button class="b" onclick="answer('${m.id}','no')">No</button><button class="b s" onclick="answer('${m.id}','later')">Later</button></div></div>`; }
  const cards=[...S.cards].sort((a,b)=>a.slot.localeCompare(b.slot));
  if(!cards.length) h+='<div class="empty">No cards. Next drafts arrive by '+esc(S.settings.review)+'.</div>';
  for(const c of cards){
    const opts=Object.keys(c.options||{}); const sel=optSel[c.id]||c.option||opts[0];
    const st={draft:'draft',approved:'approved for '+fmtSlot(c.slot),change:'change requested',skipped:'skipped',posted:'posted'}[c.status]||c.status;
    const past=new Date(c.slot)<new Date(S.now);
    h+=`<div class="card ${['posted','skipped'].includes(c.status)?'done':''}" id="c-${c.id}">
      <div class="meta"><span>${esc(c.channel)} · ${esc(c.lang)} · ${esc(c.pillar||'')}</span><span>${fmtSlot(c.slot)}</span></div>
      <div class="meta" style="margin-top:4px"><span class="pill ${c.status==='approved'?'ok':''}">${esc(st)}</span>${c.status==='approved'&&past?'<span class="pill ok">post it yourself</span>':''}</div>
      ${c.image?`<div class="img"><img src="${esc(c.image.url)}" alt=""></div><div class="imgbar"><a class="sm" style="text-decoration:none;display:inline-block" href="${esc(c.image.final||c.image.url)}" download="${esc(c.id)}.jpg">Save image</a><button class="sm s" onclick="toast('Other / Crop come with the photo pool')">Other</button><button class="sm s" onclick="toast('Crop comes with the photo pool')">Crop</button></div>`:''}
      ${opts.length>1?`<div class="opt">${opts.map(o=>`<button class="${o===sel?'on':''}" onclick="optSel['${c.id}']='${o}';renderPost()">Option ${o}</button>`).join('')}</div>`:''}
      <div class="txt" id="t-${c.id}">${esc((c.options||{})[sel]||c.text||'')}</div>
      <div class="row"><button class="sm" onclick="copyText('${c.id}')">Copy text</button></div>
      ${c.note?`<div class="q">note: ${esc(c.note)}</div>`:''}
      ${['draft','change'].includes(c.status)?`
      <textarea id="n-${c.id}" rows="2" placeholder="note for a change (optional)"></textarea>
      <div class="row"><button class="b p" onclick="decide('${c.id}','post')">Post</button><button class="b" onclick="decide('${c.id}','change')">Change + note</button><button class="b s" onclick="skipPost('${c.id}')">Skip</button></div>
      <div class="reasons" id="r-${c.id}"><button class="sm s" onclick="decide('${c.id}','skip','not the topic')">not the topic</button><button class="sm s" onclick="decide('${c.id}','skip','not the form')">not the form</button><button class="sm s" onclick="decide('${c.id}','skip','')">no reason</button></div>`:''}
      ${c.status==='approved'?`<input type="url" id="u-${c.id}" placeholder="LinkedIn post URL (optional)" style="margin-top:10px"><div class="row"><button class="b" onclick="markPosted('${c.id}')">Mark posted</button></div>`:''}
    </div>`;
  }
  h+=`<div class="set">Settings · comments expire at <input type="text" id="s-exp" value="${esc(S.settings.expiry)}"> · drafts ready by <input type="text" id="s-rev" value="${esc(S.settings.review)}" style="width:110px"> <button class="sm s" onclick="saveSettings()">save</button></div>`;
  el.innerHTML=h;
}
async function decide(id,dec,reason){
  const opt=optSel[id]||(S.cards.find(c=>c.id===id)||{}).option; const note=($('#n-'+id)||{}).value||'';
  if(dec==='change'&&!note.trim()){toast('write a note first');return}
  const r=await post({a:'decide',card_id:id,decision:dec,option:opt,note:note,reason:reason||''});
  toast(r.ok?({post:'approved',change:'change requested',skip:'skipped'}[dec]):'error'); load();
}
function skipPost(id){$('#r-'+id).classList.toggle('on')}
async function markPosted(id){const url=($('#u-'+id)||{}).value||'';const r=await post({a:'decide',card_id:id,decision:'posted',url});toast(r.ok?'logged as posted':'error');load()}
async function copyText(id){const t=$('#t-'+id).textContent;try{await navigator.clipboard.writeText(t);toast('text copied')}catch(e){const ta=document.createElement('textarea');ta.value=t;document.body.appendChild(ta);ta.select();document.execCommand('copy');ta.remove();toast('text copied')}}
async function answer(id,a){await post({a:'answer',id,answer:a});toast('noted');load()}
async function saveSettings(){const r=await post({a:'settings',expiry:$('#s-exp').value,review:$('#s-rev').value});toast(r.ok?'saved':'error');load()}
function renderComments(){
  const el=$('#comments'); const cs=S.queue.cards; let h='';
  const open=cs.filter(c=>!c.state);
  if(!cs.length) h='<div class="empty">No comment cards today.</div>';
  for(const c of cs){
    const st=c.state?`<span class="pill">${esc(c.state)}</span>`:(c.kept?'<span class="pill ok">kept until tomorrow</span>':'');
    h+=`<div class="card ${c.state?'done':''}">
      <div class="meta"><span><b>${esc(c.who)}</b>${c.company?' · '+esc(c.company):''}</span><span>${esc(c.kind||'comment')}</span></div>
      <div class="q">${esc(c.why)}</div>
      ${c.first_line?`<div class="q">„${esc(c.first_line)}“</div>`:''}
      <div class="draft" id="d-${c.id}">${esc(c.draft)}</div>
      ${st}
      ${c.state?'':`<div class="row"><a class="b" style="text-align:center;text-decoration:none;padding:11px 6px" href="${esc(c.url)}" target="_blank" rel="noopener" onclick="qdec('${c.id}','used',null,true)">${c.kind==='message'?'Open profile':'Open post'}</a><button class="b" onclick="copyDraft('${c.id}')">Copy</button><button class="b s" onclick="$('#qr-${c.id}').classList.toggle('on')">Skip</button></div>
      <div class="reasons" id="qr-${c.id}"><button class="sm s" onclick="qdec('${c.id}','skip','not the topic')">not the topic</button><button class="sm s" onclick="qdec('${c.id}','skip','not the author')">not the author</button><button class="sm s" onclick="qdec('${c.id}','skip','')">no reason</button>${c.kept?'':`<button class="sm s" onclick="qdec('${c.id}','keep')">Keep</button>`}</div>`}
    </div>`;
  }
  if(open.length) h+=`<div class="row"><button class="b s" onclick="clearAll()">Clear all</button></div><div class="q" style="text-align:center">untouched cards vanish at ${esc(S.queue.expiry)}</div>`;
  el.innerHTML=h;
}
async function qdec(id,dec,reason,silent){await post({a:'queue',card_id:id,decision:dec,reason:reason||''});if(!silent){toast(dec);load()}else setTimeout(load,1500)}
async function copyDraft(id){const t=$('#d-'+id).textContent;try{await navigator.clipboard.writeText(t)}catch(e){}toast('comment copied')}
async function clearAll(){await post({a:'queue',decision:'clear'});toast('cleared');load()}
function renderPhotos(){
  const el=$('#photos'); let h=`<form id="up" style="margin-bottom:12px"><label class="b p" style="display:block;text-align:center;border-radius:8px;padding:12px;background:var(--c);color:#fff;font-weight:600">+ Add photo<input type="file" name="photos[]" accept="image/*" multiple style="display:none" onchange="startUpload(this)"></label><input type="text" name="note" placeholder="one line only if the picture needs it (optional)" style="margin-top:8px"></form>`;
  if(S.pending.length){h+=`<div class="shoot"><h3>uploaded · ${S.pending.length} · waiting for the night run</h3><div class="grid">${S.pending.map(p=>`<div class="ph"><img src="${esc(p.url)}" loading="lazy"><span class="st">new</span></div>`).join('')}</div><div class="row">${S.pending.map(p=>`<button class="sm s" onclick="pdec('${p.id}','delete')">delete ${esc(p.id.slice(11,15))}</button>`).join('')}</div></div>`}
  for(const s of (S.photos.shoots||[])){
    h+=`<div class="shoot"><h3>${esc(s.date)} · ${esc(s.label||'')} · <span class="pill ${s.status==='ready'?'ok':''}">${esc(s.status)}</span></h3><div class="grid">${(s.photos||[]).map(p=>`<div class="ph ${p.status==='used'?'used':''}"><img src="${esc(p.thumb)}" loading="lazy"><span class="st">${esc(p.status)}${p.used_in?' · '+esc(p.used_in):''}</span></div>`).join('')}</div>
      ${s.status==='used'?'':`<div class="row" style="margin-top:6px"><button class="sm" onclick="pdec('${s.id}','use_friday')">Use Friday</button><button class="sm s" onclick="pdec('${s.id}','mark_used')">Mark shoot used</button></div>`}</div>`;
  }
  if(!S.pending.length&&!(S.photos.shoots||[]).length) h+='<div class="empty">Pool is empty. Add photos from the camera roll; originals stay on the phone.</div>';
  if(S.memos.length) h+=`<div class="set">memos waiting for transcription: ${S.memos.length}</div>`;
  el.innerHTML=h;
}
async function startUpload(inp){const fd=new FormData($('#up'));fd.append('a','upload');toast('uploading '+inp.files.length+' …');const r=await (await fetch(api,{method:'POST',body:fd})).json();toast(r.ok?`${r.saved.length} uploaded`:'upload failed');load()}
async function pdec(id,dec){await post({a:'photo',id,decision:dec});toast(dec.replace('_',' '));load()}
// --- Record
let mr=null,chunks=[],t0=0;
$('#rec').onclick=async()=>{
  if(mr&&mr.state==='recording'){mr.stop();return}
  try{const st=await navigator.mediaDevices.getUserMedia({audio:true});const mime=MediaRecorder.isTypeSupported('audio/mp4')?'audio/mp4':(MediaRecorder.isTypeSupported('audio/webm')?'audio/webm':'');mr=new MediaRecorder(st,mime?{mimeType:mime}:{});chunks=[];t0=Date.now();
    mr.ondataavailable=e=>chunks.push(e.data);
    mr.onstop=async()=>{st.getTracks().forEach(t=>t.stop());$('#rec').classList.remove('on');const blob=new Blob(chunks,{type:mr.mimeType||'audio/mp4'});const fd=new FormData();fd.append('a','memo');fd.append('audio',blob,'memo');fd.append('mime',mr.mimeType||'audio/mp4');fd.append('seconds',String(Math.round((Date.now()-t0)/1000)));toast('saving memo …');const r=await (await fetch(api,{method:'POST',body:fd})).json();toast(r.ok?'memo saved':'memo failed');load()};
    mr.start();$('#rec').classList.add('on');toast('recording … press again to stop')}catch(e){toast('microphone not available')}
};
load(); setInterval(load,60000);
</script>
</body>
</html>
