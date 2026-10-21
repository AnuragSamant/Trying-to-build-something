# CodeMind

## Run with SQLite

The app stores workspace data in a local SQLite file at `server/codemind.sqlite`. No database server or separate SQLite installation is needed. The API uses the SQLite support built into Node.js; use Node.js 22.5 or newer.

1. Install the Node.js dependencies with `npm install`.
2. Run `npm run dev`.

The API listens on `127.0.0.1` at the port configured by `API_PORT` (default `3002`); Vite reads the same `.env` setting to proxy `/api` requests to it. The API creates the `users`, `sessions`, `projects`, `conversations`, and `messages` tables in the local database file on startup.

Create an account in the app with an email and password (minimum 8 characters), then provide your display name. Passwords are hashed by the Node API, and sign-in sessions use an HTTP-only cookie. Set `COOKIE_SECURE=true` when serving over HTTPS. Project, conversation, message, and attachment metadata are stored in SQLite and scoped to the signed-in account. Browser appearance and interface settings remain in local storage.

This is an early authentication implementation for local development, not a production identity service. Before exposing it publicly, add email verification, password reset, login rate limiting, stronger operational protections, and review the authentication flow. Python ML integration is not included yet; the JavaScript API is the service boundary for it.
