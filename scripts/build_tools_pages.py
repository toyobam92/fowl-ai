"""Generate /tools/, /tools/job-agent/ and /tools/developers/ for the FOWL AI site."""
import html, json, sys
from pathlib import Path

SITE = Path.home() / "fowl-ai"
TOOLS = json.loads(Path(sys.argv[1]).read_text())
ENDPOINT = "https://tools.fowl-ai.com/job-agent/mcp"
LINK = "https://tools.fowl-ai.com/job-agent/u/&lt;your key&gt;/mcp"
START = "https://tools.fowl-ai.com/start"
e = html.escape

def head(title, desc, path):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-1K9HKRJ6ZV"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-1K9HKRJ6ZV');
  </script>
  <script src="/analytics-events.js" defer></script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}">
  <meta property="og:title" content="{e(title)}" />
  <meta property="og:description" content="{e(desc)}" />
  <meta property="og:url" content="https://www.fowl-ai.com{path}" />
  <meta property="og:image" content="https://www.fowl-ai.com/og-image.png" />
  <link rel="canonical" href="https://www.fowl-ai.com{path}">
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="stylesheet" href="/assets/site.css">
  <link rel="stylesheet" href="/tools/tools.css">
  <script src="/assets/site.js" defer></script>
  <meta name="theme-color" content="#185b42">
</head>
<body class="fowl-interior">
  <a class="skip-link" href="#main-content">Skip to content</a>
<header class="site-header">
  <nav class="site-nav" aria-label="Main navigation">
    <a class="site-brand" href="/" aria-label="FOWL AI home"><span class="site-brand-mark" aria-hidden="true"></span>FOWL<span class="ai">AI</span></a>
    <div class="site-nav-links" id="site-navigation">
      <a href="/issues/">The briefing</a><a href="/jobs/">AI jobs</a><a href="/platforms/">Platforms</a><a href="/tools/"{' aria-current="page"' if path.startswith('/tools/') else ''}>Tools</a><a href="/vibe-code-saturdays/" data-conversion="vibe-code" data-link-location="navigation">Vibe Code Saturdays</a>
      <details class="site-more"><summary>Explore</summary><div class="site-more-menu"><a href="/tests/">AI tool tests</a><a href="/glossary/">AI glossary</a><a href="/about/">About FOWL AI</a><a href="/faq/">FAQs</a></div></details>
    </div>
    <a class="site-nav-cta" href="/#signup" data-conversion="newsletter" data-link-location="navigation-cta">Subscribe free <span aria-hidden="true">↗</span></a>
    <button class="site-menu-toggle" type="button" aria-label="Open navigation" aria-controls="site-navigation" aria-expanded="false"><span></span><span></span></button>
  </nav>
</header>
<main id="main-content">
"""

FOOT = """</main>
<footer class="site-footer"><div class="site-footer-inner">
  <div class="site-footer-top">
    <div class="site-footer-about"><a class="site-brand" href="/" aria-label="FOWL AI home"><span class="site-brand-mark" aria-hidden="true"></span>FOWL<span class="ai">AI</span></a><p>A clearer view of AI.<br>A smarter next move.</p></div>
    <div class="site-footer-column"><h2>Discover</h2><a href="/issues/">The briefing</a><a href="/jobs/">AI jobs</a><a href="/platforms/">AI platforms</a><a href="/tests/">AI tool tests</a></div>
    <div class="site-footer-column"><h2>Go further</h2><a href="/tools/">Tools</a><a href="/tools/developers/">For developers</a><a href="/vibe-code-saturdays/" data-conversion="vibe-code" data-link-location="footer">Vibe Code Saturdays</a><a href="/glossary/">AI glossary</a></div>
    <div class="site-footer-column"><h2>Stay curious</h2><a href="/about/">About FOWL AI</a><a href="/faq/">FAQs</a><a href="/contact/">Get in touch</a><a href="https://www.instagram.com/fowlai/" target="_blank" rel="noopener noreferrer">Instagram ↗</a></div>
  </div>
  <div class="site-footer-bottom"><span>© 2026 FOWL AI · Future of Work Lab</span><div><a href="/privacy/">Privacy</a><a href="/feed.xml">RSS</a><a href="https://toyosibamidele.com" target="_blank" rel="noopener noreferrer">Made by TYB ↗</a></div></div>
