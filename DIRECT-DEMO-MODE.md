# Direct Demo Mode

The frontend login screen has been removed. Opening the client now goes directly to the Dashboard.

## What changed
- `/` redirects directly to `/dashboard`.
- Login page and protected-route redirect were removed from the frontend.
- The UI runs with a built-in demo administrator identity.
- The API accepts requests without a Bearer token and uses/creates `demo@oralai.local` as an admin user so existing patient, prediction, report, and admin APIs continue to work.
- Report opening no longer depends on a stored login token.

## Important security note
This mode is intended for local development, demonstrations, and academic project presentations only. It is **not secure for public production deployment** because authentication is intentionally bypassed.

To use the project publicly/for production, restore JWT authentication and protect the API before deployment.
