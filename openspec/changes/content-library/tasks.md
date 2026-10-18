# Tasks

## 1. Repo and layout
- [ ] 1.1 Create `~/dev/linkedin-system`, move `openspec/` and the opsx commands/skills there, `.gitignore` for library media
- [ ] 1.2 `config.yaml` with the path to the campaign CSVs
- [ ] 1.3 Create `library/{photos,memos,drafts,published}` with empty index files

## 2. Migration
- [ ] 2.1 Move existing photos and used-up list into `library/photos` (with photo-pool task 2.3)
- [ ] 2.2 Fill `library/published` from posts-log.csv and `local/reports/out`
- [ ] 2.3 Pre-commit size check (no media, no file > 1 MB)

## 3. Reuse
- [ ] 3.1 Monthly rotation step: photos back to ready after 6 months / 20 posts; recyclable topics list
- [ ] 3.2 Size line in the monthly report

## 4. Verify
- [ ] 4.1 Mon 19.10.: new repo pushed with specs only; library folders exist; git shows no media