</div></footer>
</body>
</html>
"""

ASSISTANTS = ["Claude", "ChatGPT", "Grok", "Meta Muse", "Claude Code", "Any MCP app"]

# ---------- /tools/ ----------
hub = head("AI Tools That Plug Into Any Assistant | FOWL AI",
           "FOWL AI tools connect to Claude, ChatGPT, Grok and Meta Muse through MCP. Add one link and your assistant can do the work.",
           "/tools/") + f"""
  <section class="tl-hero"><div class="tl-wrap">
    <p class="tl-kicker">FOWL AI · Tools</p>
    <h1>Tools your AI can <em>use</em>, not just talk about.</h1>
    <p>Each FOWL AI tool is an MCP connector. Add one link to the assistant you already use, and it can do real work for you: search, fill in, track, follow up.</p>
    <div class="tl-actions"><a class="tl-btn gold" href="/tools/job-agent/">See the Job Agent</a><a class="tl-btn ghost" href="/tools/developers/">For developers</a></div>
  </div></section>

  <section class="tl-section"><div class="tl-wrap">
    <h2>Works where you already are</h2>
    <p class="tl-lede">MCP is the standard way AI assistants connect to tools. One FOWL AI link works in each of these.</p>
    <ul class="tl-chips">{''.join(f'<li>{a}</li>' for a in ASSISTANTS)}</ul>
  </div></section>

  <section class="tl-section alt"><div class="tl-wrap">
    <h2>The tools</h2>
    <p class="tl-lede">Built and tested in Atlanta, then taught live at Vibe Code Saturdays.</p>
    <div class="tl-grid">
      <a class="tl-card" href="/tools/job-agent/" style="text-decoration:none;color:inherit">
        <span class="tl-tag">New</span>
        <h3>Job Agent</h3>
        <p>Give it your resume once. Every morning it finds jobs that fit, writes a resume for each one, fills in the application, and asks you on Telegram before it sends.</p>
        <p style="color:var(--fowl-green);font-weight:600">See how it works →</p>
      </a>
      <div class="tl-card">
        <span class="tl-tag">Live</span>
        <h3>Brand Brain</h3>
        <p>Your brand's memory: voice, colors, audience and offers. Every AI that connects to it makes work that sounds like you.</p>
        <p><a href="https://brain.fowl-ai.com/?utm_source=tools" style="color:var(--fowl-green);font-weight:600">Open Brand Brain →</a></p>
      </div>
      <div class="tl-card" style="border-style:dashed;background:transparent">
        <h3>More on the way</h3>
        <p>New tools are added here as they're built. Subscribe to the briefing to hear first.</p>
        <p><a href="/#signup" style="color:var(--fowl-green);font-weight:600" data-conversion="newsletter" data-link-location="tools-hub">Subscribe free →</a></p>
      </div>
    </div>
  </div></section>
