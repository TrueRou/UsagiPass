# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

UsagiPass is a Nuxt 4 application that generates dynamic, scannable DXPASS (player QR codes) for maimai DX arcade game players. It fetches player data from the Leporid backend API and allows customization of backgrounds, frames, and characters. The app includes a MITM proxy to intercept game server requests and redirect them to the UsagiPass frontend.

## Development Commands

### Essential Commands
- `pnpm dev` - Start development server (runs on http://localhost:7200)
- `pnpm build` - Build for production
- `pnpm lint` - Run ESLint
- `pnpm lint:fix` - Fix ESLint issues automatically

### Database Commands
- `pnpm db:generate` - Generate Drizzle database migrations (after modifying [server/database/schema.ts](server/database/schema.ts))
- Apply migrations manually to PostgreSQL after generating

### Documentation
- `pnpm docs:dev` - Run VitePress docs server locally
- `pnpm docs:build` - Build static documentation to `public/docs/`

## Environment Setup

Create a `.env` file based on [`.env.example`](.env.example):

```env
# Database (required)
NUXT_USAGIPASS_DATABASE_URL=postgresql://postgres:password@localhost:5432/usagipass

# MITM Proxy (enabled by default in dev)
NUXT_MITMPROXY_ENABLED=true
NUXT_MITMPROXY_LISTEN_HOST=127.0.0.1
NUXT_MITMPROXY_LISTEN_PORT=7300
```

The app requires PostgreSQL 15+ running locally or accessible via connection string.

## Architecture

### Directory Structure
- `app/` - Frontend Nuxt app (pages, components, composables, stores)
- `server/` - Backend Nitro server (API routes, plugins, database)
- `shared/types/` - TypeScript types shared between client and server
- `docs/` - VitePress documentation
- `public/` - Static assets including ClashMeta proxy config

### Key Backend Files
- [server/database/schema.ts](server/database/schema.ts) - Drizzle ORM schema (user preferences, accounts, ratings, servers)
- [server/plugins/mitmproxy.ts](server/plugins/mitmproxy.ts) - MITM proxy that intercepts game server QR/OAuth requests and redirects to UsagiPass
- [server/api/[...leporid].ts](server/api/[...leporid].ts) - Catch-all proxy to Leporid backend API with automatic token refresh
- [server/api/nuxt/](server/api/nuxt/) - Local API endpoints (auth, profile, wechat callback, servers)

### Key Frontend Files
- [app/app.vue](app/app.vue) - Root component
- [app/pages/index.vue](app/pages/index.vue) - Main DXPASS display page (requires login via [app/middleware/require-login.ts](app/middleware/require-login.ts))
- [app/pages/preference.vue](app/pages/preference.vue) - User settings page
- [app/plugins/api.ts](app/plugins/api.ts) - `$leporid` fetch wrapper that unwraps API responses and shows toasts
- [app/composables/useLeporid.ts](app/composables/useLeporid.ts) - `useLeporid()` composable for API calls

### State Management
- [app/stores/context.ts](app/stores/context.ts) - Runtime context (MAID code, date/time limits)
- [app/stores/notifications.ts](app/stores/notifications.ts) - Toast notifications

### External Services Integration
The app integrates with two external APIs (configured via `NUXT_LEPORID_BASE_URL` and `NUXT_OTOGE_BASE_URL`):
- **Leporid** - Main backend for user profiles, image metadata, and preferences
- **Otoge** - Score fetching service (水鱼/落雪查分器)

## MITM Proxy Development

The proxy listens on `http://127.0.0.1:7300` and intercepts:
1. `wq.sys-all.cn` QR code requests → redirects to UsagiPass with MAID/date/time params
2. `tgk-wcaime.wahlap.com` OAuth callbacks → redirects to `/api/nuxt/wechat/callback`

For development, import `public/UsagiPassDev.yaml` into ClashMeta-compatible proxy software and enable system proxy.

## Code Style

- ESLint config extends `@antfu/eslint-config` with 4-space indentation and single quotes
- JSON/YAML files are ignored by ESLint
- No-console rule is disabled
- Use `nuxt-auth-utils` for session management
- Use `drizzle-orm` for database queries
- Use `$fetch` for HTTP requests (wrapped by `$leporid` plugin)

## Adding New Features

1. **Database changes**: Modify `server/database/schema.ts`, run `pnpm db:generate`, apply SQL migrations
2. **API endpoints**: Add to `server/api/nuxt/` for local logic, or proxy through `[...leporid].ts` for Leporid calls
3. **Frontend components**: Add to `app/components/`, use TailwindCSS + DaisyUI classes
4. **Pages**: Add to `app/pages/` (file-based routing via Nuxt)
