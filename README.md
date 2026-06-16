# Loch Haven Lakes

Community incident reporting platform for the Loch Haven chain of lakes in Orlando, Florida.
Live at [lochhavenlakes.org](https://lochhavenlakes.org).

## Infrastructure

| Layer | Service | Notes |
|---|---|---|
| Frontend | [Vercel](https://vercel.com) | Static Astro build, auto-deploys from `main` |
| API | [Cloudflare Workers](https://workers.cloudflare.com) | `lochhavenlakes-api.chrisduffy90.workers.dev` |
| Database | [Neon](https://neon.tech) | Postgres, project: lochhavenlakes |
| Photos | [Cloudflare R2](https://developers.cloudflare.com/r2/) | Bucket: `lochhavenlakes-photos` |
| Domain | Namecheap | DNS pointed at Vercel |

## Data

| Table | What it stores |
|---|---|
| `signups` | Newsletter signups |
| `incident_litter` | Litter/fishing line reports |
| `incident_wildlife` | Wildlife distress reports |
| `incident_water_quality` | Water quality observations |

All incidents are published immediately — no moderation queue. Photos are optional and stored in R2, referenced by URL in the incident row.

## API endpoints

Worker lives at `https://lochhavenlakes-api.chrisduffy90.workers.dev`

| Method | Path | Description |
|---|---|---|
| POST | `/signup` | Newsletter signup |
| POST | `/upload-photo` | Upload photo to R2, returns URL |
| POST | `/report/litter` | Submit litter report |
| POST | `/report/wildlife` | Submit wildlife report |
| POST | `/report/water-quality` | Submit water quality report |
| GET | `/reports` | All incidents (litter, wildlife, water quality) |
| GET | `/photos/:key` | Serve photo from R2 |
| GET | `/health` | Health check |

## Local development

```sh
# Frontend
npm install
npm run dev        # runs at localhost:4321

# Worker (API)
cd worker
npm install
npm run dev        # runs at localhost:8787
```

The Worker reads `worker/.dev.vars` for local secrets (not committed):

```
DATABASE_URL=your_neon_connection_string
```

## Deployment

- **Frontend** — push to `main`, Vercel auto-deploys
- **Worker** — `cd worker && npm run deploy`
