<?php
// Board admin (03.11.2026): creates a board for a person, resets a password, disables a board. One admin password,
// hash in ~/board-worker/admin.json (set with `python3 pipeline/users.py admin`). The code for a new board is copied from
// ~/board-worker/code/ (pushed by users.py sync); the registry is ~/board-worker/users.json (read by the worker's users.py sync).
declare(strict_types=1); date_default_timezone_set('Europe/Berlin');
header('Cache-Control: no-store'); header('X-Robots-Tag: noindex, nofollow');
$HOME = $_SERVER['HOME'] ?? (getenv('HOME') ?: dirname(__DIR__, 5));   // web PHP has no HOME: public_html/board/admin is five levels below it
$W = "$HOME/board-worker"; $BOARD = dirname(__DIR__);
$URL = 'https://' . ($_SERVER['HTTP_HOST'] ?? 'alpitype.de') . rtrim(dirname(dirname($_SERVER['SCRIPT_NAME'])), '/') . '/';
function jr(string $f, $d) { $x = is_file($f) ? json_decode((string)file_get_contents($f), true) : null; return $x ?? $d; }
function jw(string $f, $v): void { file_put_contents($f, json_encode($v, JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES), LOCK_EX); @chmod($f, 0600); }
function h(string $s): string { return htmlspecialchars($s, ENT_QUOTES); }
function page(string $body): never {
  echo '<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Board Admin</title>',
       '<style>body{margin:0;background:#f4f6f8;color:#1f2d3a;font:15px/1.45 -apple-system,"Helvetica Neue",Arial,sans-serif}.w{max-width:760px;margin:30px auto;padding:0 18px}h1{font-size:22px;color:#0f3a50;margin:0 0 6px}h2{font-size:16px;color:#0f3a50;margin:24px 0 8px}p{color:#5a6b7a;margin:0 0 12px}',
       'input,select{box-sizing:border-box;border:1px solid #d6e2ea;border-radius:8px;padding:10px;font:inherit;background:#fff;margin:0 6px 8px 0}button{border:0;background:#20B8D0;color:#fff;border-radius:8px;padding:10px 14px;font:inherit;font-weight:600;cursor:pointer}button.s{background:#fff;color:#0f3a50;border:1px solid #d6e2ea}',
       'table{border-collapse:collapse;width:100%;background:#fff;border-radius:8px;overflow:hidden}td,th{padding:8px 10px;border-bottom:1px solid #d6e2ea;text-align:left;font-size:14px;vertical-align:top}th{color:#5a6b7a;font-weight:600}.ok{background:#e6f9ee;border:1px solid #9fdfb8;border-radius:8px;padding:12px;margin:0 0 14px}.ok code{display:block;font-size:15px;margin:4px 0}.e{background:#fff4e0;border:1px solid #f3d9a4;color:#7a4b00;border-radius:8px;padding:10px 12px;margin:0 0 12px}.bar{height:3px;background:linear-gradient(90deg,#42F45D,#01BC56,#00BEE6,#08E3FB);margin:0 0 18px;border-radius:2px}a{color:#1a8aa0}</style></head><body><div class="w"><div class="bar">', '</div>', $body, '</div></body></html>'; exit;
}
// --- admin login (own cookie, 12 hours)
$adm = jr("$W/admin.json", []); if (empty($adm['hash'])) page('<h1>Board Admin</h1><div class="e">Kein Admin-Passwort gesetzt. Auf dem Mac: <code>python3 pipeline/users.py admin</code></div>');
$sf = "$W/admin-sessions.json"; $sess = array_filter(jr($sf, []), fn($x) => (int)$x > time()); $ck = 'badmin';
if (($_POST['do'] ?? '') === 'logout') { unset($sess[$_COOKIE[$ck] ?? '']); jw($sf, $sess); setcookie($ck, '', ['expires' => 1, 'path' => dirname($_SERVER['SCRIPT_NAME']) . '/']); header('Location: ./'); exit; }
if (($_POST['do'] ?? '') === 'login') {
  $lf = "$W/admin-fails.json"; $l = jr($lf, []); $ip = $_SERVER['REMOTE_ADDR'] ?? '0'; $e = $l[$ip] ?? ['fails' => 0, 'last' => 0];
  if ($e['fails'] >= 5 && time() - $e['last'] < 900) page('<h1>Board Admin</h1><div class="e">Zu viele Versuche, 15 Minuten warten.</div>');
  if (password_verify((string)($_POST['pw'] ?? ''), $adm['hash'])) { $t = bin2hex(random_bytes(24)); $sess[$t] = time() + 12 * 3600; jw($sf, $sess); unset($l[$ip]); jw($lf, $l);
    setcookie($ck, $t, ['expires' => time() + 12 * 3600, 'path' => dirname($_SERVER['SCRIPT_NAME']) . '/', 'secure' => !empty($_SERVER['HTTPS']), 'httponly' => true, 'samesite' => 'Lax']); header('Location: ./'); exit; }
  $e['fails']++; $e['last'] = time(); $l[$ip] = $e; jw($lf, $l); page('<h1>Board Admin</h1><div class="e">Falsches Passwort.</div><form method="post"><input type="hidden" name="do" value="login"><input type="password" name="pw" placeholder="Admin-Passwort" autofocus><button>Anmelden</button></form>');
}
if (!isset($sess[$_COOKIE[$ck] ?? ''])) page('<h1>Board Admin</h1><p>AlpiType Board, Verwaltung.</p><form method="post"><input type="hidden" name="do" value="login"><input type="password" name="pw" placeholder="Admin-Passwort" autofocus><button>Anmelden</button></form>');

