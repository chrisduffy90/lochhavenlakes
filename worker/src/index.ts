import { neon } from '@neondatabase/serverless';

export interface Env {
  DATABASE_URL: string;
  PHOTOS: R2Bucket;
}

const ALLOWED_ORIGINS = [
  'https://lochhavenlakes.org',
  'https://www.lochhavenlakes.org',
  'http://localhost:4321',
];

function corsHeaders(origin: string | null): HeadersInit {
  const allowed = origin && ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    'Access-Control-Allow-Origin': allowed,
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };
}

function json(data: unknown, status = 200, origin: string | null = null): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json', ...corsHeaders(origin) },
  });
}

function isValidEmail(v: unknown): v is string {
  return typeof v === 'string' && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim());
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const origin = request.headers.get('Origin');
    const { pathname } = new URL(request.url);

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders(origin) });
    }

    const sql = neon(env.DATABASE_URL);

    try {
      // GET / or /health
      if (pathname === '/' || pathname === '/health') {
        return json({ ok: true, message: 'Loch Haven Lakes API' }, 200, origin);
      }

      // POST /signup
      if (pathname === '/signup' && request.method === 'POST') {
        const { first_name, last_name = '', email } = await request.json() as Record<string, string>;

        if (!first_name?.trim()) return json({ error: 'First name cannot be empty' }, 400, origin);
        if (!isValidEmail(email)) return json({ error: 'Invalid email address' }, 400, origin);

        try {
          const rows = await sql`
            INSERT INTO signups (first_name, last_name, email)
            VALUES (${first_name.trim()}, ${last_name.trim()}, ${email.trim().toLowerCase()})
            RETURNING *
          `;
          return json({ ok: true, data: rows[0] }, 200, origin);
        } catch (e: unknown) {
          const msg = e instanceof Error ? e.message : '';
          if (msg.includes('unique') || msg.includes('duplicate')) {
            return json({ error: 'This email is already signed up' }, 409, origin);
          }
          throw e;
        }
      }

      // POST /upload-photo
      if (pathname === '/upload-photo' && request.method === 'POST') {
        const formData = await request.formData();
        const file = formData.get('file') as File | null;

        if (!file) return json({ error: 'No file provided' }, 400, origin);

        const ext = file.name.split('.').pop() ?? 'jpg';
        const key = `${Date.now()}-${crypto.randomUUID()}.${ext}`;

        await env.PHOTOS.put(key, file.stream(), {
          httpMetadata: { contentType: file.type },
        });

        const url = `${new URL(request.url).origin}/photos/${key}`;
        return json({ url }, 200, origin);
      }

      // GET /photos/:key — serve photos from R2
      if (pathname.startsWith('/photos/') && request.method === 'GET') {
        const key = pathname.slice('/photos/'.length);
        const object = await env.PHOTOS.get(key);

        if (!object) return new Response('Not found', { status: 404 });

        return new Response(object.body, {
          headers: {
            'Content-Type': object.httpMetadata?.contentType ?? 'application/octet-stream',
            'Cache-Control': 'public, max-age=31536000',
          },
        });
      }

      // POST /report/litter
      if (pathname === '/report/litter' && request.method === 'POST') {
        const data = await request.json() as Record<string, unknown>;
        const rows = await sql`
          INSERT INTO incident_litter (
            lake, incident_date, location_description, location_lat, location_lng,
            description, photo_url, reporter_name, reporter_email, status
          ) VALUES (
            ${data.lake}, ${data.incident_date ?? null}, ${data.location_description},
            ${data.location_lat ?? null}, ${data.location_lng ?? null},
            ${data.description}, ${data.photo_url ?? null},
            ${data.reporter_name ?? null}, ${data.reporter_email ?? null},
            'published'
          ) RETURNING *
        `;
        return json(rows[0], 200, origin);
      }

      // POST /report/wildlife
      if (pathname === '/report/wildlife' && request.method === 'POST') {
        const data = await request.json() as Record<string, unknown>;
        const rows = await sql`
          INSERT INTO incident_wildlife (
            lake, incident_date, location_description, location_lat, location_lng,
            description, photo_url, reporter_name, reporter_email, status,
            species, condition
          ) VALUES (
            ${data.lake}, ${data.incident_date ?? null}, ${data.location_description},
            ${data.location_lat ?? null}, ${data.location_lng ?? null},
            ${data.description}, ${data.photo_url ?? null},
            ${data.reporter_name ?? null}, ${data.reporter_email ?? null},
            'published',
            ${data.species ?? null}, ${data.condition}
          ) RETURNING *
        `;
        return json(rows[0], 200, origin);
      }

      // POST /report/water-quality
      if (pathname === '/report/water-quality' && request.method === 'POST') {
        const data = await request.json() as Record<string, unknown>;
        const rows = await sql`
          INSERT INTO incident_water_quality (
            lake, incident_date, location_description, location_lat, location_lng,
            description, photo_url, reporter_name, reporter_email, status,
            observation_type
          ) VALUES (
            ${data.lake}, ${data.incident_date ?? null}, ${data.location_description},
            ${data.location_lat ?? null}, ${data.location_lng ?? null},
            ${data.description}, ${data.photo_url ?? null},
            ${data.reporter_name ?? null}, ${data.reporter_email ?? null},
            'published',
            ${data.observation_type}
          ) RETURNING *
        `;
        return json(rows[0], 200, origin);
      }

      // GET /reports
      if (pathname === '/reports' && request.method === 'GET') {
        const [litter, wildlife, water] = await Promise.all([
          sql`SELECT * FROM incident_litter ORDER BY created_at DESC`,
          sql`SELECT * FROM incident_wildlife ORDER BY created_at DESC`,
          sql`SELECT * FROM incident_water_quality ORDER BY created_at DESC`,
        ]);
        return json({ litter, wildlife, water_quality: water }, 200, origin);
      }

      return json({ error: 'Not found' }, 404, origin);
    } catch (e) {
      console.error(e);
      return json({ error: 'Something went wrong' }, 500, origin);
    }
  },
};
