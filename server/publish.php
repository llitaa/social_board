<?php
// Server-side publisher (21.10.2026): the always-on host posts approved cards at their slot, so publishing no longer
// depends on the Mac being awake, online or unstuck. Runs from the Hostinger cron (every 5 min), from api.php?a=tick
// (the board page and the Mac's watch loop call it every minute) or by hand: php publish.php [--dry].
// Needs: ~/board-worker/linkedin.json (token, pushed by the Mac's board_sync push; never inside public_html),
// the board's data dir (cards.json, overlay.json, img/<id>-final.jpg). Writes: overlay (status posted + url, or publish_error),
// a decision line the Mac folds into the CSVs, published.json as its own memory, publish.log.
declare(strict_types=1);
date_default_timezone_set('Europe/Berlin');   // the host runs UTC; slots are Berlin time (found in the 21.10. review: the cron would have posted two hours late)
$W = __DIR__; $DATA = getenv('BOARD_DATA') ?: glob($_SERVER['HOME'] . '/domains/alpitype.de/public_html/board/*/data')[0] ?? '';
$DRY = in_array('--dry', $argv ?? [], true);
function L(string $m): void { global $W, $DRY; $l = date('Y-m-d H:i:s') . ($DRY ? ' [dry] ' : ' ') . $m; echo $l, "\n"; if (!$DRY) file_put_contents("$W/publish.log", $l . "\n", FILE_APPEND); }
function jr(string $p, $d) { $x = is_file($p) ? json_decode((string)file_get_contents($p), true) : null; return $x ?? $d; }
function jw(string $p, $v): void { file_put_contents($p, json_encode($v, JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES), LOCK_EX); }
function version(): string { return date('Ym', strtotime('first day of -2 months')); }   // LinkedIn keeps a version ~12 months; two months back is always live
function li(array $c, string $method, string $url, $body = null, ?string $raw = null, string $ctype = 'application/json'): array {
  $ch = curl_init(strpos($url, 'http') === 0 ? $url : 'https://api.linkedin.com/rest' . $url);
  $h = ['Authorization: Bearer ' . $c['access_token'], 'LinkedIn-Version: ' . version(), 'X-Restli-Protocol-Version: 2.0.0', 'Content-Type: ' . $ctype];
  curl_setopt_array($ch, [CURLOPT_CUSTOMREQUEST => $method, CURLOPT_RETURNTRANSFER => true, CURLOPT_HEADER => true, CURLOPT_HTTPHEADER => $h, CURLOPT_TIMEOUT => 60]);
  if ($raw !== null) curl_setopt($ch, CURLOPT_POSTFIELDS, $raw); elseif ($body !== null) curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($body, JSON_UNESCAPED_UNICODE));
  $r = curl_exec($ch); $st = (int)curl_getinfo($ch, CURLINFO_RESPONSE_CODE); $hs = (int)curl_getinfo($ch, CURLINFO_HEADER_SIZE); $err = curl_error($ch); curl_close($ch);
  if ($r === false) throw new RuntimeException("curl: $err");
  $head = substr($r, 0, $hs); $bodyS = substr($r, $hs); $id = preg_match('/x-restli-id:\s*(\S+)/i', $head, $m) ? trim($m[1]) : '';
  if ($st >= 300) throw new RuntimeException("HTTP $st " . substr(trim($bodyS), 0, 200));
  return [$st, $id, $bodyS];
}
function publish_one(array $c, string $author, string $text, ?string $img): string {
  $body = ['author' => $author, 'commentary' => $text, 'visibility' => 'PUBLIC', 'distribution' => ['feedDistribution' => 'MAIN_FEED', 'targetEntities' => [], 'thirdPartyDistributionChannels' => []],
           'lifecycleState' => 'PUBLISHED', 'isReshareDisabledByAuthor' => false];
  if ($img) { [, , $b] = li($c, 'POST', '/images?action=initializeUpload', ['initializeUploadRequest' => ['owner' => $author]]); $v = json_decode($b, true)['value'];
    li($c, 'PUT', $v['uploadUrl'], null, (string)file_get_contents($img), 'application/octet-stream'); $body['content'] = ['media' => ['id' => $v['image'], 'altText' => '']]; }
  [, $urn] = li($c, 'POST', '/posts', $body); return $urn;
}
function ov_patch(string $id, array $patch): void {   // overlay read-modify-write under the same lock api.php uses
  global $DATA; $lk = fopen("$DATA/.overlay.lock", 'c'); flock($lk, LOCK_EX); $ov = jr("$DATA/overlay.json", []); $cur = $ov['cards'][$id] ?? [];
  foreach ($patch as $k => $v) { if ($v === null) unset($cur[$k]); else $cur[$k] = $v; }
  $ov['cards'][$id] = $cur + ['ts' => date('c')]; $ov['cards'][$id]['ts'] = date('c'); jw("$DATA/overlay.json", $ov); flock($lk, LOCK_UN); fclose($lk);
}
function run(): array {
  global $W, $DATA, $DRY; $out = ['checked' => 0, 'published' => [], 'failed' => []];
  if (!$DATA || !is_dir($DATA)) { L("no board data dir"); return $out; }
  $lock = "$W/.lock"; if (!$DRY && !@mkdir($lock)) { if (filemtime($lock) > time() - 600) return $out; @rmdir($lock); @mkdir($lock); }
  try {
    $me = jr("$W/linkedin.json", []); $org = jr("$W/linkedin-org.json", []); $done = jr("$W/published.json", []);
    $ov = jr("$DATA/overlay.json", []); $cards = jr("$DATA/cards.json", []); $now = date('Y-m-d\TH:i');
    $until = jr("$DATA/applied.json", [])['until'] ?? '';   // overlay entries older than the Mac's last fold are already in cards.json (same rule as the page)
    foreach ($cards as $c) {
      $id = $c['id']; $o = $ov['cards'][$id] ?? []; if ($until && !empty($o['ts']) && strtotime($o['ts']) <= strtotime($until)) $o = [];
      $st = $o['status'] ?? $c['status']; $slot = $o['slot'] ?? $c['slot'];
      if ($st !== 'approved' || isset($done[$id]) || substr((string)$slot, 0, 16) > $now) continue;
      $out['checked']++;
      $pend = max((int)($o['image_pending'] ?? 0), (int)($o['note_pending'] ?? 0));   // a change the Mac is applying: wait, but never longer than 10 minutes
      if ($pend && time() - $pend < 600) { L("$id: image or note still pending, wait"); continue; }
      $fails = (int)($o['publish_fails'] ?? 0); if ($fails >= 5) continue;   // after five failures the card says "needs you"; no retry storm
      $creds = $c['channel'] === 'company' ? $org : $me; $author = $c['channel'] === 'company' ? ($org['org_urn'] ?? '') : ($me['person_urn'] ?? '');
      if (empty($creds['access_token']) || !$author) { L("$id: no token for {$c['channel']} on the server"); continue; }
      if (!empty($creds['expires']) && $creds['expires'] < date('c')) { L("$id: token expired"); ov_patch($id, ['publish_error' => 'LinkedIn token expired: run pipeline/linkedin_auth.py on the Mac']); continue; }
      if (!empty($done[$id . '.attempt']) && time() - (int)$done[$id . '.attempt'] < 600) { L("$id: an attempt is still open, wait"); continue; }   // a lost answer must not post twice
      $done[$id . '.attempt'] = time(); jw("$W/published.json", $done);
      $text = trim((string)($o['text'] ?? $c['text'])); $img = is_file("$DATA/img/$id-final.jpg") ? "$DATA/img/$id-final.jpg" : null;
      if ($DRY) { L("would publish $id ({$c['channel']}, slot $slot, " . strlen($text) . " chars, image " . ($img ? 'yes' : 'no') . ")"); continue; }
      try {
        $urn = publish_one($creds, $author, $text, $img); $url = $urn ? "https://www.linkedin.com/feed/update/$urn/" : '';
        $done[$id] = ['ts' => date('c'), 'urn' => $urn, 'url' => $url]; unset($done[$id . '.attempt']); jw("$W/published.json", $done);
        ov_patch($id, ['status' => 'posted', 'url' => $url, 'published_by' => 'server', 'publish_error' => null, 'publish_fails' => null]);
        $d = ['type' => 'post', 'card_id' => $id, 'decision' => 'posted', 'url' => $url, 'via' => 'server', 'ts' => date('c')];
        file_put_contents("$DATA/decisions/" . date('Y-m-d') . ".jsonl", json_encode($d, JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES) . "\n", FILE_APPEND|LOCK_EX);
        L("published $id -> $url"); $out['published'][] = $id;
      } catch (Throwable $e) {
        unset($done[$id . '.attempt']); jw("$W/published.json", $done);
        ov_patch($id, ['publish_error' => substr($e->getMessage(), 0, 160) . ($fails + 1 >= 5 ? ' · five failures, needs you' : ''), 'publish_fails' => $fails + 1]);
        L("FAILED $id: " . $e->getMessage()); $out['failed'][] = $id;
      }
    }
  } finally { if (!$DRY) @rmdir($lock); }
  return $out;
}
if (PHP_SAPI === 'cli' && realpath($argv[0] ?? '') === __FILE__) { $r = run(); if (!$r['checked'] && $DRY) L("nothing due"); }
