<?php
// Board API. State lives in data/. Decisions are appended as JSONL and pulled by the Mac.
declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
date_default_timezone_set('Europe/Berlin');
$D = __DIR__ . '/data';
require __DIR__ . '/auth.php'; require __DIR__ . '/boards.php';
$a0 = $_GET['a'] ?? $_POST['a'] ?? '';
if (!in_array($a0, ['ping', 'tick'], true) && !auth_check()) { http_response_code(401); echo json_encode(['error' => 'login']); exit; }   // a person's board: session cookie or nothing; ping (change stamp) and tick (publisher) carry no data and stay open for the worker
foreach (['decisions','uploads/photos','uploads/memos','uploads/profile','queue','img'] as $p) { if (!is_dir("$D/$p")) mkdir("$D/$p", 0755, true); }

function jread(string $f, $def) { return is_file($f) ? (json_decode((string)file_get_contents($f), true) ?? $def) : $def; }
function jwrite(string $f, $v): void { file_put_contents($f, json_encode($v, JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES), LOCK_EX); }
function decide(array $d): void {
  global $D; $d['ts'] = date('c');
  file_put_contents("$D/decisions/" . date('Y-m-d') . ".jsonl", json_encode($d, JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES) . "\n", FILE_APPEND|LOCK_EX);
}
function out($v): never { echo json_encode($v, JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES); exit; }
function settings(): array { global $D; return array_merge(['expiry' => '18:00', 'review' => 'Sat 08:00'], jread("$D/settings.json", [])); }

