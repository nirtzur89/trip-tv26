#!/usr/bin/env bash
# Rebuilds the password-protected copy of the trip page and pushes it to GitHub Pages.
set -euo pipefail
cd "$(dirname "$0")"
# Sync the page source with the private repo (trip-tv26-source) so edits made on GitHub are included.
if [ -d ../.git ]; then
  git -C .. add trip.html
  git -C .. diff --cached --quiet || git -C .. commit -q -m "Update trip page"
  git -C .. pull -q --rebase || { git -C .. rebase --abort; echo "Source repo has conflicting edits; resolve them before deploying." >&2; exit 1; }
  git -C .. push -q
fi
mkdir -p build
python3 -I inline.py ../trip.html build/index.html assets
STATICRYPT_PASSWORD="$(cat .password)" npx -y staticrypt@3 build/index.html -d docs --short --remember 180 \
  --template-title "הטיול לתאילנד וויאטנם" \
  --template-instructions "הקלידו את הסיסמה שקיבלתם מניר וממאיה" \
  --template-button "כניסה" --template-placeholder "סיסמה" \
  --template-remember "לזכור אותי במכשיר הזה" --template-error "הסיסמה לא נכונה" \
  --template-color-primary "#0E8A7E" --template-color-secondary "#0f4c5c"
cp static/* docs/
SITE_LINK="$(STATICRYPT_PASSWORD="$(cat .password)" npx -y staticrypt@3 --share https://nirtzur89.github.io/trip-tv26/ --share-remember 2>/dev/null | tail -1)"
python3 -I export_data.py ../trip.html "$SITE_LINK" | openssl enc -aes-256-cbc -pbkdf2 -salt -a -pass file:.datakey > docs/d.enc
touch docs/.nojekyll
if [ -d .git ]; then git add -A && (git diff --cached --quiet || git commit -q -m "Update site") && git push -q; fi
