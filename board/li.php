<?php
// LinkedIn OAuth callback for every board (05.11.2026), one registered redirect URL: https://alpitype.de/board/li.php
// api.php (li_start) sent the person to LinkedIn with state = <board token>.<nonce>. The code lands in that board's
// data/uploads/profile/li-code.json; the worker (pipeline/linkedin_connect.py) exchanges it with the app secret, which never
// sits on this host, and writes users/<slug>/linkedin.json. Then the board shows "verbunden als …" and posts itself.
declare(strict_types=1);
require __DIR__ . '/boards.php';
function li_page(string $h1, string $p, string $back = ''): never {
  header('Cache-Control: no-store'); header('X-Robots-Tag: noindex, nofollow');
  echo '<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>LinkedIn</title>',
       '<style>body{margin:0;background:#f4f6f8;color:#1f2d3a;font:16px/1.45 -apple-system,"Helvetica Neue",Arial,sans-serif}.w{max-width:420px;margin:12vh auto;padding:0 18px}h1{font-size:22px;color:#0f3a50;margin:0 0 6px}p{color:#5a6b7a;margin:0 0 16px}a{display:block;text-align:center;background:#20B8D0;color:#fff;border-radius:8px;padding:13px;font-weight:600;text-decoration:none}.bar{height:3px;background:linear-gradient(90deg,#42F45D,#01BC56,#00BEE6,#08E3FB);margin:0 0 18px;border-radius:2px}</style></head><body><div class="w"><div class="bar"></div><h1>',
       htmlspecialchars($h1), '</h1><p>', htmlspecialchars($p), '</p>', $back !== '' ? '<a href="' . htmlspecialchars($back) . '">Zurück zum Board</a>' : '', '</div></body></html>';
  exit;
}
$state = (string)($_GET['state'] ?? ''); [$token, $nonce] = array_pad(explode('.', $state, 2), 2, '');
if (!preg_match('/^[A-Za-z0-9]{20,40}$/', $token) || !is_dir(__DIR__ . "/$token/data")) { http_response_code(400); li_page('Unbekanntes Board', 'Dieser Link gehört zu keinem Board.'); }
$D = __DIR__ . "/$token/data"; $back = boards_url() . $token . '/#profile';
$lf = "$D/li-state.json"; $ls = is_file($lf) ? (json_decode((string)file_get_contents($lf), true) ?? []) : [];
if (($ls['nonce'] ?? '') === '' || $nonce === '' || !hash_equals((string)$ls['nonce'], $nonce) || time() - (int)($ls['ts'] ?? 0) > 1800) li_page('Abgelaufen', 'Die Anfrage ist abgelaufen. Bitte im Board noch einmal auf „Mit LinkedIn verbinden“ tippen.', $back);
unset($ls['nonce']); $ls['done'] = time();
if (isset($_GET['error']) || empty($_GET['code'])) {
  $ls['error'] = substr((string)($_GET['error_description'] ?? $_GET['error'] ?? 'kein Code'), 0, 200); file_put_contents($lf, json_encode($ls), LOCK_EX);
  li_page('Nicht verbunden', 'LinkedIn hat die Verbindung nicht freigegeben: ' . $ls['error'], $back);
}
@mkdir("$D/uploads/profile", 0755, true);
file_put_contents("$D/uploads/profile/li-code.json", json_encode(['code' => (string)$_GET['code'], 'ts' => date('c'), 'redirect' => boards_url() . 'li.php']), LOCK_EX);
unset($ls['error']); file_put_contents($lf, json_encode($ls), LOCK_EX);
header('Location: ' . $back); exit;
