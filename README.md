# Elm Grove Garage Door — elmgrovegaragedoor.com

Static website: a homepage plus 14 service pages (same service list as a1garage.com), served from Cloudflare Workers static assets.

## Structure

- `content/home.json`, `content/services/*.json` — all page copy. The homepage has about 4,800 words on the page and each service page has 3,200–3,350.
- `public/assets/css/site.css` — styles and color palette.
- `public/assets/js/site.js` — motion and interactions.
- `public/images/` — 60 new Envato photos (none used on the earlier garage door sites), converted to large WebP (2560px for full-width, 1920px for the rest). Originals are in `~/Downloads/`, web copies in `~/Downloads/elmgrove-garage-door-images/web/`.
- `build.py` — the generator. Site settings are in `SITE` at the top: phone, hours, email, form endpoint, logo and favicon.
- `public/*.html` and `public/*/index.html` are generated. Edit the content or `build.py`, not the HTML.

## Build and deploy

```bash
python3 build.py          # regenerates the HTML in ./public
npx wrangler deploy       # deploys ./public to Cloudflare
```

To preview locally: `cd public && python3 -m http.server 8000`.

## Before going live

1. **Phone**: set `SITE["phone"]` and `SITE["phone_href"]` in `build.py` (currently the placeholder `(262) 000-0000`). Confirm `SITE["hours"]` and `SITE["email"]`.
2. **Quote form**: set `SITE["form_endpoint"]` to a Formspree, Web3Forms or Worker URL. Until then the form validates and shows a thank-you message, but nothing is delivered.
3. **Logo**: put `logo.webp` (+ `logo@2x.webp`) in `public/images/` and set `SITE["logo"] = "/images/logo.webp"`. Until then a built-in elm-tree wordmark shows.
4. **Favicon**: add `favicon.ico`, `favicon-32.png`, `apple-touch-icon.png`, `icon-192.png`, `icon-512.png` to `public/` and set `SITE["favicon"] = True`.
5. Run `python3 build.py` after any change.

## Design: "Canopy"

A new look, different from the earlier garage door sites, built around Elm Grove's tree canopy (the village takes its name from its groves and has been a Tree City USA since 1989):

- Instrument Serif display headlines with italic accents, Onest body text.
- A quote form in the header (hero) on every page, with an animated gradient border.
- Low-opacity photo backgrounds with parallax behind the hero and alternating sections, plus a slow "dappled light" overlay.
- Drifting leaves (canvas) in every hero and spinning tree-ring badges.
- One full-width band on the homepage: the photo opens like an iris as you scroll, with outlined "Elm Grove" type drifting across it.
- Sticky stacking problem cards, a scroll-driven horizontal reel of door styles, a filterable service grid, season tabs with a sliding indicator, and a scroll-drawn process line.
- Photo frames that wipe open on scroll, word-by-word headline reveals, magnetic buttons, 3D tilt cards, cursor glow, marquee, scroll progress bar and a back-to-top progress ring. Everything respects `prefers-reduced-motion`.
- A Google Map of Elm Grove, WI in the footer (and in the homepage service area section).

## Color palette: soft Elm Grove greens and autumn amber

| Token | Hex | Use |
|---|---|---|
| Elm green | `#557f66` | Buttons, accents, links |
| Elm hover | `#446a54` | Hover states, small green text |
| Elm light | `#8db59a` | Leaves, highlights on dark |
| Leaf tint / Sage | `#e3ece4` / `#eef3ee` | Icon chips, tinted sections |
| Deep grove | `#1c2f29` | Top bar, marquee, dark sections, footer |
| Autumn amber | `#d9a35e` | Quote button, pre-footer, accents |
| Amber tint | `#f8ecd9` | Soft highlight cards |
| Village navy | `#2f4c60` | Reserved accent |
| Linen / Paper | `#f8f6f0` / `#fcfbf8` | Backgrounds |
| Ink | `#1b2a25` | Headings and text |