// Overlays = decisions taken here since the last Mac push, so the UI reflects them immediately.
// The Mac pushes applied.json {until: ts} once a decision is folded into the CSVs; older overlay entries are then ignored.
function fresh(?array $st): bool {
  global $D; if (!$st) return false; $u = jread("$D/applied.json", [])['until'] ?? '';
  return !$u || empty($st['ts']) || strtotime($st['ts']) > strtotime($u);
}
function overlay_cards(array $cards): array {
  global $D; $ov = jread("$D/overlay.json", []);
  foreach ($cards as &$c) { $st = $ov['cards'][$c['id']] ?? null; if (fresh($st)) $c = array_merge($c, $st); }
  return $cards;
}
function overlay_photos(array $ph): array {
  global $D; $ov = jread("$D/overlay.json", [])['photos'] ?? [];
  foreach ($ph['shoots'] ?? [] as &$s) {
    $ss = $ov[$s['id']] ?? null; $shoot_used = fresh($ss) && $ss['state'] === 'mark_used'; $shoot_hold = fresh($ss) && $ss['state'] === 'hold';
    if (fresh($ss) && $ss['state'] === 'use_friday') $s['label'] = 'friday';
    foreach ($s['photos'] as &$p) {
      $ps = $ov[$p['id']] ?? null;
      if ($shoot_used || (fresh($ps) && $ps['state'] === 'mark_used')) { if ($p['status'] !== 'used') { $p['status'] = 'used'; $p['used_in'] = $p['used_in'] ?: 'manual'; $p['eligible'] = false; } }
      if ($shoot_hold || (fresh($ps) && $ps['state'] === 'hold')) { $p['status'] = 'hold'; $p['eligible'] = false; }
      if (fresh($ps) && $ps['state'] === 'use_friday') $p['label'] = 'friday';
    } unset($p);
    $st = array_values(array_unique(array_column($s['photos'], 'status')));
    $s['status'] = ($st === ['used']) ? 'used' : ($st === ['hold'] ? 'hold' : (in_array('new', $st, true) ? 'new' : 'ready'));
    $s['eligible'] = (bool)array_filter($s['photos'], fn($p) => !empty($p['eligible']));
  } unset($s);
  return $ph;
}
function overlay_pipeline(array $pipe): array {   // posts Anton logged as published himself, and numbers he typed, show before the Mac folds them into the CSVs
  global $D; $ov = jread("$D/overlay.json", []); $pipe['published'] = $pipe['published'] ?? [];
  $have = array_column($pipe['published'], 'id');
  foreach ($ov['published'] ?? [] as $id => $st) {
    if (!fresh($st) || in_array($id, $have, true)) continue;
    array_unshift($pipe['published'], ['id' => $id, 'date' => $st['date'] ?? '', 'channel' => $st['channel'] ?? 'personal', 'hook' => $st['hook'] ?? '', 'impressions' => '', 'reactions' => '', 'comments' => '', 'link' => $st['url'] ?? '', 'numbers_at' => '']);
  }
  foreach ($pipe['published'] as &$p) {
    $st = $ov['metrics'][$p['id']] ?? null; if (!fresh($st)) continue;
    foreach (['impressions', 'reactions', 'comments'] as $k) if (isset($st[$k]) && $st[$k] !== '') $p[$k] = $st[$k];
    $p['numbers_at'] = substr((string)$st['ts'], 0, 16);
  } unset($p);
  foreach ($pipe['memos'] ?? [] as &$m) { $st = $ov['memos'][$m['id']] ?? null; if (fresh($st)) $m['share'] = $st['share']; } unset($m);   // a memo shared here shows before the Mac folds it (04.11.)
  // S4: proposals Anton already confirmed or dropped here disappear at once; S3: a typed week shows before the Mac folds it in
  $pipe['inbound_proposed'] = array_values(array_filter($pipe['inbound_proposed'] ?? [], fn($q) => !fresh($ov['inbound'][$q['id']] ?? null)));
  $pipe['profile_weekly'] = $pipe['profile_weekly'] ?? [];
  foreach ($ov['profile'] ?? [] as $week => $st) {
    if (!fresh($st)) continue; $found = false;
    foreach ($pipe['profile_weekly'] as &$w) { if (($w['week'] ?? '') === $week) { $w['visits'] = $st['visits']; $found = true; } } unset($w);
    if (!$found) $pipe['profile_weekly'][] = ['week' => $week, 'visits' => $st['visits']];
  }
  usort($pipe['published'], fn($a, $b) => strcmp((string)$b['date'], (string)$a['date']));
  return $pipe;
}
function set_overlay(string $kind, string $id, array $patch): void {
  global $D; $lk = fopen("$D/.overlay.lock", 'c'); flock($lk, LOCK_EX);   // read-modify-write under one lock (page ticks, cron and taps run at the same time)
  $ov = jread("$D/overlay.json", []); $cur = $ov[$kind][$id] ?? [];
  if ($kind === 'cards' && isset($patch['status'])) unset($cur['image_pending'], $cur['note_pending'], $cur['publish_error']);   // a new decision ends what was pending
  $ov[$kind][$id] = array_merge($cur, $patch, ['ts' => date('c')]); jwrite("$D/overlay.json", $ov); flock($lk, LOCK_UN); fclose($lk);
}
function today_queue(): array {
  global $D; $s = settings(); $today = date('Y-m-d'); $f = "$D/queue/$today.json";
  $q = jread($f, ['date' => $today, 'cards' => []]);
  $ov = jread("$D/overlay.json", []);
  $now = time(); [$eh, $em] = array_map('intval', explode(':', $s['expiry'])); $exp = mktime($eh, $em, 0);
  $out = [];
  foreach ($q['cards'] as $c) {
    $st = $ov['queue'][$c['id']] ?? [];
    $c = array_merge($c, $st); unset($c['ts']);
    if (empty($c['state'])) {
      if ($now > $exp && empty($c['kept'])) { $c['state'] = 'expired'; set_overlay('queue', $c['id'], ['state' => 'expired']); decide(['type'=>'comment','card_id'=>$c['id'],'decision'=>'expired']); }
    }
    // kept cards from yesterday are merged by the Mac into today's queue file; nothing to do here
    $out[] = $c;
  }
  $q['cards'] = $out; $q['expiry'] = $s['expiry'];
  return $q;
}

$a = $_GET['a'] ?? $_POST['a'] ?? '';
$body = [];
if (($_SERVER['CONTENT_TYPE'] ?? '') === 'application/json') { $body = json_decode((string)file_get_contents('php://input'), true) ?? []; $a = $body['a'] ?? $a; }

