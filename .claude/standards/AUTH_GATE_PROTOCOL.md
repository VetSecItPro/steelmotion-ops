# Auth Gate Protocol for Browser-Based Skills

**Version:** 1.0
**Applies to:** Any skill that launches a Playwright browser and may encounter a login screen.
**Skills affected:** `/browse`, `/qatest`, `/redteam`

---

## The Problem

Skills launch a browser, navigate to the app, and immediately hit a login/auth screen. Without credentials, the skill hangs or tests only the login page. The user has to manually intervene, breaking the autonomous flow.

**This must never happen.** Browser skills must detect and handle auth gates automatically.

---

## Detection

When navigating to any page, check for an auth gate BEFORE proceeding with testing:

### Signal 1: URL Redirect
After navigating, check if the final URL differs from the requested URL:
```
Navigated to: http://localhost:3000/dashboard
Landed on:    http://localhost:3000/login?from=/dashboard
```
If the URL contains `/login`, `/signin`, `/auth`, or a `from`/`redirect` query param, an auth gate is active.

### Signal 2: Page Content
Take a browser snapshot and look for:
- Login form elements (username/password inputs, "Sign in" button)
- Auth-related text ("Please log in", "Authentication required", "Enter your credentials")
- OAuth buttons ("Sign in with Google", "Continue with GitHub")

### Signal 3: HTTP Status
If an API call returns 401 or 403, the app requires authentication.

### Signal 4: Phase 0 Detection
During skill initialization, the auth system was already detected (NextAuth, Supabase Auth, Clerk, etc.). If auth exists, assume auth gates exist on protected routes.

---

## Resolution (in priority order)

### Strategy 1: Service Token (API-only, fastest)
If the app supports service token auth (for example an `x-service-token` header):
- Use the token for all API calls via curl (no browser auth needed)
- For browser testing of protected pages, use Strategy 2 or 3

### Strategy 2: Create Test User via API, Login via Browser
This is the primary strategy for browser-based testing:

```
STEP 1: Create test user
   - POST to auth API endpoint (detected in Phase 0)
   - Use recognizable test credentials:
     - Email: qatest_{unix_timestamp}@example.com
     - Username: qatest_{unix_timestamp}
     - Password: QaTest!{unix_timestamp}!Secure
     - Role: you (not admin - test with realistic permissions)
   - If signup API doesn't exist, check for:
     - Admin user creation API (POST /api/users)
     - Direct database seeding (if accessible via API)
     - Default/demo credentials in .env or README
   - Track the created user ID for cleanup

STEP 2: Login via browser
   - Navigate to the login page
   - Fill the login form:
     - browser_fill_form with username/email and password
   - Click the submit/login button
   - Wait for redirect to the authenticated page
   - Verify: URL is no longer /login, session cookie is set

STEP 3: Verify authenticated state
   - Navigate to a known protected route
   - Confirm: no redirect back to login
   - Confirm: page content loads (not empty/error state)

STEP 4: Proceed with testing
   - All subsequent browser navigation uses the authenticated session
   - Cookies persist across page navigations within the same browser instance

STEP 5: Cleanup (at end of skill run)
   - Delete the test user via API (DELETE /api/users/{id} or equivalent)
   - If admin API requires admin auth: use service token or admin credentials
   - Verify: user is deleted (GET /api/users/{id} returns 404)
   - If deletion fails: log in SITREP with manual cleanup instructions
```

### Strategy 3: Use Existing Credentials from Environment
Check for test credentials in the environment:
```
- .env.local: ADMIN_PASSWORD, TEST_USER_PASSWORD, QATEST_PASSWORD
- .env: same
- .env.test: same
- secrets.env: same (Docker setups)
```
If found, use them directly without creating a new user.

### Strategy 4: Cookie Injection (for apps with known session format)
If the auth system uses predictable session cookies:
- Generate a valid session cookie via the API (e.g., POST /api/auth/token)
- Inject it into the browser via `browser_evaluate`:
  ```javascript
  document.cookie = "mc_auth=<value>; path=/; httpOnly=false";
  ```
- Navigate to the protected page
- Note: this only works if cookies are not httpOnly or if set via API response

### Strategy 5: Ask the User (last resort)
If no automated strategy works:
```
"I need to test authenticated pages but can't get past the login screen.
Options:
  A) Give me test credentials (I'll clean up after)
  B) Skip authenticated routes (test public pages only)
  C) Create a test user manually and tell me the credentials"
```
This is the ONLY acceptable hang point. Never silently hang on a login screen.

---

## Auth-Aware Route Classification

During Phase 0 or route discovery, classify every route:

| Route Type | Auth Required | Testing Approach |
|-----------|:------------:|-----------------|
| Public pages (/, /about, /pricing) | No | Test directly |
| Login/signup pages | No | Test the auth flow itself |
| Dashboard, settings, admin | Yes | Authenticate first, then test |
| API routes (public) | No | Test via curl |
| API routes (protected) | Yes | Test via service token or session cookie |

**Test public routes first.** If auth setup fails, you still get coverage on the public surface.

---

## Framework-Specific Auth Patterns

| Framework | Signup API | Login API | Session Type |
|-----------|-----------|-----------|-------------|
| NextAuth / Auth.js | Varies (provider-dependent) | POST /api/auth/callback/credentials | JWT or database session |
| Supabase Auth | POST /auth/v1/signup | POST /auth/v1/token?grant_type=password | JWT (access + refresh) |
| Clerk | POST /v1/sign_ups | POST /v1/sign_ins | Clerk session token |
| Lucia | App-defined | App-defined | Database session |
| Custom | POST /api/users or POST /api/auth/token | POST /api/auth/login | Cookie (session) |
| No auth detected | N/A | N/A | Test everything directly |

---

## 2FA Handling

If the app has 2FA enabled (TOTP, SMS, etc.):
1. Create the test user WITHOUT 2FA (if possible via API flags)
2. If 2FA is mandatory: log it as a skip with explanation
3. Never attempt to bypass 2FA - that's a security control, not a testing obstacle

---

## Cleanup Requirements

Per the [Resource Cleanup Protocol](./CLEANUP_PROTOCOL.md), Rule 6a:

- Test users use prefix: `qatest_` (or skill-specific: `redteam_`, `browse_`)
- All created users tracked by ID in state file
- Deleted at end of skill run via API
- Verified deleted (GET returns 404)
- If deletion fails: SITREP includes manual cleanup SQL/API command

---

## Reference in Skills

Add this to any skill that launches a browser:

```markdown
## AUTH GATE PROTOCOL

> Reference: [Auth Gate Protocol](~/.claude/standards/AUTH_GATE_PROTOCOL.md)

When the browser encounters a login screen:
1. Detect the auth gate (URL redirect, login form, 401)
2. Resolve using the priority strategies (service token > API user creation > env credentials > ask user)
3. Track test user for cleanup
4. Proceed with authenticated testing
5. Clean up test user at end of run
```
