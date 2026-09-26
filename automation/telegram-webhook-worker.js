// Relays Telegram messages from @fowlai_bot into a workflow_dispatch of
// telegram-approve.yml.
//
// Auth to GitHub: a GitHub App (secrets APP_ID, APP_INSTALLATION_ID,
// APP_PRIVATE_KEY -- PKCS#8 PEM). The app key never expires; each call mints
// a 1-hour installation token, so there's nothing to rotate. The old
// fine-grained PAT (GH_TOKEN) died silently Sep 14 2026 and cut Telegram off
// for 8 days. GH_TOKEN is only a fallback until the app secrets are set.

let cachedToken = null; // { token, expiresAt } -- survives within an isolate

function b64url(bytes) {
  let s = '';
  for (const b of new Uint8Array(bytes)) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

async function appJwt(env) {
  const der = Uint8Array.from(
    atob(env.APP_PRIVATE_KEY.replace(/-----[^-]+-----/g, '').replace(/\s+/g, '')),
    (c) => c.charCodeAt(0)
  );
  const key = await crypto.subtle.importKey(
    'pkcs8',
    der,
    { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' },
    false,
    ['sign']
  );
  const now = Math.floor(Date.now() / 1000);
  const enc = new TextEncoder();
  const head = b64url(enc.encode(JSON.stringify({ alg: 'RS256', typ: 'JWT' })));
  // iat backdated 60s for clock skew; GitHub caps exp at 10 minutes.
  const body = b64url(enc.encode(JSON.stringify({ iat: now - 60, exp: now + 540, iss: env.APP_ID })));
  const sig = await crypto.subtle.sign('RSASSA-PKCS1-v1_5', key, enc.encode(`${head}.${body}`));
  return `${head}.${body}.${b64url(sig)}`;
}

async function githubToken(env) {
  if (!env.APP_ID || !env.APP_PRIVATE_KEY || !env.APP_INSTALLATION_ID) return env.GH_TOKEN;
  if (cachedToken && cachedToken.expiresAt - Date.now() > 5 * 60 * 1000) return cachedToken.token;
  const resp = await fetch(
    `https://api.github.com/app/installations/${env.APP_INSTALLATION_ID}/access_tokens`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${await appJwt(env)}`,
        Accept: 'application/vnd.github+json',
        'User-Agent': 'fowlai-telegram-webhook',
      },
      // Narrowest token that can dispatch: one repo, Actions only, even if
      // the app installation itself covers more.
      body: JSON.stringify({ repositories: ['fowl-ai'], permissions: { actions: 'write' } }),
    }
  );
  if (!resp.ok) {
    throw new Error(`installation token failed: ${resp.status} ${(await resp.text()).slice(0, 200)}`);
  }
  const data = await resp.json();
  cachedToken = { token: data.token, expiresAt: Date.parse(data.expires_at) };
  return cachedToken.token;
}

export default {
  async fetch(request, env) {
    if (request.method !== 'POST') {
      return new Response('ok', { status: 200 });
    }
    if (request.headers.get('X-Telegram-Bot-Api-Secret-Token') !== env.WEBHOOK_SECRET) {
      return new Response('forbidden', { status: 403 });
    }

    let update;
    try {
      update = await request.json();
    } catch {
      return new Response('ok', { status: 200 }); // not JSON we care about
    }

    const message = update.message;
    const text = message && message.text;
    const chatId = message && message.chat && String(message.chat.id);
    if (!text || !chatId || chatId !== env.TELEGRAM_CHAT_ID) {
      return new Response('ok', { status: 200 }); // ignore silently, no dispatch
    }

    let token;
    try {
      token = await githubToken(env);
    } catch (err) {
      console.error(String(err));
      return new Response('github auth failed', { status: 502 });
    }

    const resp = await fetch(
      'https://api.github.com/repos/toyobam92/fowl-ai/actions/workflows/telegram-approve.yml/dispatches',
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: 'application/vnd.github+json',
          'User-Agent': 'fowlai-telegram-webhook',
        },
        body: JSON.stringify({
          ref: 'main',
          inputs: { message_text: text, chat_id: chatId },
        }),
      }
    );
    // Non-2xx -> 502 so Telegram holds the update and retries, and the
    // failure shows up in getWebhookInfo (telegram-diag.yml) instead of
    // being swallowed like the Sep 14-22 2026 outage.
    if (!resp.ok) {
      const detail = (await resp.text()).slice(0, 200);
      console.error(`dispatch failed: ${resp.status} ${detail}`);
      return new Response(`dispatch failed: ${resp.status}`, { status: 502 });
    }
    return new Response('ok', { status: 200 });
  },
};