""" + FOOT

# ---------- /tools/job-agent/ ----------
steps = [("Give it your resume", "Paste it or attach the file. It fills in your details and work history."),
         ("Answer a few questions once", "Jobs you want, where you'll work, pay, work authorization. Each one is a tap."),
         ("Connect Telegram (optional)", "Say \"Connect Telegram\", tap your own link and press Start. Steps below."),
         ("It finds jobs that fit", "New openings on company job boards, at your level, without duplicates. Run it any time."),
         ("You pick from a short list", "Up to 10 jobs, each with a match score, why you fit and the honest gap. Pursue or Pass."),
         ("It writes a resume for each one", "Tailored from your real experience, saved per job with a note on what changed. It never invents."),
         ("One click fills the form, you press Submit", "Open today's applications on your computer, click Fill with Job Agent, check it, submit."),
         ("You keep a copy of what you sent", "Every job, its stage, dates and the exact answers you sent, on your job search page.")]
stages = [("On your shortlist", "#fef3c7"), ("Ready: press Submit", "#fde68a"), ("Applied", "#c7d2fe"), ("Interviewing", "#bbf7d0"), ("Offer", "#4ade80"), ("Not moving forward", "#fecaca")]
ja = head("Job Agent: Your AI Applies to Jobs for You | FOWL AI",
          "Give it your resume once. It finds jobs that fit, tailors your resume for each one and fills in the application in one click. You press Submit. Works in Claude, ChatGPT, Grok and Meta Muse.",
          "/tools/job-agent/") + f"""
  <section class="tl-hero"><div class="tl-wrap">
    <p class="tl-kicker">FOWL AI Tools · Job Agent</p>
    <h1>Set it up once. <em>Apply in minutes.</em></h1>
    <p>Your AI job search assistant, inside the AI you already use. Drop your resume in once. It finds roles that fit, writes a resume for each one you pick and fills in the application in one click. You check it and press Submit. Free.</p>
    <div class="tl-actions"><a class="tl-btn gold" href="https://tools.fowl-ai.com/start" data-link-location="job-agent-hero">Get started</a><a class="tl-btn ghost" href="#how">How it works</a></div>
  </div></section>

  <section class="tl-section" id="how"><div class="tl-wrap">
    <h2>How it works</h2>
    <p class="tl-lede">About 10 minutes to set up. After that, about a minute per application. Focused: around 5 strong applications a day, not 100.</p>
    <ol class="tl-steps">{''.join(f'<li><span><b>{e(t)}</b>{e(d)}</span></li>' for t, d in steps)}</ol>
  </div></section>

  <section class="tl-section" id="watch" style="border-top:1px solid var(--fowl-line)"><div class="tl-wrap">
    <h2>See it work</h2>
    <p class="tl-lede">A sample applicant, Maya, on real job forms. Nothing was sent. Tap a video to play it with sound.</p>
    <div class="tl-vids">
      <figure class="tl-vid"><video controls playsinline preload="none" crossorigin="anonymous" poster="https://tools.fowl-ai.com/media/job-agent/06-shortlist.jpg" aria-label="Real matches, you choose"><source src="https://tools.fowl-ai.com/media/job-agent/06-shortlist.mp4" type="video/mp4"><track kind="captions" src="https://tools.fowl-ai.com/media/job-agent/06-shortlist.vtt" srclang="en" label="English"></video><figcaption><b>Real matches, you choose</b>It searches, scores every job against your resume, and you Pursue or Pass.</figcaption></figure>
      <figure class="tl-vid"><video controls playsinline preload="none" crossorigin="anonymous" poster="https://tools.fowl-ai.com/media/job-agent/07-resume.jpg" aria-label="A resume for each job"><source src="https://tools.fowl-ai.com/media/job-agent/07-resume.mp4" type="video/mp4"><track kind="captions" src="https://tools.fowl-ai.com/media/job-agent/07-resume.vtt" srclang="en" label="English"></video><figcaption><b>A resume for each job</b>Built from your real experience, with a note on what changed.</figcaption></figure>
      <figure class="tl-vid"><video controls playsinline preload="none" crossorigin="anonymous" poster="https://tools.fowl-ai.com/media/job-agent/08-fill.jpg" aria-label="One click fills it, you press Submit"><source src="https://tools.fowl-ai.com/media/job-agent/08-fill.mp4" type="video/mp4"><track kind="captions" src="https://tools.fowl-ai.com/media/job-agent/08-fill.vtt" srclang="en" label="English"></video><figcaption><b>One click fills it, you press Submit</b>Review every answer first, and keep a copy of what you sent.</figcaption></figure>
      <figure class="tl-vid"><video controls playsinline preload="none" crossorigin="anonymous" poster="https://tools.fowl-ai.com/media/job-agent/09-tracker.jpg" aria-label="Your whole job search on one page"><source src="https://tools.fowl-ai.com/media/job-agent/09-tracker.mp4" type="video/mp4"><track kind="captions" src="https://tools.fowl-ai.com/media/job-agent/09-tracker.vtt" srclang="en" label="English"></video><figcaption><b>Your whole job search on one page</b>Every job, its stage, dates and the resume made for it.</figcaption></figure>
      <figure class="tl-vid"><video controls playsinline preload="none" crossorigin="anonymous" poster="https://tools.fowl-ai.com/media/job-agent/10-telegram-mode.jpg" aria-label="Telegram mode"><source src="https://tools.fowl-ai.com/media/job-agent/10-telegram-mode.mp4" type="video/mp4"><track kind="captions" src="https://tools.fowl-ai.com/media/job-agent/10-telegram-mode.vtt" srclang="en" label="English"></video><figcaption><b>Telegram mode</b>Approve on your phone, finish at your computer.</figcaption></figure>
    </div>
  </div></section>

  <section class="tl-section alt"><div class="tl-wrap">
    <h2>Two ways to run it</h2>
    <p class="tl-lede">Start guided. Switch to Autonomous once you trust its picks.</p>
    <div class="tl-grid">
      <div class="tl-card"><span class="tl-tag">Guided (Telegram mode)</span><h3>You pick, it prepares, you submit</h3><p>Your shortlist and reminders arrive on Telegram. On your computer, one link opens today's applications: one click fills each form, you press Submit.</p></div>
      <div class="tl-card"><span class="tl-tag">Autonomous mode</span><h3>It applies within your limits</h3><p>On sites that allow it, it applies on its own to strong matches, up to your daily limit. When a site asks for a person at Submit (an emailed code), it sends you an Open &amp; fill button instead.</p></div>
    </div>
  </div></section>

  <section class="tl-section"><div class="tl-wrap">
    <h2 id="connect">Add it in under a minute</h2>
    <p class="tl-lede">Your assistant does the thinking and the Job Agent hands it one task at a time. No downloads, no API keys.</p>
    <ol class="tl-steps">
      <li><span><b>Pick your assistant</b>Claude, ChatGPT, Claude Code, Grok or Meta Muse. Each has its own two-minute guide.</span></li>
      <li><span><b>Sign in once</b>Continue with Google, or your email and a code. One free account for every FOWL AI tool.</span></li>
      <li><span><b>Say "Start my job agent"</b>It takes it from there.</span></li>
    </ol>
    <div class="tl-actions" style="display:flex;gap:12px;flex-wrap:wrap;margin-top:24px"><a class="tl-btn green" href="https://tools.fowl-ai.com/start" data-link-location="job-agent-connect">Get started</a><a class="tl-btn" style="border-color:var(--fowl-line);color:var(--fowl-ink)" href="https://tools.fowl-ai.com/account">Your account</a></div>
    <ul class="tl-chips" style="margin-top:22px">{''.join(f'<li>{a}</li>' for a in ASSISTANTS)}</ul>
  </div></section>

  <section class="tl-section" id="telegram" style="border-top:1px solid var(--fowl-line)"><div class="tl-wrap">
    <h2>Connect Telegram (optional, 1 minute)</h2>
    <p class="tl-lede">Telegram is where your shortlist, reminders and "your turn" alerts arrive on your phone. Skip it and you approve everything in chat instead.</p>
    <ol class="tl-steps">
      <li><span><b>Get Telegram</b>Free on the App Store, Google Play or telegram.org. Sign up with your phone number. Already have it? Skip this.</span></li>
      <li><span><b>In your assistant, say "Connect Telegram"</b>The Job Agent replies with your own link. It starts with t.me/FowlJobAgentBot and is only for you.</span></li>
      <li><span><b>Tap the link, then tap Start</b>Telegram opens the FOWL Job Agent bot. It replies that you're connected.</span></li>
      <li><span><b>Back in chat, say "done"</b>You get a test message on Telegram. That's it.</span></li>
    </ol>
    <p class="tl-note">What you'll get there: your shortlist to Pursue or Pass, a morning nudge when new jobs are in, an "Open &amp; fill" button when an application needs you, and follow-up reminders. We never message anyone else for you.</p>
  </div></section>

  <section class="tl-section alt"><div class="tl-wrap">
    <h2>Your tracker, always up to date</h2>
    <p class="tl-lede">Every job in one place: stage, match, dates, the resume made for it and a copy of exactly what you sent. Connect Gmail in your assistant and it moves jobs along from recruiter replies.</p>
    <p>{''.join(f'<span class="tl-stage" style="background:{c};margin:0 8px 8px 0">{e(s)}</span>' for s, c in stages)}</p>
  </div></section>

  <section class="tl-section"><div class="tl-wrap">
    <h2>Rules it never breaks</h2>
    <div class="tl-grid">
      <div class="tl-card"><h3>Never invents</h3><p>No made-up experience, numbers, titles or skills. It only reorders and rewords what's on your resume.</p></div>
      <div class="tl-card"><h3>Never guesses</h3><p>If a form asks something your setup doesn't cover, that job comes to you instead.</p></div>
      <div class="tl-card"><h3>Private by default</h3><p>Voluntary self-ID questions answer "I don't wish to answer" unless you choose to share.</p></div>
      <div class="tl-card"><h3>You press Submit</h3><p>You see every answer before it goes. It never solves a "confirm you're human" check for you, and it never applies to your current employer or companies you block.</p></div>
    </div>
  </div></section>

  <section class="tl-section alt"><div class="tl-wrap">
    <h2>Set up your AI job search agent in an hour</h2>
    <p class="tl-lede">A free live session, online, on a Thursday or Friday evening. Bring your resume and laptop. Leave with an agent applying for you.</p>
    <div class="tl-actions" style="display:flex;gap:12px;flex-wrap:wrap"><a class="tl-btn green" href="/tools/job-agent/session/" data-link-location="job-agent-session">Save my free seat</a><a class="tl-btn" style="border-color:var(--fowl-line);color:var(--fowl-ink)" href="https://tools.fowl-ai.com/start" data-link-location="job-agent-session-start">Set it up now</a></div>
    <p class="tl-note">Developers: the connector and every tool are documented on the <a href="/tools/developers/" style="color:var(--fowl-green)">developers page</a>.</p>
  </div></section>
