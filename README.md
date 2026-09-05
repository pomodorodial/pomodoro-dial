# Pomodoro Dial

A free, single-file Pomodoro timer with a wind-up dial. Everything runs in the browser; nothing is sent to a server.

- Tasks with pomodoro estimates and a rough finish time
- 25 / 5 / 15 minute sessions, long break after four
- Adjust by the minute (−1, +1, Shift for five) or click the digits and type
- Accurate in background tabs, resumes after a reload
- Chime, optional ticking, desktop notifications
- Keyboard shortcuts, light and dark themes
- Presets by link: `/?focus=50&short=10&long=20&sets=4` sets the durations and the number of focus sessions before a long break
- Fonts served from the site itself (`fonts/`, SIL Open Font License); the only third-party request is the analytics beacon

## Run it locally

```bash
./start.sh          # http://localhost:8080, localhost only
./start.sh 9000     # another port
```

Or open `index.html` directly in a browser.

## Put it on the internet for $0

The site is static, so any free static host works. GitHub Pages is the simplest.

### GitHub Pages

1. Create a new **public** repository on github.com, for example `pomodoro-dial`. Don't add a README or license there; this folder already has one.
2. Push this folder:

   ```bash
   git remote add origin https://github.com/YOUR-USER/pomodoro-dial.git
   git push -u origin main
   ```

3. On GitHub open **Settings → Pages**, set *Source* to **Deploy from a branch**, branch `main`, folder `/ (root)`, and save.
4. After a minute the site is live at `https://YOUR-USER.github.io/pomodoro-dial/`.
5. Write that URL into the page, sitemap and robots file, then push again:

   ```bash
   ./set-url.sh https://YOUR-USER.github.io/pomodoro-dial/ https://github.com/YOUR-USER/pomodoro-dial
   git commit -am "Set site URL" && git push
   ```

### Cloudflare Pages (alternative, also free)

Connect the same GitHub repository at dash.cloudflare.com → Workers & Pages → Create → Pages. No build command, output directory `/`. You get `something.pages.dev` with unlimited bandwidth.

### Custom domain (optional, about $10 a year)

A domain is the only thing worth paying for: it is your brand in search results and you keep it if you ever change hosts. Buy it at Cloudflare Registrar (sold at cost) or Porkbun, point it at GitHub Pages or Cloudflare Pages following their docs, then run `./set-url.sh` again with the new URL.

## After going live

1. **Google Search Console** (search.google.com/search-console): add the site, verify it, submit `sitemap.xml`, and use *URL inspection → Request indexing* on the home page.
2. **Bing Webmaster Tools**: same steps. It also feeds DuckDuckGo and Yahoo.
3. Check the share preview at opengraph.xyz or by pasting the link into a chat app.
4. Tell people: a "Show HN" on news.ycombinator.com, r/productivity and r/webdev, Product Hunt, X. Links from those places are what moves a new site up in Google.

## Files

| File | Purpose |
| --- | --- |
| `index.html` | The whole app, plus SEO tags and the About section |
| `favicon.svg`, `apple-touch-icon.png`, `icon-512.png` | Icons |
| `og-image.png` | Preview image for links shared on social media and chat |
| `robots.txt`, `sitemap.xml` | Search engine files |
| `.nojekyll` | Tells GitHub Pages to serve the files as they are |
| `set-url.sh` | Writes your real URL into every file that needs it |
| `start.sh` | Local server |
