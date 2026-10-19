# Connecting LinkedIn (one hour, once)

Until this is done, an approved card says "you post it <slot>": at the slot you press Copy text, save the image and post in the LinkedIn app. After it, approved personal posts go out by themselves at the slot (`pipeline/publish.py`). Nothing here is done by the assistant: the app, the login and the consent are yours.

## 1. Create the app (10 min)
1. Open https://www.linkedin.com/developers/apps while logged in as yourself, press **Create app**.
2. App name: `AlpiType Board`. LinkedIn Page: **AlpiType** (the company page; you are its admin). Privacy policy URL: `https://alpitype.de/datenschutz/` (or the current page). Upload the logo. Accept the legal terms, press Create app.
3. **Settings** tab → **Verify** next to the page name → Generate URL → open that URL (you are the page admin) → Verify. The app status becomes "Verified".

## 2. Add the products (5 min, instant)
**Products** tab → Request access for
- **Share on LinkedIn** (scope `w_member_social`: posting on your profile)
- **Sign In with LinkedIn using OpenID Connect** (scopes `openid profile`: so the script learns your member id)

Both are granted at once, no review.

## 3. Redirect URL and keys (5 min)
**Auth** tab:
1. Under *OAuth 2.0 settings* → Authorized redirect URLs → Add: `http://localhost:8765/callback` (LinkedIn accepts http for localhost; if the form refuses it, tell me and I switch the script to an https page on alpitype.de).
2. Copy **Client ID** and **Primary Client Secret** into a new file `~/dev/linkedin-system/config.local.linkedin.json` (gitignored):
```
{"client_id": "…", "client_secret": "…"}
```
Never paste the secret anywhere else.

## 4. Authorise (2 min)
In the terminal of this session:
```
! /opt/anaconda3/bin/python3 ~/dev/linkedin-system/pipeline/linkedin_auth.py
```
The browser opens LinkedIn, you log in and press Allow, the tab says "Done". The token (valid 60 days) and your member URN are saved into the same local file. The board's system line then says "LinkedIn connected until <date>", approved cards say "posts itself <slot>".

Dry run that shows what would go out and sends nothing:
```
/opt/anaconda3/bin/python3 ~/dev/linkedin-system/pipeline/publish.py --dry
```

## 5. Company page (later, LinkedIn review)
Posting as AlpiType needs the **Community Management API** product (scope `w_organization_social`). Products tab → Community Management API → Request access → the form asks for the use case (own company page, own posts, no third parties) and takes days to a few weeks. When granted: `linkedin_auth.py --org` once more, and company cards post themselves too. Until then company cards stay "you post it".

## What the system never does
No reading of other people's content, no comments, no messages through the API, only posting what you approved. Token and keys live in the local file by path; the board, the repo and the docs never show them. The board warns 7 days before the token expires; you run step 4 again.