""" + FOOT

# ---------- /tools/developers/ ----------
def params(p):
    if not p:
        return '<span style="color:var(--fowl-muted)">none</span>'
    return ", ".join(f'<code>{e(x["name"])}</code>' + ("" if x["required"] else '<span style="color:var(--fowl-muted)">?</span>') for x in p)

rows = "".join(f'<tr><td><code>{e(t["name"])}</code></td><td>{params(t["params"])}</td><td>{e(t["desc"])}</td></tr>' for t in TOOLS)
clients = [("Claude (claude.ai, Desktop, mobile)", f"Settings → Connectors → Add custom connector. Paste <code>{ENDPOINT}</code>, press Connect, sign in."),
           ("Claude Code", f"claude mcp add --transport http job-agent {ENDPOINT} then /mcp to sign in."),
           ("ChatGPT", f"Settings → Apps &amp; Connectors → Advanced → Developer mode → Create. Paste <code>{ENDPOINT}</code>, authentication OAuth."),
           ("Grok", f"Add a remote MCP server: <code>{ENDPOINT}</code> with header <code>Authorization: Bearer &lt;key&gt;</code>, or the private link."),
           ("Meta Muse", f"Add an MCP connector: <code>{ENDPOINT}</code> with the key as API key, or the private link."),
           ("Anything else", "Any client that speaks MCP over streamable HTTP. Use the private link, or the endpoint plus a Bearer header.")]
dev = head("Developers: FOWL AI MCP Tools | FOWL AI",
           "Endpoints, authentication and the full tool reference for FOWL AI's MCP tools, starting with the Job Agent.",
           "/tools/developers/") + f"""
  <section class="tl-hero"><div class="tl-wrap">
    <p class="tl-kicker">FOWL AI Tools · Developers</p>
    <h1>One standard. <em>Any assistant.</em></h1>
    <p>Every FOWL AI tool is a remote MCP server over streamable HTTP. Each tool lives at its own path on <code style="background:#eef3ef;color:var(--fowl-ink)">tools.fowl-ai.com</code>, carries its own instructions, and uses the same sign-in.</p>
  </div></section>

  <section class="tl-section"><div class="tl-wrap">
    <h2>Connecting</h2>
    <p class="tl-lede">One FOWL AI Tools account works for every tool. Clients that support MCP sign-in use it; others use a personal key.</p>
    <div class="tl-grid">
      <div class="tl-card"><h3>Sign in (recommended)</h3><p>Standard MCP authorization: OAuth 2.1 with PKCE and dynamic client registration. The user signs in with an emailed code. Tokens last 30 days and refresh.</p><div class="tl-code">{ENDPOINT}
