# Connecting LinkedIn to the board

**What you get:** approved personal posts go out by themselves at their slot. Until then an approved card says "you post it <slot>" and you copy the text at the slot.
**What it costs:** about 15 minutes once, then a two-minute re-login every 60 days (the board warns 7 days before).
**Who does what:** every step in the portal and the login are yours. I never sign in, never see the secret; it lives in one local file by path.

You already have the app **AlpiType Analytics** (created 28.05.2026, under the AlpiType page, company verified). Everything below happens inside that app. Its client id is already in the local config file; only the secret is missing.

---

## Step 1 · Open the app (1 min)

1. Go to https://www.linkedin.com/developers/apps (logged in as yourself).
2. Click **AlpiType Analytics**.

You see the tabs **Settings · Auth · Products · Analytics · Team members**.

## Step 2 · Products (2 min)

Click the **Products** tab. Under *Added products* look for these two:

| Product | Needed for | If it is missing |
|---|---|---|
| **Share on LinkedIn** | posting on your profile | click *Request access*, tick the terms, it is granted at once |
| **Sign In with LinkedIn using OpenID Connect** | the script learns your member id | same, granted at once |

Also note whether **Community Management API** is listed under *Added products*. It is what posting as AlpiType needs. If it is there: good, tell me, step 5 is yours already. If not: leave it for now (it needs a LinkedIn review; see step 6).

☐ Share on LinkedIn is under Added products
☐ Sign In with LinkedIn using OpenID Connect is under Added products
☐ I noted whether Community Management API is there

## Step 3 · Redirect URL and secret (3 min)

Click the **Auth** tab.

1. Scroll to *OAuth 2.0 settings* → *Authorized redirect URLs for your app* → click the pencil → **Add redirect URL** → paste exactly:
   ```
   http://localhost:8765/callback
   ```
   → **Update**. (LinkedIn accepts http for localhost. If the form refuses it, stop here and tell me; I switch the script to an https page on alpitype.de.)
2. Scroll up to *Application credentials*. Next to **Primary Client Secret** click the eye icon, then copy it.
3. Open this file in any editor and paste the secret between the empty quotes:
   ```
   ~/dev/linkedin-system/config.local.linkedin.json
   ```
   It then looks like this (your real values, no spaces inside the quotes):
   ```
   {"client_id": "78nli4pak5l6sm", "client_secret": "PASTE_HERE"}
   ```
   Save. The file is gitignored and readable only by you.

Under *OAuth 2.0 scopes* you should now see `openid`, `profile`, `w_member_social` (and, with Community Management, `w_organization_social`, `r_organization_social`). Nothing to click there.

☐ Redirect URL saved
☐ Secret pasted into the local file

## Step 4 · Authorise (2 min)

In the terminal of this session, type the line with the leading `!`:
```
! /opt/anaconda3/bin/python3 ~/dev/linkedin-system/pipeline/linkedin_auth.py
```
What happens:
1. The terminal prints "Opening the browser; log in and allow. Waiting on http://localhost:8765/callback".
2. Your browser opens a LinkedIn page "AlpiType Analytics would like to …". Log in if asked, press **Allow**.
3. The browser shows a plain page "Done. You can close this tab."
4. The terminal prints "authorised as Anton Lytvynenko, token valid until <date>, scopes: …".

The token is saved into the same local file. Within a minute the board's system line reads "LinkedIn connected until <date> (personal only)" and approved personal cards say "posts itself <slot>".

If the terminal prints "no code received: …" instead, copy that line to me.

☐ "authorised as …" printed
☐ Board says "LinkedIn connected"

## Step 5 · Dry run, nothing goes out (1 min)

```
! /opt/anaconda3/bin/python3 ~/dev/linkedin-system/pipeline/publish.py --dry
```
It lists each approved card with slot, channel, length and image, and publishes nothing. The real publishing step runs inside the worker at the slot; the first real post is the next approved personal card after this, and its URL lands in `posts-log.csv` and on the card.

## Step 6 · Company page (later; LinkedIn review)

Posting as AlpiType needs the product **Community Management API**. If step 2 showed it: run step 4 again with `--org` at the end of the command, press Allow again, done; company cards then say "posts itself" too.

If it was not there: Products tab → Community Management API → *Request access*. The form asks for the use case; a fitting answer: "Publishing our own company page posts from an internal scheduling tool. Single page (AlpiType), own content only, no third-party pages, no data collection." Review takes days to a few weeks; LinkedIn mails you. Then the `--org` run above. Until then company cards stay "you post it".

## Every 60 days

The token expires. The board shows a red line "LinkedIn token · expires in n days · run: pipeline/linkedin_auth.py" seven days before. Step 4 again, two minutes.

## What the system never does

Only posts what you approved, on your profile (and the page once step 6 is done). No reading of other people's content through the API, no comments, no messages. Token and secret stay in the local file; the board, the repo and the docs never show them.
