<?php
// Login for a board (03.11.2026). data/auth.json = {slug, name, lang, hash, must_change, disabled}: this board belongs to one
// person and needs their password. No auth.json = an open board behind its secret link (Anton's, as before).
// A session is a random token in data/sessions.json (30 days) carried by an HttpOnly, Secure, SameSite cookie; nothing in localStorage.
// Five wrong passwords from one address lock the login for 15 minutes (data/.logins.json).
declare(strict_types=1);
function auth_dir(): string { return __DIR__ . '/data'; }
function auth_jr(string $f, $d) { $x = is_file($f) ? json_decode((string)file_get_contents($f), true) : null; return $x ?? $d; }
function auth_jw(string $f, $v): void { @mkdir(dirname($f), 0755, true); file_put_contents($f, json_encode($v, JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES), LOCK_EX); }
function auth_user(): ?array { $u = auth_jr(auth_dir() . '/auth.json', null); return is_array($u) && !empty($u['hash']) ? $u : null; }
function auth_cookie(): string { return 'b_' . substr(md5(__DIR__), 0, 10); }
function auth_sessions(): array { $s = auth_jr(auth_dir() . '/sessions.json', []); $now = time(); return array_filter($s, fn($x) => (int)($x['exp'] ?? 0) > $now); }
function auth_check(): bool {
  if (!auth_user()) return true;                                   // open board
  $t = $_COOKIE[auth_cookie()] ?? ''; if ($t === '' || !preg_match('/^[a-f0-9]{48}$/', $t)) return false;
  $s = auth_sessions(); return isset($s[$t]);
}
function auth_ip(): string { return (string)($_SERVER['REMOTE_ADDR'] ?? '0'); }
function auth_locked(): int {   // seconds left in a lock, 0 = free
  $l = auth_jr(auth_dir() . '/.logins.json', []); $e = $l[auth_ip()] ?? null;
  return ($e && (int)($e['fails'] ?? 0) >= 5 && time() - (int)$e['last'] < 900) ? 900 - (time() - (int)$e['last']) : 0;
}
function auth_fail(): void { $f = auth_dir() . '/.logins.json'; $l = auth_jr($f, []); $e = $l[auth_ip()] ?? ['fails' => 0]; if (time() - (int)($e['last'] ?? 0) > 900) $e['fails'] = 0; $e['fails']++; $e['last'] = time(); $l[auth_ip()] = $e; auth_jw($f, $l); }
function auth_login(string $pw): bool {
  $u = auth_user(); if (!$u || !empty($u['disabled']) || auth_locked()) return false;
  if (!password_verify($pw, $u['hash'])) { auth_fail(); return false; }
  $l = auth_jr(auth_dir() . '/.logins.json', []); unset($l[auth_ip()]); auth_jw(auth_dir() . '/.logins.json', $l);
  $t = bin2hex(random_bytes(24)); $s = auth_sessions(); $s[$t] = ['exp' => time() + 30 * 86400, 'ua' => substr((string)($_SERVER['HTTP_USER_AGENT'] ?? ''), 0, 80), 'at' => date('c')];
  auth_jw(auth_dir() . '/sessions.json', $s);
  setcookie(auth_cookie(), $t, ['expires' => time() + 30 * 86400, 'path' => dirname($_SERVER['SCRIPT_NAME'] ?? '/') . '/', 'secure' => !empty($_SERVER['HTTPS']), 'httponly' => true, 'samesite' => 'Lax']);
  return true;
}
function auth_logout(): void {
  $t = $_COOKIE[auth_cookie()] ?? ''; $s = auth_sessions(); unset($s[$t]); auth_jw(auth_dir() . '/sessions.json', $s);
  setcookie(auth_cookie(), '', ['expires' => 1, 'path' => dirname($_SERVER['SCRIPT_NAME'] ?? '/') . '/', 'secure' => !empty($_SERVER['HTTPS']), 'httponly' => true, 'samesite' => 'Lax']);
}
function auth_set_password(string $new): string {   // '' = ok, else the reason
  if (strlen($new) < 10) return 'mindestens 10 Zeichen';
  $u = auth_user(); if (!$u) return 'kein Konto'; $u['hash'] = password_hash($new, PASSWORD_DEFAULT); $u['must_change'] = false; $u['changed'] = date('c');
  auth_jw(auth_dir() . '/auth.json', $u); auth_jw(auth_dir() . '/sessions.json', []); return '';
}
function auth_page(string $title, string $body): never {   // small German pages for login and password change, same look as the board
  header('Cache-Control: no-store'); header('X-Robots-Tag: noindex, nofollow');
  echo '<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>', htmlspecialchars($title), '</title>',
       '<style>body{margin:0;background:#f4f6f8;color:#1f2d3a;font:16px/1.45 -apple-system,"Helvetica Neue",Arial,sans-serif}.w{max-width:420px;margin:12vh auto;padding:0 18px}h1{font-size:22px;color:#0f3a50;margin:0 0 6px}p{color:#5a6b7a;margin:0 0 16px}',
       'input{width:100%;box-sizing:border-box;border:1px solid #d6e2ea;border-radius:8px;padding:12px;font:inherit;font-size:16px;margin:0 0 10px;background:#fff}button{width:100%;border:0;background:#20B8D0;color:#fff;border-radius:8px;padding:13px;font:inherit;font-size:16px;font-weight:600;cursor:pointer}.e{background:#fff4e0;border:1px solid #f3d9a4;color:#7a4b00;border-radius:8px;padding:10px 12px;margin:0 0 12px;font-size:14px}.bar{height:3px;background:linear-gradient(90deg,#42F45D,#01BC56,#00BEE6,#08E3FB);margin:0 0 18px;border-radius:2px}</style></head><body><div class="w"><div class="bar"></div>', $body, '</div></body></html>';
  exit;
}
function auth_gate(): void {   // called by index.php: shows login or password change and stops, or returns when the person may see the board
  $u = auth_user(); if (!$u) return;
  $err = '';
  if (($_POST['do'] ?? '') === 'login') { if (auth_login((string)($_POST['pw'] ?? ''))) { header('Location: ' . strtok($_SERVER['REQUEST_URI'], '?')); exit; } $err = auth_locked() ? 'Zu viele Versuche, bitte in 15 Minuten noch einmal.' : 'Das Passwort stimmt nicht.'; }
  if (!auth_check()) {
    $name = htmlspecialchars($u['name'] ?? ''); $e = $err ? "<div class=\"e\">$err</div>" : '';
    auth_page('Board', "<h1>Dein Board</h1><p>$name, bitte melde dich an.</p>$e<form method=\"post\"><input type=\"hidden\" name=\"do\" value=\"login\"><input type=\"password\" name=\"pw\" placeholder=\"Passwort\" autofocus autocomplete=\"current-password\"><button>Anmelden</button></form>");
  }
  if (($_POST['do'] ?? '') === 'password') {
    $r = ($_POST['pw1'] ?? '') !== ($_POST['pw2'] ?? '') ? 'die beiden Eingaben sind verschieden' : auth_set_password((string)($_POST['pw1'] ?? ''));
    if ($r === '') { auth_login((string)$_POST['pw1']); header('Location: ' . strtok($_SERVER['REQUEST_URI'], '?')); exit; } $err = ucfirst($r) . '.';
  }
  if (!empty($u['must_change'])) {
    $e = $err ? "<div class=\"e\">$err</div>" : '';
    auth_page('Passwort', "<h1>Neues Passwort</h1><p>Das erste Passwort war nur für den Start. Wähle jetzt dein eigenes, mindestens 10 Zeichen.</p>$e<form method=\"post\"><input type=\"hidden\" name=\"do\" value=\"password\"><input type=\"password\" name=\"pw1\" placeholder=\"Neues Passwort\" autocomplete=\"new-password\" autofocus><input type=\"password\" name=\"pw2\" placeholder=\"Noch einmal\" autocomplete=\"new-password\"><button>Speichern</button></form>");
  }
}
