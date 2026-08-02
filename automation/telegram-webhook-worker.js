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

    const resp = await fetch(
      'https://api.github.com/repos/toyobam92/fowl-ai/actions/workflows/telegram-approve.yml/dispatches',
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${env.GH_TOKEN}`,
          Accept: 'application/vnd.github+json',
          'User-Agent': 'fowlai-telegram-webhook',
        },
        body: JSON.stringify({
          ref: 'main',
          inputs: { message_text: text, chat_id: chatId },
        }),
      }
    );
    return new Response(resp.ok ? 'ok' : `dispatch failed: ${resp.status}`, { status: 200 });
  },
};