# 401 -> /.well-known/oauth-protected-resource/job-agent/mcp
# issuer: https://tools.fowl-ai.com</div></div>
      <div class="tl-card"><h3>Endpoint plus key</h3><p>For clients that can send headers.</p><div class="tl-code">POST {ENDPOINT}
Authorization: Bearer ja_xxxxxxxx
# or  x-api-key: ja_xxxxxxxx</div></div>
      <div class="tl-card"><h3>Private link</h3><p>For clients that only take a URL. Treat it like a password.</p><div class="tl-code">{LINK}</div></div>
    </div>
    <p class="tl-note">Keys are made on the <a href="https://tools.fowl-ai.com/account" style="color:var(--fowl-green)">account page</a> and are stored only as a hash. Name each key, and revoke any one without affecting the others. Tool results that point to files (tailored resumes, screenshots, the tracker) return private download links.</p>
  </div></section>

  <section class="tl-section alt"><div class="tl-wrap">
    <h2>Client setup</h2>
    <div class="tl-scroll"><table class="tl-table"><thead><tr><th>Client</th><th>How</th></tr></thead><tbody>
      {''.join(f'<tr><td><b>{c}</b></td><td>{h}</td></tr>' for c, h in clients)}
    </tbody></table></div>
    <p class="tl-note">Menu names change often. Look for connectors, MCP, tools or integrations.</p>
  </div></section>

  <section class="tl-section"><div class="tl-wrap">
    <h2>Job Agent: tool reference</h2>
    <p class="tl-lede">{len(TOOLS)} tools. The whole flow is one loop: <code>start_here</code> once, then <code>next_task</code> until it returns <code>done</code>. Each task carries its own instructions and data (resume text, the posting, the questions to ask), so any assistant can follow it. The other tools are what the tasks tell it to call. Parameters marked ? are optional.</p>
    <div class="tl-scroll"><table class="tl-table"><thead><tr><th>Tool</th><th>Parameters</th><th>What it does</th></tr></thead><tbody>{rows}</tbody></table></div>
  </div></section>

  <section class="tl-section alt"><div class="tl-wrap">
    <h2>Behavior you can rely on</h2>
    <div class="tl-grid">
      <div class="tl-card"><h3>The assistant is the brain</h3><p>No model runs on the server and no API keys are needed. The connected assistant reads, asks and writes; the server stores, searches, fills, tracks and messages Telegram.</p></div>
      <div class="tl-card"><h3>Safe previews</h3><p><code>fill_application</code> never submits. Practice runs use a local copy of the exact form; previews block every outgoing request.</p></div>
      <div class="tl-card"><h3>Explicit approval</h3><p><code>submit_application</code> refuses without <code>user_approved</code> unless the user chose autonomous mode, and stops at the daily cap.</p></div>
      <div class="tl-card"><h3>Plain errors</h3><p>Errors come back as tool results with a plain reason the assistant can relay, like a missing key or an unanswered question.</p></div>
    </div>
    <p class="tl-note">Want to build on FOWL AI tools or suggest one? <a href="/contact/?topic=developers" style="color:var(--fowl-green)">Get in touch</a>.</p>
  </div></section>
