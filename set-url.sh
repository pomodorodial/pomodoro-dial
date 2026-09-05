#!/usr/bin/env bash
# Writes your real site URL (and optionally the GitHub repo URL) into every file that needs it.
# Usage: ./set-url.sh https://your-site.example/ [https://github.com/you/pomodoro-dial]
set -e
cd "$(dirname "$0")"
SITE="${1:?Usage: ./set-url.sh https://your-site.example/ [https://github.com/you/repo]}"
SITE="${SITE%/}/"
sed -i "s#https://example.com/#$SITE#g" index.html sitemap.xml robots.txt
if [ -n "${2:-}" ]; then sed -i "s#https://github.com/example/pomodoro-dial#${2%/}#g" index.html; fi
sed -i "s#<lastmod>[0-9-]*</lastmod>#<lastmod>$(date +%F)</lastmod>#" sitemap.xml
echo "Site URL is now $SITE"
grep -c "$SITE" index.html sitemap.xml robots.txt
