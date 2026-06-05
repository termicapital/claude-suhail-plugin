# AI Workshop — Registration form

A designed registration page (`index.html`) styled to match the AI Workshop flyer,
that writes every signup as a row in **your own Google Sheet** via a small Google
Apps Script web app.

```
registration/
├── index.html       ← the form (open in a browser / host anywhere)
├── apps-script.gs   ← paste into your Google Sheet's Apps Script
└── README.md        ← you are here
```

## What the registrant fills in
Name, work email, company/team, role, AI experience, which of the 4 sessions
they'll attend, and an optional goal. Each submission lands in the sheet with a
timestamp.

---

## Setup — about 2 minutes

### 1. Create the Google Sheet
- Go to <https://sheets.new> and name it e.g. **"AI Workshop — Registrations"**.
- You don't need to add any columns; the script creates the header row on the first signup.

### 2. Add the backend script
1. In that sheet: **Extensions → Apps Script**.
2. Delete whatever is in `Code.gs`, then paste the entire contents of **`apps-script.gs`**.
3. Click **Save** (💾).

### 3. Deploy it as a Web App
1. Click **Deploy → New deployment**.
2. Next to "Select type" click the gear ⚙ → **Web app**.
3. Set:
   - **Description:** `AI Workshop registration`
   - **Execute as:** **Me**
   - **Who has access:** **Anyone**  ← required so the public form can post.
4. Click **Deploy**, then **Authorize access** and approve with your Google account.
   (You'll see a "Google hasn't verified this app" screen — it's your own script;
   click *Advanced → Go to … (unsafe)* to continue.)
5. Copy the **Web app URL** (looks like `https://script.google.com/macros/s/AKfy…/exec`).

### 4. Connect the form
- Open **`index.html`**, find the `CONFIG` block near the bottom, and paste your URL:
  ```js
  const CONFIG = {
    endpoint: "https://script.google.com/macros/s/AKfy…/exec"
  };
  ```
- Save. Done — open `index.html` and submit a test entry; it should appear in the sheet.

---

## Hosting the form
`index.html` is a single self-contained file. Options:
- **Quick test:** double-click to open it locally in your browser.
- **Share a link (free):** enable **GitHub Pages** on this repo (Settings → Pages →
  deploy from branch) and the form will be served at
  `https://<org>.github.io/<repo>/registration/`.
- Or drop it on any static host (Netlify, Vercel, an internal server, etc.).

## Notes
- **Updating the script later:** after editing `apps-script.gs`, do
  **Deploy → Manage deployments → Edit ✏ → Version: New version → Deploy** so the
  changes go live (the URL stays the same).
- **Spam:** the form has a hidden honeypot field; bots that fill it are silently dropped.
- **Privacy:** data goes only to your sheet. The script runs as you and isn't shared.
- **Editing sessions/dates:** the session list and dates are plain HTML in
  `index.html` (the `.sessions` list and `.datebox`) — edit there if plans change.
