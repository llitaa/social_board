<?php
// Board API. State lives in data/. Decisions are appended as JSONL and pulled by the Mac.
declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
date_default_timezone_set('Europe/Berlin');
$D = __DIR__ . '/data';
foreach (['decisions','uploads/photos','uploads/memos','queue','img'] as $p) { if (!is_dir("$D/$p")) mkdir("$D/$p", 0755, true); }

function jread(string $f, $def) { return is_file($f) ? (json_decode((string)file_get_contents($f), true) ?? $def) : $def; }
function jwrite(string $f, $v): void { file_put_contents($f, json_encode($v, JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES), LOCK_EX); }
function decide(array $d): void {
  global $D; $d['ts'] = date('c');
  file_put_contents("$D/decisions/" . date('Y-m-d') . ".jsonl", json_encode($d, JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES) . "\n", FILE_APPEND|LOCK_EX);
}
function out($v): never { echo json_encode($v, JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES); exit; }
function settings(): array { global $D; return array_merge(['expiry' => '18:00', 'review' => 'Sat 08:00'], jread("$D/settings.json", [])); }

// Apply local overlays (decisions taken since the last Mac push) so the UI reflects them immediately.
function overlay_cards(array $cards): array {
  global $D; $ov = jread("$D/overlay.json", []);
  foreach ($cards as &$c) { if (isset($ov['cards'][$c['id']])) $c = array_merge($c, $ov['cards'][$c['id']]); }
  return $cards;
}
function set_overlay(string $kind, string $id, array $patch): void {
  global $D; $ov = jread("$D/overlay.json", []); $ov[$kind][$id] = array_merge($ov[$kind][$id] ?? [], $patch); jwrite("$D/overlay.json", $ov);
}
function today_queue(): array {
  global $D; $s = settings(); $today = date('Y-m-d'); $f = "$D/queue/$today.json";
  $q = jread($f, ['date' => $today, 'cards' => []]);
  $ov = jread("$D/overlay.json", []);
  $now = time(); [$eh, $em] = array_map('intval', explode(':', $s['expiry'])); $exp = mktime($eh, $em, 0);
  $out = [];
  foreach ($q['cards'] as $c) {
    $st = $ov['queue'][$c['id']] ?? [];
    $c = array_merge($c, $st);
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
  case 'state':
    $cards = overlay_cards(jread("$D/cards.json", []));
    $photos = jread("$D/photos.json", ['shoots' => []]);
    $pending = [];
    foreach (glob("$D/uploads/photos/*") as $f) { $pending[] = ['id' => basename($f), 'url' => 'data/uploads/photos/' . rawurlencode(basename($f)), 'ts' => date('c', filemtime($f))]; }
    $memos = [];
    foreach (glob("$D/uploads/memos/*") as $f) { $memos[] = ['id' => basename($f), 'ts' => date('c', filemtime($f)), 'bytes' => filesize($f)]; }
    $msg = jread("$D/messages.json", []);
    out(['cards' => $cards, 'queue' => today_queue(), 'photos' => $photos, 'pending' => $pending, 'memos' => $memos, 'settings' => settings(), 'messages' => $msg, 'now' => date('c')]);

  case 'decide': // post card: post | change | skip | posted
    $id = (string)($body['card_id'] ?? ''); $dec = (string)($body['decision'] ?? '');
    if ($id === '' || !in_array($dec, ['post','change','skip','posted'], true)) out(['error' => 'bad request']);
    $patch = ['status' => ['post'=>'approved','change'=>'change','skip'=>'skipped','posted'=>'posted'][$dec], 'decided' => date('c')];
    foreach (['option','image_id','note','reason','url'] as $k) if (isset($body[$k]) && $body[$k] !== '') $patch[$k] = $body[$k];
    set_overlay('cards', $id, $patch);
    decide(['type'=>'post','card_id'=>$id,'decision'=>$dec] + array_intersect_key($patch, array_flip(['option','image_id','note','reason','url'])));
    out(['ok' => true, 'status' => $patch['status']]);

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

  case 'photo': // use_friday | mark_used | delete  (id = photo id or shoot id)
    $dec = (string)($body['decision'] ?? ''); $id = (string)($body['id'] ?? '');
    if ($id === '' || !in_array($dec, ['use_friday','mark_used','delete'], true)) out(['error' => 'bad request']);
    if ($dec === 'delete' && is_file("$D/uploads/photos/$id") && preg_match('/^[\w.\-]+$/', $id)) unlink("$D/uploads/photos/$id");
    set_overlay('photos', $id, ['state' => $dec]);
    decide(['type'=>'photo','id'=>$id,'decision'=>$dec]);
    out(['ok'=>true]);

  case 'upload': // multipart photos[]
    $saved = [];
    if (!empty($_FILES['photos'])) {
      $n = count($_FILES['photos']['name']);
      for ($i = 0; $i < $n; $i++) {
        if ($_FILES['photos']['error'][$i] !== UPLOAD_ERR_OK) continue;
        $ext = strtolower(pathinfo($_FILES['photos']['name'][$i], PATHINFO_EXTENSION)) ?: 'jpg';
        if (!in_array($ext, ['jpg','jpeg','png','heic','heif','webp'], true)) $ext = 'jpg';
        $name = date('Y-m-d_His') . '_' . substr(bin2hex(random_bytes(3)), 0, 4) . ".$ext";
        if (move_uploaded_file($_FILES['photos']['tmp_name'][$i], "$D/uploads/photos/$name")) $saved[] = $name;
      }
    }
    $note = trim((string)($_POST['note'] ?? ''));
    if ($note !== '' && $saved) { $notes = jread("$D/uploads/photo-notes.json", []); foreach ($saved as $s) $notes[$s] = $note; jwrite("$D/uploads/photo-notes.json", $notes); }
    decide(['type'=>'upload','files'=>$saved,'note'=>$note]);
    out(['ok'=>true,'saved'=>$saved]);

  case 'memo': // multipart audio
    if (empty($_FILES['audio']) || $_FILES['audio']['error'] !== UPLOAD_ERR_OK) out(['error' => 'no audio']);
    $mime = (string)($_POST['mime'] ?? 'audio/mp4'); $ext = str_contains($mime, 'webm') ? 'webm' : (str_contains($mime, 'ogg') ? 'ogg' : 'm4a');
    $name = date('Y-m-d_His') . ".$ext";
    move_uploaded_file($_FILES['audio']['tmp_name'], "$D/uploads/memos/$name");
    $txt = trim((string)($_POST['text'] ?? '')); if ($txt !== '') file_put_contents("$D/uploads/memos/$name.note.txt", $txt);
    decide(['type'=>'memo','file'=>$name,'seconds'=>(int)($_POST['seconds'] ?? 0)]);
    out(['ok'=>true,'file'=>$name]);

  case 'settings':
    $s = settings(); foreach (['expiry','review'] as $k) if (isset($body[$k])) $s[$k] = (string)$body[$k];
    jwrite("$D/settings.json", $s); decide(['type'=>'settings'] + $s); out(['ok'=>true,'settings'=>$s]);

  case 'answer': // weekly question / monthly decision cards
    $id = (string)($body['id'] ?? ''); $ans = (string)($body['answer'] ?? '');
    set_overlay('messages', $id, ['answer' => $ans]); decide(['type'=>'answer','id'=>$id,'answer'=>$ans]); out(['ok'=>true]);

  default: out(['error' => 'unknown action']);
}
