# Tasks

## 1. Authorisation
- [ ] 1.1 Create the LinkedIn developer app, enable Share on LinkedIn, Anton authorises once
- [ ] 1.2 Store token by path; redaction rule in logs

## 2. Publishing
- [ ] 2.1 `publish.py`: read approved cards at slot, upload image, create post, write URL to posts-log.csv
- [ ] 2.2 launchd schedule for the four slots; dry-run flag
- [ ] 2.3 Daily health check, token expiry warning 7 days ahead, failure reason on the card

## 3. Company page
- [ ] 3.1 Apply for Community Management product; until granted, company cards show "no API yet"

## 4. Verify
- [ ] 4.1 Fri 06.11.: one approved test card publishes at its slot with no click; URL in posts-log.csv