switch ($a) {
  case 'tick': // run the server-side publisher (server/publish.php lives outside public_html in ~/board-worker); at most once a minute
    $home = $_SERVER['HOME'] ?? (getenv('HOME') ?: dirname(__DIR__, 5)); $wf = "$home/board-worker/publish.php"; $tf = "$D/.tick";   // web PHP has no HOME: public_html/board/<token> is five levels below it
    if (!is_file($wf)) out(['ok' => false, 'error' => 'no worker on the server']);
    if (is_file($tf) && filemtime($tf) > time() - 55) out(['ok' => true, 'skipped' => 'ran less than a minute ago']);
    touch($tf); putenv("BOARD_DATA=$D"); $argv = []; require_once $wf; out(['ok' => true] + run());

  case 'ping': // cheap change stamp: the worker polls this every few seconds and runs the chain when it moves
    $st = 0;
    foreach (array_merge(glob("$D/decisions/*.jsonl"), glob("$D/uploads/photos/*"), glob("$D/uploads/memos/*")) as $f) $st = max($st, filemtime($f) * 1000 + (filesize($f) % 1000));
    out(['stamp' => $st, 'now' => date('c')]);

  case 'state':
    $cards = overlay_cards(jread("$D/cards.json", []));
    $photos = overlay_photos(jread("$D/photos.json", ['shoots' => []]));
    $pipe = overlay_pipeline(jread("$D/pipeline.json", ['upcoming' => [], 'published' => []]));
    $pending = [];
    foreach (glob("$D/uploads/photos/*") as $f) { $pending[] = ['id' => basename($f), 'url' => 'data/uploads/photos/' . rawurlencode(basename($f)), 'ts' => date('c', filemtime($f))]; }
    $memos = [];
    foreach (glob("$D/uploads/memos/*") as $f) { $memos[] = ['id' => basename($f), 'ts' => date('c', filemtime($f)), 'bytes' => filesize($f)]; }
    $msg = jread("$D/messages.json", []);
    $health = jread("$D/health.json", ['ts' => '', 'issues' => []]);
    $me = auth_user(); $me = $me ? ['slug' => $me['slug'], 'name' => $me['name'], 'lang' => $me['lang'] ?? 'de'] + jread("$D/profile.json", []) : null;   // profile.json: pushed by the worker (onboard.py)
    $props = jread("$D/proposals.json", []); $pov = jread("$D/overlay.json", [])['proposals'] ?? [];   // shared photos offered on cards (match.py); a tap here shows before the worker folds it
    foreach ($props as $cid => &$pp) { if (fresh($pov[$cid] ?? null)) $pp['state'] = $pov[$cid]['state']; } unset($pp);
    $profile_pending = is_file("$D/uploads/profile/request.json");
    $self = boards_self(auth_user()); $net = boards_network($self, jread("$D/network.json", []));   // my groups, who else is in them (registry, immediate), how many photos they share (match.py)
    if ($me) $me['groups'] = $self['groups'];
    $inv = jread("$D/invites.json", []); $BD = dirname(__DIR__);
    foreach ($inv as &$iv) { $au = jread("$BD/{$iv['token']}/data/auth.json", []); $iv['state'] = !empty($au['disabled']) ? 'gesperrt' : (empty($au['must_change']) && !empty($au['changed']) ? 'angemeldet' : 'wartet auf erste Anmeldung'); unset($iv['token']); } unset($iv);
    out(['me' => $me, 'board' => $self, 'network' => $net, 'invites' => $inv, 'proposals' => $props, 'profile_pending' => $profile_pending, 'health' => $health, 'cards' => $cards, 'pipeline' => $pipe, 'queue' => today_queue(), 'photos' => $photos, 'pending' => $pending, 'memos' => $memos, 'settings' => settings(), 'messages' => $msg, 'now' => date('c'), 'build' => (int)filemtime(__DIR__ . '/index.php')]);   // build: the page reloads itself after a deploy

  case 'decide': // post card: post (now) | schedule (when) | change (note) | skip | posted | unschedule | photo_next
    $id = (string)($body['card_id'] ?? ''); $dec = (string)($body['decision'] ?? '');
    if ($id === '' || !in_array($dec, ['post','schedule','change','skip','posted','unschedule','photo_next','order'], true)) out(['error' => 'bad request']);
    if ($dec === 'order') { // order = card ids of one channel in the wanted sequence; they take their existing slots in that sequence
      $ids = array_values(array_filter(array_map(fn($x) => preg_replace('/[^\w-]/', '', (string)$x), (array)($body['order'] ?? []))));
      $cards = overlay_cards(jread("$D/cards.json", [])); $slots = [];
      foreach ($cards as $c) if (in_array($c['id'], $ids, true) && ($c['status'] ?? '') !== 'scheduled') $slots[$c['id']] = $c['slot'];
      $ids = array_values(array_filter($ids, fn($x) => isset($slots[$x]))); $free = array_values($slots); sort($free);
      if (count($ids) < 2) out(['error' => 'nothing to reorder']);
      $stat = []; foreach ($cards as $c) $stat[$c['id']] = (jread("$D/overlay.json", [])['cards'][$c['id']]['status'] ?? $c['status']);
      foreach ($ids as $i => $cid) if ($stat[$cid] === 'approved' && $free[$i] < date('Y-m-d\TH:i')) out(['error' => "$cid is approved and would land in a slot that has passed, it would post at once; unschedule it first"]);
      foreach ($ids as $i => $cid) set_overlay('cards', $cid, ['slot' => $free[$i], 'decided' => date('c')]);
      decide(['type'=>'post','card_id'=>$ids[0],'decision'=>'order','order'=>$ids]);
      out(['ok' => true, 'slots' => array_combine($ids, array_slice($free, 0, count($ids)))]);
    }
    $known = array_column(jread("$D/cards.json", []), 'id'); if (!in_array($id, $known, true)) out(['error' => 'unknown card']);
    if (isset($body['text']) && strlen((string)$body['text']) > 4000) out(['error' => 'text too long']);
    $status = ['post'=>'approved','schedule'=>'approved','change'=>'change','skip'=>'skipped','posted'=>'posted','unschedule'=>'draft'][$dec] ?? null;
    $patch = ['decided' => date('c')]; if ($status) $patch['status'] = $status;
    if ($dec === 'post') $patch['slot'] = date('Y-m-d\TH:i');
    if ($dec === 'schedule') { $w = preg_replace('/[^0-9T:-]/', '', (string)($body['when'] ?? '')); if (strlen($w) < 16) out(['error' => 'when missing']); $patch['slot'] = substr($w, 0, 16); $body['when'] = $patch['slot']; }
    if ($dec === 'photo_next') $patch['image_pending'] = time();
    foreach (['option','image_id','note','reason','url','text','when'] as $k) if (isset($body[$k]) && $body[$k] !== '') $patch[$k] = $body[$k];
    set_overlay('cards', $id, $patch);   // text: the post as Anton edited it on the card; shown at once, written to the draft by the worker
    decide(['type'=>'post','card_id'=>$id,'decision'=>$dec] + array_intersect_key($patch, array_flip(['option','image_id','note','reason','url','text','when'])));
    out(['ok' => true, 'status' => $patch['status'] ?? '']);

  case 'queue': // comment card: used | skip | keep | clear
    $dec = (string)($body['decision'] ?? ''); $id = (string)($body['card_id'] ?? '');
    if ($dec === 'clear') {
      foreach (today_queue()['cards'] as $c) if (empty($c['state'])) { set_overlay('queue', $c['id'], ['state' => 'cleared']); }
      decide(['type'=>'comment','card_id'=>'*','decision'=>'clear']); out(['ok'=>true]);
    }
    if ($id === '' || !in_array($dec, ['used','skip','keep'], true)) out(['error' => 'bad request']);
    $patch = $dec === 'keep' ? ['kept' => true] : ['state' => $dec === 'used' ? 'used' : 'skipped'];
    if (!empty($body['reason'])) $patch['reason'] = $body['reason'];
    set_overlay('queue', $id, $patch);
    decide(['type'=>'comment','card_id'=>$id,'decision'=>$dec,'reason'=>$body['reason'] ?? null]);
    out(['ok'=>true]);

  case 'photo': // hold | use_friday | mark_used | delete  (id = photo id or shoot id)
    $dec = (string)($body['decision'] ?? ''); $id = (string)($body['id'] ?? '');
    if ($id === '' || !in_array($dec, ['hold','use_friday','mark_used','delete','share','unshare'], true)) out(['error' => 'bad request']);   // share: offered to the other boards (03.11.)
    if ($dec === 'delete' && is_file("$D/uploads/photos/$id") && preg_match('/^[\w.\-]+$/', $id)) unlink("$D/uploads/photos/$id");
    set_overlay('photos', $id, ['state' => $dec]);
    decide(['type'=>'photo','id'=>$id,'decision'=>$dec]);
    out(['ok'=>true]);

  case 'upload': // multipart photos[]
    $saved = []; $failed = [];
    $errs = [1 => 'larger than the server allows', 2 => 'larger than the form allows', 3 => 'only partly uploaded', 4 => 'no file arrived', 6 => 'no temp folder', 7 => 'cannot write to disk', 8 => 'blocked by a PHP extension'];
    if (empty($_FILES['photos']) && empty($_POST)) $failed[] = 'request too large: PHP dropped the whole upload (' . (int)($_SERVER['CONTENT_LENGTH'] ?? 0) . ' bytes); send fewer photos at once';
    if (!empty($_FILES['photos'])) {
      $n = count($_FILES['photos']['name']);
      for ($i = 0; $i < $n; $i++) {
        if ($_FILES['photos']['error'][$i] !== UPLOAD_ERR_OK) { $failed[] = ($_FILES['photos']['name'][$i] ?: '?') . ': ' . ($errs[$_FILES['photos']['error'][$i]] ?? 'error ' . $_FILES['photos']['error'][$i]); continue; }
        $ext = strtolower(pathinfo($_FILES['photos']['name'][$i], PATHINFO_EXTENSION)) ?: 'jpg';
        if (!in_array($ext, ['jpg','jpeg','png','heic','heif','webp'], true)) $ext = 'jpg';
        $name = date('Y-m-d_His') . '_' . substr(bin2hex(random_bytes(3)), 0, 4) . ".$ext";
        if (move_uploaded_file($_FILES['photos']['tmp_name'][$i], "$D/uploads/photos/$name")) $saved[] = $name;
      }
    }
    $note = trim((string)($_POST['note'] ?? '')); $card = preg_replace('/[^\w-]/', '', (string)($_POST['card_id'] ?? ''));
    if (!empty($_POST['share']) && $card === '') $note = '[netzwerk] ' . $note;   // shared for the other boards as soon as the worker has it (photo_index.py)
    if ($card !== '') { $note = "card:$card"; if ($saved) set_overlay('cards', $card, ['image_pending' => time()]); }   // image for one post, not for the pool
    if ($note !== '' && $saved) { $notes = jread("$D/uploads/photo-notes.json", []); foreach ($saved as $s) $notes[$s] = $note; jwrite("$D/uploads/photo-notes.json", $notes); }
    if (!$saved && !$failed) $failed[] = 'no file arrived in the request (the browser sent none: pick the photos again, fewer at once)';
    decide(['type'=>'upload','files'=>$saved,'failed'=>$failed,'note'=>$note,'card_id'=>$card]);
    out(['ok'=>count($saved) > 0,'saved'=>$saved,'failed'=>$failed]);

  case 'memo': // multipart audio
    if (empty($_FILES['audio']) || $_FILES['audio']['error'] !== UPLOAD_ERR_OK) out(['error' => 'no audio']);
    $mime = (string)($_POST['mime'] ?? 'audio/mp4'); $ext = str_contains($mime, 'webm') ? 'webm' : (str_contains($mime, 'ogg') ? 'ogg' : 'm4a');
    $name = date('Y-m-d_His') . ".$ext";
    $txt = trim((string)($_POST['text'] ?? '')); if ($txt !== '') file_put_contents("$D/uploads/memos/$name.note.txt", $txt);
    $card = preg_replace('/[^\w-]/', '', (string)($_POST['card_id'] ?? ''));   // a spoken note for one post: the Mac transcribes it and applies it like a typed note
    if ($card !== '') file_put_contents("$D/uploads/memos/$name.card.txt", $card);   // sidecars first, audio last: a pull in between never separates them
    move_uploaded_file($_FILES['audio']['tmp_name'], "$D/uploads/memos/$name");
    if ($card !== '') { set_overlay('cards', $card, ['note_pending' => time()]); }
    decide(['type'=>'memo','file'=>$name,'seconds'=>(int)($_POST['seconds'] ?? 0),'card_id'=>$card]);
    out(['ok'=>true,'file'=>$name]);

  case 'external': // a post Anton published or scheduled in LinkedIn himself, outside the board: goes into posts-log so Published is complete
    $date = preg_replace('/[^0-9-]/', '', (string)($body['date'] ?? '')); if (strlen($date) !== 10) $date = date('Y-m-d');
    $ch = (($body['channel'] ?? 'personal') === 'company') ? 'company' : 'personal';
    $hook = trim((string)($body['hook'] ?? '')); $hook = function_exists('mb_substr') ? mb_substr($hook, 0, 160) : substr($hook, 0, 160);
    $url = trim((string)($body['url'] ?? '')); if ($url !== '' && !preg_match('~^https://(www\.)?linkedin\.com/~', $url)) out(['error' => 'not a LinkedIn URL']);
    if ($hook === '' && $url === '') out(['error' => 'first line or URL needed']);
    $id = 'li-ext-' . date('Ymd-Hi');
    set_overlay('published', $id, ['date' => $date, 'channel' => $ch, 'hook' => $hook, 'url' => $url]);
    decide(['type' => 'external', 'post_id' => $id, 'date' => $date, 'channel' => $ch, 'hook' => $hook, 'url' => $url]);
    out(['ok' => true, 'id' => $id]);

  case 'metrics': // numbers Anton reads off LinkedIn for one published post (the API cannot read them until LinkedIn grants the analytics scope)
    $id = preg_replace('/[^\w-]/', '', (string)($body['post_id'] ?? '')); if ($id === '') out(['error' => 'bad request']);
    $patch = []; foreach (['impressions', 'reactions', 'comments'] as $k) if (isset($body[$k]) && $body[$k] !== '') $patch[$k] = (string)(int)preg_replace('/\D/', '', (string)$body[$k]);
    if (!$patch) out(['error' => 'no numbers']);
    set_overlay('metrics', $id, $patch); decide(['type' => 'metrics', 'post_id' => $id] + $patch); out(['ok' => true]);

  case 'profile_visits': // S3: weekly sum of profile visits Anton reads off the LinkedIn app; one number per ISO week, no names
    $week = preg_replace('/[^0-9W-]/', '', (string)($body['week'] ?? '')); $v = preg_replace('/\D/', '', (string)($body['visits'] ?? ''));
    if (!preg_match('/^\d{4}-W\d{2}$/', $week) || $v === '') out(['error' => 'week and visits needed']);
    set_overlay('profile', $week, ['visits' => $v]); decide(['type' => 'profile_visits', 'week' => $week, 'visits' => $v]); out(['ok' => true]);

  case 'inbound': // S4: a proposed contact from a lead mail: confirm (becomes an inbound-log row) or drop; nothing is sent anywhere
    $id = preg_replace('/[^\w.@-]/', '', (string)($body['id'] ?? '')); $dec = (($body['decision'] ?? '') === 'confirm') ? 'confirm' : 'drop';
    if ($id === '') out(['error' => 'bad request']);
    $d = ['type' => 'inbound', 'id' => $id, 'decision' => $dec];
    foreach (['date', 'source', 'who', 'what', 'qualified', 'next'] as $k) if (isset($body[$k])) { $s = trim((string)$body[$k]); $d[$k] = function_exists('mb_substr') ? mb_substr($s, 0, 300) : substr($s, 0, 300); }
    set_overlay('inbound', $id, ['state' => $dec]); decide($d); out(['ok' => true]);

  case 'logout': auth_logout(); out(['ok' => true]);

  case 'profile': // onboarding (03.11.): website, own words, optional document -> uploads/profile/request.json; the worker's onboard.py makes the proposal
    if (!auth_user()) out(['error' => 'no owner']);
    $web = trim((string)($_POST['website'] ?? '')); $words = trim((string)($_POST['words'] ?? '')); $li = trim((string)($_POST['linkedin'] ?? ''));
    if ($li !== '' && !preg_match('~^(https?://)?([\w-]+\.)?linkedin\.com/\S+$~i', $li)) out(['error' => 'LinkedIn: bitte den Link zu deinem Profil (linkedin.com/in/...)']);
    if ($web !== '' && !preg_match('~^(https?://)?[\w.-]+\.[a-z]{2,}(/\S*)?$~i', $web)) out(['error' => 'Website: bitte eine Adresse wie firma.de']);
    $doc = '';
    if (!empty($_FILES['doc']) && $_FILES['doc']['error'] === UPLOAD_ERR_OK) {
      $ext = strtolower(pathinfo($_FILES['doc']['name'], PATHINFO_EXTENSION));
      if (!in_array($ext, ['pdf','txt','md','docx'], true)) out(['error' => 'Dokument: PDF oder Text']);
      if ($_FILES['doc']['size'] > 15 * 1048576) out(['error' => 'Dokument größer als 15 MB']);
      $doc = "doc.$ext"; move_uploaded_file($_FILES['doc']['tmp_name'], "$D/uploads/profile/$doc");
    }
    if ($web === '' && $words === '' && $doc === '') out(['error' => 'Website, ein paar Sätze oder ein Dokument: mindestens eins davon']);
    jwrite("$D/uploads/profile/request.json", ['website' => $web, 'linkedin' => $li, 'words' => function_exists('mb_substr') ? mb_substr($words, 0, 4000) : substr($words, 0, 4000), 'doc' => $doc, 'ts' => date('c')]);
    decide(['type' => 'profile', 'decision' => 'request', 'website' => $web, 'doc' => $doc]); out(['ok' => true]);

  case 'profile_confirm': // the person corrected the proposal and said yes: profile.json confirmed here at once, the worker writes facts, positioning and inventory
    if (!auth_user()) out(['error' => 'no owner']);
    $pr = jread("$D/profile.json", []); $d = ['type' => 'profile_confirm'];
    foreach (['role','company','website','audience','offer','goal','tone','facts','words','examples','linkedin'] as $k) if (isset($body[$k])) { $v = trim((string)$body[$k]); $d[$k] = function_exists('mb_substr') ? mb_substr($v, 0, 6000) : substr($v, 0, 6000); $pr[$k] = $d[$k]; }
    foreach (['topics','avoid'] as $k) if (isset($body[$k])) { $t = array_values(array_filter(array_map('trim', is_array($body[$k]) ? $body[$k] : explode("\n", (string)$body[$k])))); $d[$k] = array_slice($t, 0, 20); $pr[$k] = $d[$k]; }
    if (isset($body['style']) && is_array($body['style'])) { $st = []; foreach (['register','length','question'] as $k) $st[$k] = substr((string)($body['style'][$k] ?? ''), 0, 20); $d['style'] = $st; $pr['style'] = $st; }
    if (isset($body['day']) && in_array($body['day'], ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'], true)) { $d['day'] = $body['day']; $pr['day'] = $d['day']; }
    $pr['confirmed'] = true; $pr['confirmed_at'] = date('c'); jwrite("$D/profile.json", $pr); decide($d); out(['ok' => true]);

  case 'invite': // any board invites a person (04.11.): a new board in one of my teams or in a new team; link + start password come back once, the inviter sends them
    $self = boards_self(auth_user()); $name = trim((string)($body['name'] ?? '')); $lang = ($body['lang'] ?? 'de') === 'en' ? 'en' : 'de';
    $team = boards_group_in((string)($body['team'] ?? ''))[0] ?? ''; if ($team === '') out(['error' => 'Team fehlt']);
    $inv = jread("$D/invites.json", []); if (count(array_filter($inv, fn($x) => substr((string)$x['ts'], 0, 10) === date('Y-m-d'))) >= 20) out(['error' => 'heute schon 20 Einladungen, morgen weiter']);
    $r = boards_create($name, $lang, [$team], $self['slug']); if (isset($r['error'])) out(['error' => $r['error']]);
    $reg = boards_registry(); if (isset($reg[$self['slug']]) && !in_array($team, boards_groups($reg[$self['slug']]), true)) { $reg[$self['slug']]['groups'] = array_values(array_unique(array_merge(boards_groups($reg[$self['slug']]), [$team]))); unset($reg[$self['slug']]['group']); boards_save($reg); }   // a new team: I am in it too
    $inv[] = ['ts' => date('c'), 'name' => $name, 'slug' => $r['slug'], 'team' => $team, 'token' => $r['token']]; jwrite("$D/invites.json", $inv);
    decide(['type' => 'invite', 'name' => $name, 'slug' => $r['slug'], 'team' => $team]);
    $first = explode(' ', $name)[0]; $my = explode(' ', $self['name'])[0];
    $text = "Hallo $first, hier ist dein Board: {$r['url']}\nStartpasswort: {$r['pw']}\nBeim ersten Öffnen wählst du dein eigenes Passwort. Dann Website eintragen, drei Sätze zu dir, fertig. Der erste Entwurf kommt von selbst, nichts geht ohne dich raus.\nGrüße, $my";
    out(['ok' => true, 'url' => $r['url'], 'pw' => $r['pw'], 'slug' => $r['slug'], 'team' => $team, 'text' => $text]);

  case 'team': // join a new or existing team, or leave one (04.11.); the worker carries it into config.yaml within 10 minutes
    $self = boards_self(auth_user()); $team = boards_group_in((string)($body['team'] ?? ''))[0] ?? ''; if ($team === '') out(['error' => 'Teamname: Kleinbuchstaben, Ziffern, Bindestrich']);
    $reg = boards_registry(); if (!isset($reg[$self['slug']])) out(['error' => 'Board nicht registriert']); $g = boards_groups($reg[$self['slug']]);
    if (($body['do'] ?? 'join') === 'leave') { $g = array_values(array_diff($g, [$team])); if (!$g) out(['error' => 'das letzte Team bleibt']); } else $g = array_values(array_unique(array_merge($g, [$team])));
    $reg[$self['slug']]['groups'] = $g; unset($reg[$self['slug']]['group']); boards_save($reg); decide(['type' => 'team', 'do' => $body['do'] ?? 'join', 'team' => $team]); out(['ok' => true, 'groups' => $g]);

  case 'profile_save': // Mein Profil (04.11.): facts, topics, never-topics, tone, examples, sharing default; profile.json here at once, the worker writes facts and positioning (apply_decisions.py)
    if (!auth_user()) out(['error' => 'no owner']);
    $pr = jread("$D/profile.json", []); $d = ['type' => 'profile_save']; $cut = fn($v, $n) => function_exists('mb_substr') ? mb_substr($v, 0, $n) : substr($v, 0, $n);
    foreach (['role','company','website','audience','offer','goal','tone','facts','words','examples','linkedin'] as $k) if (isset($body[$k])) { $d[$k] = $cut(trim((string)$body[$k]), 8000); $pr[$k] = $d[$k]; }
    if (isset($body['day']) && in_array($body['day'], ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'], true)) { $d['day'] = $body['day']; $pr['day'] = $d['day']; }
    foreach (['topics','avoid'] as $k) if (isset($body[$k])) { $t = array_values(array_filter(array_map(fn($x) => $cut(trim((string)$x), 160), is_array($body[$k]) ? $body[$k] : explode("\n", (string)$body[$k])))); $d[$k] = array_slice($t, 0, 20); $pr[$k] = $d[$k]; }
    if (isset($body['style']) && is_array($body['style'])) { $st = []; foreach (['register','length','question'] as $k) $st[$k] = $cut((string)($body['style'][$k] ?? ''), 20); $d['style'] = $st; $pr['style'] = $st; }
    if (isset($body['share_default'])) { $d['share_default'] = (bool)$body['share_default']; $pr['share_default'] = $d['share_default']; }
    $pr['saved_at'] = date('c'); jwrite("$D/profile.json", $pr); decide($d); out(['ok' => true]);

  case 'proposal': // a shared photo offered on a card: accept | decline (apply_decisions.py puts it on the card with a credit line)
    $id = preg_replace('/[^\w#-]/', '', (string)($body['card_id'] ?? '')); $dec = ($body['decision'] ?? '') === 'accept' ? 'accept' : 'decline';   // card id, or card id + "#t" for a text proposal (04.11.)
    $props = jread("$D/proposals.json", []); if ($id === '' || empty($props[$id])) out(['error' => 'unknown proposal']);
    set_overlay('proposals', $id, ['state' => $dec]); decide(['type' => 'proposal', 'card_id' => $id, 'decision' => $dec, 'kind' => $props[$id]['kind'] ?? 'photo', 'photo' => $props[$id]['photo'] ?? '', 'owner' => $props[$id]['owner'] ?? '']); out(['ok' => true]);

  case 'memo_share': // a voice memo offered to the other boards (04.11.): share | unshare; apply_decisions.py writes memos/index.csv, match.py reads it
    $dec = ($body['decision'] ?? '') === 'share' ? 'share' : 'unshare'; $id = (string)($body['id'] ?? ''); if ($id === '' || !preg_match('/^[\w.\-]+$/', $id)) out(['error' => 'bad request']);
    set_overlay('memos', $id, ['share' => $dec === 'share' ? 'network' : '']); decide(['type' => 'memo_share', 'id' => $id, 'decision' => $dec]); out(['ok' => true]);

  case 'password': // the person changes their own password (auth.php); ends all other sessions of this board
    $r = auth_set_password((string)($body['new'] ?? '')); if ($r !== '') out(['error' => $r]); auth_login((string)$body['new']); out(['ok' => true]);

  case 'settings':
    $s = settings(); foreach (['expiry','review'] as $k) if (isset($body[$k])) $s[$k] = (string)$body[$k];
    jwrite("$D/settings.json", $s); decide(['type'=>'settings'] + $s); out(['ok'=>true,'settings'=>$s]);

  case 'answer': // weekly question / monthly decision cards
    $id = (string)($body['id'] ?? ''); $ans = (string)($body['answer'] ?? '');
    set_overlay('messages', $id, ['answer' => $ans]); decide(['type'=>'answer','id'=>$id,'answer'=>$ans]); out(['ok'=>true]);

  default: out(['error' => 'unknown action']);
}
