# Claude's Picks — a Stremio add-on

A static, catalog-only Stremio add-on served by GitHub Pages. It adds a
"Claude's Picks" row (movies and series) to the Stremio home screen.

**Install:** https://d-o-g-e.github.io/stremio/ (tap *Install*), or paste
`https://d-o-g-e.github.io/stremio/manifest.json` into Stremio's add-on search bar.

## Updating the list

1. Find each title's IMDb id as Stremio sees it (Cinemeta):
   `https://v3-cinemeta.strem.io/catalog/movie/top/search=<title>.json`
   (use `series` instead of `movie` for shows).
2. Add entries to the top of `picks.json` (`id`, `type` = movie|series, `name`,
   `year`, `list`, `note`).
3. Run `python3 build.py`, then commit and push. Pages redeploys in about a minute;
   Stremio picks up the change on its next refresh (restart the app if it doesn't).
