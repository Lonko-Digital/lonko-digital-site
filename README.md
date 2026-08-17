# Lonko Digital — Public Company Website

Static public website for **Lonko Digital**. This repository is intentionally separate from the private operational Marketing Intelligence Platform.

## Purpose

- Establish a legitimate public company presence
- Provide a stable company URL via GitHub Pages (optional custom domain later)
- Host Privacy Policy and Terms of Use
- Support future developer-platform/API applications (public URLs only)
- Reserve architecture for a future Public Executive Showcase
- Maintain clear separation from private operations and future commercial SaaS

## Repository boundary (critical)

| Repository | Purpose | Must never contain |
|---|---|---|
| **`lonko-digital-site`** (this repo) | Public company website | Credentials, OAuth tokens, account IDs, private reports, customer data, private app code |
| **Private operational platform** (separate private repository) | Operational intelligence platform | Public publishing without governance review |

**Do not copy private application templates, runtime code, screenshots, or configuration into this repository.**

## Organization

- **GitHub organization:** Lonko-Digital
- **Public repository:** lonko-digital-site
- **Expected GitHub Pages URL:** https://lonko-digital.github.io/lonko-digital-site/

## Architecture

- **Stack:** HTML, CSS, minimal vanilla JavaScript
- **Hosting target:** GitHub Pages (free tier)
- **No backend, database, or Node runtime**
- **No server-side contact form**
- **Google Tag Manager:** container `GTM-53DPJ88F` is installed sitewide as the tag-management foundation only. No Google Ads, GA4, Meta Pixel, LinkedIn Insight Tag, or other analytics/advertising tags are currently configured to fire through it.

```
/
├── index.html
├── 404.html
├── about/index.html
├── privacy/index.html
├── terms/index.html
├── contact/index.html
├── assets/
│   ├── css/site.css
│   ├── js/site.js
│   └── images/          (reserved)
├── config/
│   └── contact.example.json
├── platform/              (reserved — not built yet)
│   └── README.md
├── scripts/
│   └── public_safety_audit.py
├── robots.txt
└── sitemap.xml
```

## Local preview

From the repository root:

```bash
# Python 3
python -m http.server 8080

# Or Node (if installed locally — not required for the site)
npx --yes serve -l 8080
```

Open `http://localhost:8080/` and verify pages at common widths (1440, 1280, 768, 390, 375).

Run the public safety audit:

```bash
python scripts/public_safety_audit.py
```

## GitHub Pages deployment

**This public site is live** at `https://lonko-digital.github.io/lonko-digital-site/`.

GitHub Pages is configured from the default branch (`main`) at repository root. HTTPS is enabled by default on GitHub Pages.

### Custom domain (future)

Custom domain setup is optional and not required for publication. If added later:

1. Add a `CNAME` file with the confirmed domain — only after domain ownership is confirmed.
2. Configure DNS per [GitHub Pages custom domain documentation](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site).
3. Enable “Enforce HTTPS” after DNS propagates.

## Future Public Executive Showcase

A future `/platform/` or `/showcase/` section is **reserved but not built**. Publishing requires a separate gate:

- Synthetic data audit
- Privacy scrub
- Rich demo data
- Executive storytelling
- Responsive QA
- Recruiter/C-level review
- Publication approval
- **READY FOR LINKEDIN** determination

See `platform/README.md`. Publishing gates are maintained internally by Lonko Digital.

## LinkedIn developer context

This site may later provide:

- Public company URL
- Privacy Policy URL
- Credible public business presence

Creating this site **does not guarantee** LinkedIn Advertising API approval. Approval remains governed by LinkedIn.

## Contact email

Public contact: [lonkodigital@gmail.com](mailto:lonkodigital@gmail.com)

See `config/contact.example.json` for the configuration pattern.

## Governance

Publishing governance is maintained internally by Lonko Digital. Public-facing safety checks for this repository are enforced via `scripts/public_safety_audit.py`.

## Status

Public company website is **published** via GitHub Pages at `https://lonko-digital.github.io/lonko-digital-site/`.
