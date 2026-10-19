# SnooCommerce

A Reddit Snoo-themed shopping website built with React + Vite + Styled Components.

## Features

- Browse products in a responsive grid layout with Snoo branding
- Add items to cart with upvote-style buttons
- Cart persists in localStorage across page refreshes
- Fake "Pay Now" button with a coming-soon modal
- Lead registration form (Name + Email)
- Reddit orangered color palette with Snoo iconography

## Getting Started

```bash
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

## Build

```bash
npm run build
```

Output is in the `dist/` folder.

## Reddit OAuth callback

After deploying, register this exact redirect URI in the developer app:

```text
https://snoocommerce.onrender.com/oauth/callback.html
```

Use the same URI in the authorization request and token exchange. Request `scope=adsread` and generate a fresh random `state` for each authorization. After consent, the callback displays the returned code and state; paste your original state to verify it and enable the copy button. Exchange the one-time code promptly with your local token client. The callback itself does not exchange tokens, accept client secrets, store codes, or load the storefront's advertising pixels. It removes the query and fragment from the address bar after reading the response; refreshing clears the result.

The page is a standalone static asset copied to `dist/oauth/callback.html` by `npm run build`. Render serves existing files before the storefront's catch-all rewrite, so no API backend or routing change is required.

## Local Reddit LEAD CAPI Job

The additional Reddit LEAD-only CAPI job sends standard `LEAD` events to pixel `p2_18kzhk31x1bzs` without changing the deployed Render cron jobs.

Set the token locally in `.env`:

```bash
REDDIT_LEAD_CAPI_ACCESS_TOKEN=
REDDIT_LEAD_CAPI_PIXEL_ID=p2_18kzhk31x1bzs
```

Run the job manually:

```bash
./scripts/send-reddit-leads.sh
```

## Deploy to Netlify

1. Push this repo to GitHub.
2. Connect the repo in [Netlify](https://app.netlify.com).
3. Netlify will auto-detect the build settings from `netlify.toml`.

## Tech Stack

- React 18
- Vite
- Styled Components
- React Router v6