// --- actions
$reg = jr("$W/users.json", []); $msg = ''; $err = '';
function copy_code(string $src, string $dst): void {
  foreach (scandir($src) as $f) { if ($f === '.' || $f === '..' || $f === 'data' || $f === 'admin') continue; $s = "$src/$f"; $d = "$dst/$f";
    if (is_dir($s)) { @mkdir($d, 0755, true); copy_code($s, $d); } else copy($s, $d); }
}
function groups_in(string $s): array { $g = []; foreach (preg_split('/[,\s]+/', strtolower($s)) as $x) { $x = preg_replace('/[^a-z0-9-]/', '', $x); if ($x !== '') $g[] = $x; } return array_values(array_unique($g)) ?: ['bni-gilching']; }
function groups_of(array $i): array { $g = $i['groups'] ?? ($i['group'] ?? null); if (is_string($g)) $g = [$g]; return $g ?: ['bni-gilching']; }
function slugify(string $n): string { $s = strtolower(iconv('UTF-8', 'ASCII//TRANSLIT', $n) ?: $n); $s = preg_replace('/[^a-z0-9]+/', '-', $s); return trim($s, '-') ?: 'board'; }
$do = $_POST['do'] ?? '';
if ($do === 'create') {
  $name = trim((string)($_POST['name'] ?? '')); $lang = ($_POST['lang'] ?? 'de') === 'en' ? 'en' : 'de'; $slug = trim((string)($_POST['slug'] ?? '')) ?: slugify($name);
  $groups = groups_in((string)($_POST['groups'] ?? ''));   // boards share material only within a common group; several allowed (04.11.)
  if ($name === '') $err = 'Name fehlt.'; elseif (!preg_match('/^[a-z0-9][a-z0-9-]{1,30}$/', $slug)) $err = 'Kurzname: Kleinbuchstaben, Ziffern, Bindestrich.'; elseif (isset($reg[$slug])) $err = "$slug gibt es schon."; elseif (!is_dir("$W/code") || !is_file("$W/code/index.php")) $err = 'Kein Code unter ~/board-worker/code: auf dem Mac python3 pipeline/users.py sync.';
  else {
    $token = substr(strtr(base64_encode(random_bytes(24)), '+/', 'xy'), 0, 32); $pw = substr(strtr(base64_encode(random_bytes(9)), '+/', 'ab'), 0, 12); $dir = "$BOARD/$token";
    foreach (['decisions','uploads/photos','uploads/memos','uploads/profile','queue','img'] as $sub) @mkdir("$dir/data/$sub", 0755, true);   // the worker pulls these before the first API call
    copy_code("$W/code", $dir);
    jw("$dir/data/auth.json", ['slug' => $slug, 'name' => $name, 'lang' => $lang, 'hash' => password_hash($pw, PASSWORD_DEFAULT), 'created' => date('c'), 'must_change' => true]);
    $reg[$slug] = ['name' => $name, 'lang' => $lang, 'groups' => $groups, 'token' => $token, 'created' => date('c')]; jw("$W/users.json", $reg);
    $msg = "<div class=\"ok\">Board für <b>" . h($name) . "</b> angelegt. Link und Startpasswort, nur jetzt sichtbar:<code>$URL$token/</code><code>" . h($pw) . "</code>Beim ersten Anmelden wählt die Person ein eigenes Passwort. Der Mac legt users/$slug/ beim nächsten Lauf an (spätestens in 10 Minuten); bis dahin zeigt das Board „waiting for the Mac“.</div>";
  }
}
if ($do === 'reset' && isset($reg[$_POST['slug'] ?? ''])) {
  $slug = $_POST['slug']; $f = "$BOARD/{$reg[$slug]['token']}/data/auth.json"; $a = jr($f, []); $pw = substr(strtr(base64_encode(random_bytes(9)), '+/', 'ab'), 0, 12);
  $a['hash'] = password_hash($pw, PASSWORD_DEFAULT); $a['must_change'] = true; jw($f, $a); @unlink("$BOARD/{$reg[$slug]['token']}/data/sessions.json");
  $msg = "<div class=\"ok\">Neues Startpasswort für <b>" . h($reg[$slug]['name']) . "</b>:<code>" . h($pw) . "</code>Alle Anmeldungen dieses Boards sind beendet.</div>";
}
if ($do === 'groups' && isset($reg[$_POST['slug'] ?? ''])) {   // the Mac's users.py sync carries the new groups into users/<slug>/config.yaml within 10 minutes
  $slug = $_POST['slug']; $reg[$slug]['groups'] = groups_in((string)($_POST['groups'] ?? '')); unset($reg[$slug]['group']); jw("$W/users.json", $reg);
  $msg = '<div class="ok">' . h($reg[$slug]['name']) . ' ist jetzt in: <b>' . h(implode(', ', $reg[$slug]['groups'])) . '</b>. Gilt nach dem nächsten Lauf des Macs.</div>';
}
if (($do === 'disable' || $do === 'enable') && isset($reg[$_POST['slug'] ?? ''])) {
  $slug = $_POST['slug']; $f = "$BOARD/{$reg[$slug]['token']}/data/auth.json"; $a = jr($f, []); $a['disabled'] = $do === 'disable'; jw($f, $a);
  $reg[$slug]['disabled'] = $do === 'disable'; jw("$W/users.json", $reg); if ($do === 'disable') @unlink("$BOARD/{$reg[$slug]['token']}/data/sessions.json");
  $msg = '<div class="ok">' . h($reg[$slug]['name']) . ($do === 'disable' ? ' gesperrt.' : ' wieder frei.') . '</div>';
}
// --- page
$rows = '';
foreach ($reg as $slug => $i) {
  $rows .= '<tr><td><b>' . h($i['name'] ?? '') . '</b><br><span style="color:#5a6b7a">' . h($slug) . ' · ' . h($i['lang'] ?? 'de') . ' · seit ' . h(substr((string)($i['created'] ?? ''), 0, 10)) . (!empty($i['disabled']) ? ' · <b>gesperrt</b>' : '') . '</span></td>'
        . '<td><form method="post" style="display:inline"><input type="hidden" name="slug" value="' . h($slug) . '"><input type="text" name="groups" value="' . h(implode(', ', groups_of($i))) . '" style="width:170px" title="Gruppen, Komma"> <button class="s" name="do" value="groups">Gruppen speichern</button></form></td>'
        . '<td><a href="' . h($URL . $i['token']) . '/" target="_blank">Board öffnen</a></td>'
        . '<td><form method="post" style="display:inline"><input type="hidden" name="slug" value="' . h($slug) . '"><button class="s" name="do" value="reset" onclick="return confirm(\'Startpasswort neu setzen? Die Person wird abgemeldet.\')">Passwort neu</button> '
        . '<button class="s" name="do" value="' . (!empty($i['disabled']) ? 'enable">Freigeben' : 'disable" onclick="return confirm(\'Board sperren?\')">Sperren') . '</button></form></td></tr>';
}
page('<h1>Board Admin</h1><p>Ein Board je Person: eigener Link, eigenes Passwort, eigene Inhalte. Anton: dieser Link bleibt wie bisher, ohne Passwort.</p>' . ($err ? "<div class=\"e\">$err</div>" : '') . $msg
   . '<h2>Neues Board</h2><form method="post"><input type="hidden" name="do" value="create"><input type="text" name="name" placeholder="Vor- und Nachname" required style="width:260px"><input type="text" name="slug" placeholder="Kurzname (optional)" style="width:180px"><select name="lang"><option value="de">deutsch</option><option value="en">english</option></select><input type="text" name="groups" placeholder="Gruppen, Komma" value="bni-gilching" style="width:200px"><button>Anlegen</button></form><p style="font-size:13px">Gruppen: Boards mit einer gemeinsamen Gruppe bekommen gegenseitig freigegebenes Material vorgeschlagen, andere nicht. Ein Board kann in mehreren Gruppen sein (Komma). Antons Board gehört zu bni-gilching; seine Gruppen stehen in config.yaml.</p>'
   . '<h2>Boards · ' . count($reg) . '</h2>' . ($rows ? "<table><tr><th>Wer</th><th>Gruppen</th><th>Link</th><th></th></tr>$rows</table>" : '<p>noch keins</p>')
   . '<p style="margin-top:24px"><form method="post"><button class="s" name="do" value="logout">Abmelden</button></form></p>');
