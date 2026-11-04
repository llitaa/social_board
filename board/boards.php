<?php
// Boards as a library (04.11.2026): create a board, read and write the registry, know who "I" am. Used by board/admin/ and by
// api.php (invite from any board). Registry ~/board-worker/users.json = {slug: {name, lang, groups[], token, created, disabled?,
// invited_by?}}; Anton's own board is the entry "anton" (no password, token = its directory). A group is who shares with whom.
declare(strict_types=1);
function boards_home(): string {   // web PHP has no HOME: walk up from this file until board-worker/ is found (board/boards.php and board/<token>/boards.php sit at different depths)
  if (!empty($_SERVER['HOME']) || getenv('HOME')) return $_SERVER['HOME'] ?? getenv('HOME');
  $d = __DIR__; for ($i = 0; $i < 8; $i++) { $d = dirname($d); if (is_dir("$d/board-worker")) return $d; } return dirname(__DIR__, 4);
}
function boards_w(): string { return boards_home() . '/board-worker'; }
function boards_jr(string $f, $d) { $x = is_file($f) ? json_decode((string)file_get_contents($f), true) : null; return $x ?? $d; }
function boards_jw(string $f, $v): void { file_put_contents($f, json_encode($v, JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES), LOCK_EX); @chmod($f, 0600); }
function boards_registry(): array { return boards_jr(boards_w() . '/users.json', []); }
function boards_save(array $reg): void { boards_jw(boards_w() . '/users.json', $reg); }
function boards_groups(array $i): array { $g = $i['groups'] ?? ($i['group'] ?? null); if (is_string($g)) $g = [$g]; return array_values(array_filter((array)$g)) ?: ['bni-gilching']; }
function boards_group_in(string $s): array { $g = []; foreach (preg_split('/[,\s]+/', strtolower($s)) as $x) { $x = preg_replace('/[^a-z0-9-]/', '', $x); if ($x !== '' && strlen($x) <= 30) $g[] = $x; } return array_values(array_unique($g)); }
function boards_slugify(string $n): string { $s = strtolower(iconv('UTF-8', 'ASCII//TRANSLIT', $n) ?: $n); $s = preg_replace('/[^a-z0-9]+/', '-', $s); return trim($s, '-') ?: 'board'; }
function boards_url(): string { return 'https://' . ($_SERVER['HTTP_HOST'] ?? 'alpitype.de') . '/board/'; }
function boards_copy_code(string $src, string $dst): void {   // everything under ~/board-worker/code, recursively (same as the admin page did)
  @mkdir($dst, 0755, true);
  foreach (scandir($src) as $f) { if ($f === '.' || $f === '..') continue; $s = "$src/$f"; $d = "$dst/$f";
    if (is_dir($s)) { @mkdir($d, 0755, true); boards_copy_code($s, $d); } else copy($s, $d); }
}
/** Create a board. Returns ['slug','token','pw'] or ['error' => reason]. $by = slug of the inviting board or 'admin'. */
function boards_create(string $name, string $lang, array $groups, string $by, string $slug = ''): array {
  $W = boards_w(); $BOARD = is_file(__DIR__ . '/api.php') ? dirname(__DIR__) : __DIR__;   // board/<token>/boards.php (invite) or board/boards.php (admin): a board dir has api.php, the boards root has not
  $name = trim($name); $lang = $lang === 'en' ? 'en' : 'de'; $slug = trim($slug) ?: boards_slugify($name); $reg = boards_registry();
  if ($name === '' || mb_strlen($name) > 80) return ['error' => 'Name fehlt.'];
  if (!preg_match('/^[a-z0-9][a-z0-9-]{1,30}$/', $slug)) return ['error' => 'Kurzname: Kleinbuchstaben, Ziffern, Bindestrich.'];
  $base = $slug; $n = 2; while (isset($reg[$slug])) { $slug = "$base-$n"; $n++; }   // same name twice: anna, anna-2
  if (!is_dir("$W/code") || !is_file("$W/code/index.php")) return ['error' => 'Kein Code unter ~/board-worker/code: auf dem Mac python3 pipeline/users.py sync.'];
  $token = substr(strtr(base64_encode(random_bytes(24)), '+/', 'xy'), 0, 32); $pw = substr(strtr(base64_encode(random_bytes(9)), '+/', 'ab'), 0, 12); $dir = "$BOARD/$token";
  foreach (['decisions','uploads/photos','uploads/memos','uploads/profile','queue','img'] as $sub) @mkdir("$dir/data/$sub", 0755, true);   // the worker pulls these before the first API call
  boards_copy_code("$W/code", $dir);
  boards_jw("$dir/data/auth.json", ['slug' => $slug, 'name' => $name, 'lang' => $lang, 'hash' => password_hash($pw, PASSWORD_DEFAULT), 'created' => date('c'), 'must_change' => true]);
  $reg[$slug] = ['name' => $name, 'lang' => $lang, 'groups' => $groups ?: ['bni-gilching'], 'token' => $token, 'created' => date('c'), 'invited_by' => $by]; boards_save($reg);
  return ['slug' => $slug, 'token' => $token, 'pw' => $pw, 'url' => boards_url() . $token . '/'];
}
/** Which board am I: the login's slug, or "anton" on the open board (registered on first use, token = this directory). */
function boards_self(?array $auth): array {
  $reg = boards_registry();
  if ($auth) { $slug = $auth['slug']; if (!isset($reg[$slug])) return ['slug' => $slug, 'name' => $auth['name'] ?? $slug, 'groups' => ['bni-gilching'], 'default' => false]; return ['slug' => $slug, 'name' => $reg[$slug]['name'] ?? $slug, 'groups' => boards_groups($reg[$slug]), 'default' => false]; }
  if (!isset($reg['anton'])) { $reg['anton'] = ['name' => 'Anton Lytvynenko', 'lang' => 'de', 'groups' => ['bni-gilching'], 'token' => basename(dirname($_SERVER['SCRIPT_FILENAME'] ?? __DIR__)), 'self' => true, 'created' => date('c')]; boards_save($reg); }
  return ['slug' => 'anton', 'name' => $reg['anton']['name'], 'groups' => boards_groups($reg['anton']), 'default' => true];
}
/** Members of my groups from the registry (immediate, no worker needed) plus shared-photo counts from network.json where the worker has them. */
function boards_network(array $me, array $net): array {
  $reg = boards_registry(); $cnt = []; foreach ($net['groups'] ?? [] as $g) foreach ($g['members'] ?? [] as $m) $cnt[$m['name']] = $m['shared'] ?? 0;
  $out = [];
  foreach ($me['groups'] as $g) {
    $members = [];
    foreach ($reg as $slug => $i) { if ($slug === $me['slug'] || !empty($i['disabled']) || !in_array($g, boards_groups($i), true)) continue; $members[] = ['name' => $i['name'] ?? $slug, 'shared' => $cnt[$i['name'] ?? ''] ?? 0, 'since' => substr((string)($i['created'] ?? ''), 0, 10)]; }
    $out[] = ['group' => $g, 'members' => $members];
  }
  return $out;
}
