# Tasks

## 1. Authorisation
- [x] 1.1 Existing app "AlpiType Analytics" reused, Share on LinkedIn + OpenID Connect, Anton authorised 19.10. (token until 18.12.)
- [ ] 1.2 Store token by path; redaction rule in logs

## 2. Publishing
- [x] 2.1 `publish.py` in the chain (fast + full), `watch.py` triggers it when an approved slot arrives; untested against the live API until the first approved card (19.10.)
- [ ] 2.2 launchd schedule for the four slots; dry-run flag
- [ ] 2.3 Daily health check, token expiry warning 7 days ahead, failure reason on the card

## 3. Company page
- [ ] 3.1 Apply for Community Management product; until granted, company cards show "no API yet"

## 4. Verify
- [ ] 4.1 Fri 06.11.: one approved test card publishes at its slot with no click; URL in posts-log.csv
- [x] Server-side publisher + tick + cron doc + computed API version + Mac watchdog (21.10., after the 07:30 post was missed)
- [ ] Anton adds the hPanel cron job (step 7)
