#!/usr/bin/env bash
# Writes your site URL (and optionally the GitHub repo URL) into every file that needs it.
# Works both the first time (placeholder) and later (replaces the current URL).
# Usage: ./set-url.sh https://your-site.example/ [https://github.com/you/pomodoro-dial]
set -e
cd "$(dirname "$0")"
SITE="${1:?Usage: ./set-url.sh https://your-site.example/ [https://github.com/you/repo]}"
SITE="${SITE%/}/"
CURRENT=$(grep -o '<link rel="canonical" href="[^"]*"' index.html | sed 's/.*href="//; s/"$//')
CURRENT="${CURRENT:-https://example.com/}"
sed -i "s#$CURRENT#$SITE#g" index.html sitemap.xml robots.txt
if [ -n "${2:-}" ]; then
  CURREPO=$(grep -o 'href="https://github.com/[^"]*"' index.html | head -1 | sed 's/href="//; s/"$//')
  sed -i "s#${CURREPO:-https://github.com/example/pomodoro-dial}#${2%/}#g" index.html
fi
sed -i "s#<lastmod>[0-9-]*</lastmod>#<lastmod>$(date +%F)</lastmod>#" sitemap.xml
echo "Site URL is now $SITE (was $CURRENT)"
grep -c "$SITE" index.html sitemap.xml robots.txt