""" + FOOT

for path, page in [("tools/index.html", hub), ("tools/job-agent/index.html", ja), ("tools/developers/index.html", dev)]:
    (SITE / path).write_text(page)
    assert "—" not in page.replace("<!--", ""), f"em dash in {path}"
print("written")

# ---------- /tools/job-agent/session/ (free live session sign-up) ----------
SESSION_CSS = """<style>
.ss-hero{background:linear-gradient(#fff 55%,var(--fowl-paper));color:var(--fowl-ink);padding:64px 24px 72px;border-bottom:1px solid var(--fowl-line)}
.ss-hero .tl-wrap{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,.75fr);gap:40px;align-items:center}
@media(max-width:860px){.ss-hero .tl-wrap{grid-template-columns:1fr}}
.ss-badges{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 18px}
.ss-badges span{font:550 12px var(--fowl-font);letter-spacing:.2px;padding:7px 12px;border-radius:999px;border:1px solid #e1e8dc;background:#f7faf4;color:#4d674e}
.ss-badges span.free{background:var(--fowl-green);color:#fff;border-color:var(--fowl-green)}
.ss-hero h1{font-family:var(--fowl-font)!important;font-weight:650;font-size:clamp(40px,6vw,68px);line-height:1.03;margin:0 0 18px;letter-spacing:-.055em;color:var(--fowl-ink);text-wrap:balance}
.ss-hero h1 em{font-style:normal;color:var(--fowl-green);display:block}
.ss-hero p.lede{font-size:19px;line-height:1.6;color:var(--fowl-muted);max-width:56ch;margin:0}
.ss-ticket{background:#fff;color:var(--fowl-ink);border:1px solid var(--fowl-line);border-radius:20px;padding:24px;box-shadow:0 24px 60px rgba(13,63,49,.10);position:relative}
.ss-ticket:before,.ss-ticket:after{content:"";position:absolute;left:-12px;top:52%;width:24px;height:24px;border-radius:50%;background:var(--fowl-paper);border:1px solid var(--fowl-line)}
.ss-ticket:after{left:auto;right:-12px}
.ss-ticket .k{font:650 11px var(--fowl-font);letter-spacing:1.5px;text-transform:uppercase;color:#638058}
.ss-ticket b.t{display:block;font:650 24px/1.15 var(--fowl-font);letter-spacing:-.035em;margin:8px 0 14px}
.ss-ticket dl{display:grid;grid-template-columns:auto 1fr;gap:8px 14px;margin:0;font-size:15px;border-top:1px dashed #cfd9d1;padding-top:14px}
.ss-ticket dt{color:#647169} .ss-ticket dd{margin:0;font-weight:600}
.ss-out{counter-reset:o;list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,180px),1fr));gap:14px}
.ss-out li{counter-increment:o;background:#fff;border:1px solid var(--fowl-line);border-radius:16px;padding:18px}
.ss-out li:before{content:counter(o,decimal-leading-zero);display:block;font:650 12px var(--fowl-font);letter-spacing:1px;color:#638058;margin-bottom:8px}
.ss-out b{display:block;font-size:16px;margin-bottom:4px}
.ss-out span{color:var(--fowl-muted);font-size:14.5px}
.ss-form *{box-sizing:border-box}
.ss-form{background:#fff;border:1px solid var(--fowl-line);border-radius:22px;padding:28px;max-width:640px;box-shadow:0 20px 50px rgba(13,63,49,.08)}
.ss-form label.f{display:block;font-weight:600;font-size:14px;margin:16px 0 6px}
.ss-form input[type=text],.ss-form input[type=email],.ss-form select{width:100%;font:inherit;font-size:16px;padding:13px 14px;border:1px solid #c9d2cb;border-radius:12px;background:#fff}
.ss-days{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
@media(max-width:520px){.ss-days{grid-template-columns:1fr}}
.ss-days label{border:1px solid #c9d2cb;border-radius:12px;padding:12px;min-height:48px;cursor:pointer;display:flex;gap:8px;align-items:center;font-size:15px}
.ss-days input{accent-color:#185b42}
.ss-days label:has(input:checked){border-color:#185b42;background:#eef6f0;font-weight:600}
.ss-submit{display:flex;align-items:center;justify-content:center;width:100%;min-height:54px;margin-top:22px;border:0;border-radius:999px;background:var(--fowl-green);color:#fff;font:650 17px var(--fowl-font);cursor:pointer}
.ss-submit:hover{background:#124a35}.ss-submit:active{transform:scale(.98)}
.ss-trap{position:absolute;left:-10000px;width:1px;height:1px;overflow:hidden}
.ss-err{background:#fdecec;color:#8a1c1c;border-radius:12px;padding:12px 14px;font-size:14px}
.ss-faq details{border-bottom:1px solid var(--fowl-line);padding:14px 0} .ss-faq summary{cursor:pointer;font-weight:650;font-size:16px}
.ss-faq p{color:var(--fowl-muted);margin:8px 0 0}
input:focus-visible,select:focus-visible,.ss-submit:focus-visible,summary:focus-visible{outline:3px solid #8fc9a8;outline-offset:2px}
</style>"""

session = head("Free Live Session: Set Up Your AI Job Search Agent in One Hour | FOWL AI",
               "Looking for a job? Take the driver's seat. In one free hour, set up an AI job search agent in the AI you already use: Claude, ChatGPT, Grok or Meta Muse.",
               "/tools/job-agent/session/") + SESSION_CSS + """
  <section class="ss-hero"><div class="tl-wrap">
    <div>
      <div class="ss-badges"><span class="free">Free</span><span>Live online</span><span>1 hour</span><span>No coding</span></div>
      <h1>Looking for a job? <em>Take the driver's seat.</em></h1>
      <p class="lede">Stop relying on a dozen job apps. In one hour, set up your own AI job search agent inside the AI you already use. If you have Claude, ChatGPT or another AI tool, this is a very simple process.</p>
      <div class="tl-actions" style="margin-top:28px"><a class="tl-btn gold" href="#signup" data-link-location="session-hero">Save my free seat</a><a class="tl-btn ghost" href="/tools/job-agent/">What's the Job Agent?</a></div>
    </div>
    <aside class="ss-ticket" aria-label="Session details">
      <span class="k">FOWL AI · Live session</span>
      <b class="t">Set up your AI job search agent in one hour</b>
      <dl><dt>When</dt><dd>Thursday or Friday evening, date coming soon</dd><dt>Where</dt><dd>Online, on Zoom</dd>
      <dt>Cost</dt><dd>Free, and the tools are free too</dd><dt>Bring</dt><dd>Your laptop and your resume</dd></dl>
    </aside>
  </div></section>

  <section class="tl-section"><div class="tl-wrap">
    <h2>In one hour, you'll</h2>
    <p class="tl-lede">We do it together, step by step. You leave with an agent that's already working for you.</p>
    <ol class="ss-out">
      <li><b>Connect the Job Agent</b><span>to Claude, ChatGPT, Grok or Muse. Two minutes, no downloads.</span></li>
      <li><b>Load your resume</b><span>and answer eight quick questions by tapping, not typing.</span></li>
      <li><b>See your first matches</b><span>each with a resume tailored to that job and the application filled in.</span></li>
      <li><b>Choose how it runs</b><span>approve each job on Telegram, or review it all in chat. You see every answer before you press Submit.</span></li>
      <li><b>Leave with a tracker</b><span>every job, its stage and when to follow up, updated for you.</span></li>
    </ol>
  </div></section>

  <section class="tl-section alt"><div class="tl-wrap">
    <h2>You stay in control</h2>
    <div class="tl-grid">
      <div class="tl-card"><h3>Your AI, your choice</h3><p>Use the assistant you already like. Out of messages in one? Switch to another and pick up right where you left off.</p></div>
      <div class="tl-card"><h3>Everything stays with you</h3><p>Your profile, resumes and tracker live in your own FOWL AI account, not inside one app.</p></div>
      <div class="tl-card"><h3>Nothing sent without your yes</h3><p>Every application waits for your tap, unless you choose Autonomous mode yourself.</p></div>
      <div class="tl-card"><h3>Never invents anything</h3><p>It only reorders and rewords what's true on your resume. No made-up experience.</p></div>
    </div>
  </div></section>

  <section class="tl-section" id="signup"><div class="tl-wrap">
    <h2>Save your free seat</h2>
    <p class="tl-lede">We're picking between a Thursday and a Friday evening. Tell us what works and we'll email you the date and Zoom link.</p>
    <form class="ss-form" method="post" action="https://tools.fowl-ai.com/sessions/signup">
      <p class="ss-err" id="ss-err" hidden>Please add your name and a valid email.</p>
      <label class="f" for="ss-name">Your name</label><input type="text" id="ss-name" name="name" required autocomplete="name" placeholder="Jordan Lee">
      <label class="f" for="ss-email">Email</label><input type="email" id="ss-email" name="email" required autocomplete="email" placeholder="you@email.com">
      <span class="f" style="display:block;font-weight:600;font-size:14px;margin:16px 0 6px">Which evening works?</span>
      <div class="ss-days" role="radiogroup" aria-label="Which evening works">
        <label><input type="radio" name="day" value="thursday"> Thursday</label>
        <label><input type="radio" name="day" value="friday"> Friday</label>
        <label><input type="radio" name="day" value="either" checked> Either works</label>
      </div>
      <label class="f" for="ss-ai">Which AI do you use?</label>
      <select id="ss-ai" name="assistant"><option>Claude</option><option>ChatGPT</option><option>Grok</option><option>Meta Muse</option><option>More than one</option><option value="None yet">None yet (we'll help)</option></select>
      <label class="f" for="ss-sit">Where are you in your search?</label>
      <select id="ss-sit" name="situation"><option>Employed, looking quietly</option><option>Between jobs</option><option>Student or new grad</option><option>Changing careers</option><option>Just curious</option></select>
      <div class="ss-trap" aria-hidden="true"><label>Leave this empty<input name="leave_empty_hp" tabindex="-1" autocomplete="off"></label></div>
      <button class="ss-submit" type="submit">Save my free seat</button>
      <p class="tl-note" style="text-align:center">Free. We'll only email you about this session.</p>
    </form>
  </div></section>

  <section class="tl-section alt"><div class="tl-wrap">
    <h2>Questions</h2>
    <div class="ss-faq" style="max-width:760px">
      <details><summary>Is it really free?</summary><p>Yes. The session is free and the FOWL AI tools are free.</p></details>
      <details><summary>Do I need to know how to code?</summary><p>No. You'll copy one address, sign in, and tap through a few questions.</p></details>
      <details><summary>What do I need?</summary><p>A laptop, your latest resume, and Claude, ChatGPT, Grok or Meta Muse. A free account works. No AI yet? Pick "None yet" and we'll help you start.</p></details>
      <details><summary>Can I set it up before the session?</summary><p>Yes, at <a href="https://tools.fowl-ai.com/start" style="color:var(--fowl-green)">tools.fowl-ai.com/start</a>. Come to the session to get the most out of it.</p></details>
      <details><summary>Will it apply to jobs without asking me?</summary><p>Only if you turn on Autonomous mode. By default, every job waits for your Apply.</p></details>
    </div>
  </div></section>
<script>if (location.search.includes("error=1")) document.getElementById("ss-err").hidden = false;</script>
""" + FOOT

thanks = head("You're On the List | FOWL AI", "You're signed up for the free live session: set up your AI job search agent in one hour.",
              "/tools/job-agent/session/thanks/") + SESSION_CSS + """
  <section class="ss-hero"><div class="tl-wrap" style="grid-template-columns:1fr">
    <div><div class="ss-badges"><span class="free">You're in</span><span>Free</span><span>Live online</span></div>
    <h1>You're on the list. <em>See you there.</em></h1>
    <p class="lede">We'll email you the date, time and Zoom link as soon as it's set. Check your inbox for a confirmation now.</p></div>
  </div></section>
  <section class="tl-section"><div class="tl-wrap">
    <h2>Get ready in two minutes</h2>
    <ol class="ss-out">
      <li><b>Have an AI ready</b><span>Claude, ChatGPT, Grok or Meta Muse. A free account works.</span></li>
      <li><b>Find your resume</b><span>Your latest PDF or Word file.</span></li>
      <li><b>Want a head start?</b><span>Connect the Job Agent now at <a href="https://tools.fowl-ai.com/start" style="color:var(--fowl-green)">tools.fowl-ai.com/start</a>.</span></li>
    </ol>
    <p class="tl-note" style="margin-top:22px">Know someone looking for a job? Send them <a href="/tools/job-agent/session/" style="color:var(--fowl-green)">fowl-ai.com/tools/job-agent/session</a>.</p>
  </div></section>
""" + FOOT

for path, html_page in [("tools/job-agent/session/index.html", session), ("tools/job-agent/session/thanks/index.html", thanks)]:
    out = SITE / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_page)
    assert "—" not in html_page.replace("<!--", ""), f"em dash in {path}"
print("session pages written")

# ---------- /links/ (one link for the Instagram and Threads bio) ----------
links = head("FOWL AI links", "Free job agent session, Vibe Code Saturdays and FOWL AI tools in one place.", "/links/") + """
  <section class="tl-hero"><div class="tl-wrap">
    <p class="tl-kicker">FOWL AI</p>
    <h1>Where do you want to go?</h1>
    <p>Pick one. Everything here is from Toyosi and FOWL AI.</p>
  </div></section>
  <section class="tl-section"><div class="tl-wrap">
    <div class="tl-grid">
      <a class="tl-card" href="/tools/job-agent/session/" data-link-location="links-job-agent-session" style="text-decoration:none;color:inherit;border:2px solid var(--fowl-green)">
        <span class="tl-tag">New · Free</span><h3>Set up your AI job search agent in one hour</h3>
        <p>A free live session, Thursday or Friday evening. Leave with your job agent running.</p><p style="color:var(--fowl-green);font-weight:700">Save my free seat →</p></a>
      <a class="tl-card" href="/tools/job-agent/" data-link-location="links-job-agent" style="text-decoration:none;color:inherit">
        <span class="tl-tag">Free tool</span><h3>Job Agent</h3>
        <p>Works in Claude, ChatGPT, Grok or Meta Muse. It finds jobs, tailors your resume and fills in the form. You press Submit.</p><p style="color:var(--fowl-green);font-weight:700">See how it works →</p></a>
      <a class="tl-card" href="/vibe-code-saturdays/" data-link-location="links-vcs" style="text-decoration:none;color:inherit">
        <span class="tl-tag">Class</span><h3>Vibe Code Saturdays</h3>
        <p>Build and launch your website and brand with AI, live with Toyosi.</p><p style="color:var(--fowl-green);font-weight:700">Save my seat →</p></a>
      <a class="tl-card" href="/tools/" data-link-location="links-tools" style="text-decoration:none;color:inherit">
        <span class="tl-tag">All tools</span><h3>FOWL AI Tools</h3>
        <p>Every free tool, one account.</p><p style="color:var(--fowl-green);font-weight:700">Browse tools →</p></a>
    </div>
  </div></section>
""" + FOOT

# ---------- /jobagent/ (the short link said in ads: goes to the free session sign-up) ----------
short = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Job Agent free session | FOWL AI</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="canonical" href="https://www.fowl-ai.com/tools/job-agent/session/">
<meta http-equiv="refresh" content="0; url=/tools/job-agent/session/?utm_source=short&utm_campaign=jobagent">
<meta name="robots" content="noindex"></head>
<body style="font-family:-apple-system,Helvetica,Arial,sans-serif;padding:40px">
<p>Taking you to the free Job Agent session sign-up. <a href="/tools/job-agent/session/">Continue</a></p>
<script>location.replace("/tools/job-agent/session/?utm_source=short&utm_campaign=jobagent")</script></body></html>"""

for path, html_page in [("jobagent/index.html", short)]:  # /links/ is the Brand Brain link-in-bio page; edited by hand
    out = SITE / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_page)
    assert "—" not in html_page.replace("<!--", ""), f"em dash in {path}"
print("links pages written")
