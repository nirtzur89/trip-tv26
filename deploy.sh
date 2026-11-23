#!/usr/bin/env bash
# Rebuilds the password-protected copy of the trip page and pushes it to GitHub Pages.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build
python3 -I inline.py ../trip.html build/index.html assets
STATICRYPT_PASSWORD="$(cat .password)" npx -y staticrypt@3 build/index.html -d docs --short --remember 180 \
  --template-title "הטיול לתאילנד וויאטנם" \
  --template-instructions "הקלידו את הסיסמה שקיבלתם מניר" \
  --template-button "כניסה" --template-placeholder "סיסמה" \
  --template-remember "לזכור אותי במכשיר הזה" --template-error "הסיסמה לא נכונה" \
  --template-color-primary "#0E8A7E" --template-color-secondary "#0f4c5c"
cp static/* docs/
touch docs/.nojekyll
if [ -d .git ]; then git add -A && (git diff --cached --quiet || git commit -q -m "Update site") && git push -q; fi
