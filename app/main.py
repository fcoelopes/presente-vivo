import html
import io
import os
import re
import secrets
import sqlite3
from datetime import datetime, timezone
from urllib.parse import urlparse

import qrcode
from fastapi import Depends, FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles

BASE = os.getenv("PUBLIC_BASE_URL", "http://localhost:8098").rstrip("/")
DB = os.getenv("DB_PATH", "/data/presentes.sqlite3")
ADMIN_USER = os.getenv("ADMIN_USER", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
if not ADMIN_USER or not ADMIN_PASSWORD:
    raise RuntimeError("Defina ADMIN_USER e ADMIN_PASSWORD.")
app = FastAPI(title="Presente Vivo", docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")
security = HTTPBasic()
THEMES = {"familia": "Natal em Família", "amor": "Natal de Quem Ama", "gratidao": "Você é Meu Presente"}

def esc(value):
    return html.escape(str(value or ""), quote=True)

def connect():
    os.makedirs(os.path.dirname(DB) or ".", exist_ok=True)
    c = sqlite3.connect(DB, timeout=30)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA busy_timeout=30000")
    return c

with connect() as c:
    c.execute("""CREATE TABLE IF NOT EXISTS gifts (
        id TEXT PRIMARY KEY, theme TEXT NOT NULL, recipient TEXT NOT NULL,
        sender TEXT NOT NULL, teaser TEXT NOT NULL, message TEXT NOT NULL,
        voice_url TEXT NOT NULL, photo_url TEXT NOT NULL,
        extra_messages TEXT NOT NULL, created_at TEXT NOT NULL,
        enabled INTEGER NOT NULL DEFAULT 1
    )""")

def auth(credentials: HTTPBasicCredentials = Depends(security)):
    if not (secrets.compare_digest(credentials.username.encode(), ADMIN_USER.encode())
            and secrets.compare_digest(credentials.password.encode(), ADMIN_PASSWORD.encode())):
        raise HTTPException(401, "Acesso negado", headers={"WWW-Authenticate": 'Basic realm="Presente Vivo"'})

def page(title, body, theme="familia"):
    return HTMLResponse(
        '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<meta name="robots" content="noindex,nofollow"><title>' + esc(title) + '</title>'
        '<link rel="stylesheet" href="/static/style.css"></head><body class="theme-' + esc(theme) + '">'
        + body + '</body></html>',
        headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer",
                 "X-Content-Type-Options": "nosniff",
                 "Content-Security-Policy": "default-src 'self'; img-src 'self' data: https:; media-src 'self' https:; style-src 'self'; script-src 'self'; base-uri 'none'; form-action 'self'"}
    )

def media(value):
    if not value.strip():
        return ""
    p = urlparse(value.strip())
    if p.scheme != "https" or not p.netloc or p.username or p.password:
        raise HTTPException(422, "Endereço de mídia deve ser HTTPS válido")
    return value.strip()

def get_gift(key):
    if not re.fullmatch(r"[A-Za-z0-9_-]{16,40}", key):
        raise HTTPException(404)
    with connect() as c:
        record = c.execute("SELECT * FROM gifts WHERE id=? AND enabled=1", (key,)).fetchone()
    if record is None:
        raise HTTPException(404)
    return record

@app.get("/")
def root():
    return RedirectResponse("/admin")

@app.get("/health")
def health():
    with connect() as c:
        c.execute("SELECT 1").fetchone()
    return {"status": "ok"}

@app.get("/admin")
def admin(_=Depends(auth)):
    with connect() as c:
        items = c.execute("SELECT id, recipient, theme FROM gifts ORDER BY created_at DESC LIMIT 100").fetchall()
    options = "".join('<option value="' + k + '">' + esc(v) + '</option>' for k,v in THEMES.items())
    rows = "".join('<tr><td>' + esc(r["recipient"]) + '</td><td>' + esc(THEMES[r["theme"]])
                   + '</td><td><a href="/p/' + r["id"] + '">Ver</a> · <a href="/tag/' + r["id"]
                   + '">Tag</a> · <a href="/qr/' + r["id"] + '.png">QR</a></td></tr>' for r in items)
    body = """<main class="admin"><div class="panel"><p class="eyebrow">ATELIÊ • EDIÇÃO NATAL 2026</p>
    <h1>Crie um Presente Vivo</h1><p>Um presente físico, uma surpresa digital e uma lembrança especial.</p>
    <form action="/admin/create" method="post">
    <label>Experiência<select name="theme">""" + options + """</select></label>
    <label>Para<input name="recipient" required maxlength="60" placeholder="Juliana"></label>
    <label>De<input name="sender" required maxlength="60" placeholder="Carlos"></label>
    <label>Frase no cartão<input name="teaser" maxlength="120" value="Há um carinho especial esperando por você..."></label>
    <label>Carta digital<textarea name="message" required maxlength="3000" rows="6"></textarea></label>
    <label>Mensagens coletivas (uma por linha: Nome | mensagem)<textarea name="extra_messages" maxlength="3500" rows="4"></textarea></label>
    <label>Foto (URL HTTPS opcional)<input name="photo_url"></label>
    <label>Áudio (URL HTTPS de arquivo MP3 ou OGG, opcional)<input name="voice_url"></label>
    <button>Criar presente e QR Code</button></form>
    <h2>Presentes criados</h2><div class="scroll"><table><tr><th>Para</th><th>Tema</th><th>Links</th></tr>""" + rows + """</table></div>
    </div></main>"""
    return page("Ateliê Presente Vivo", body)

@app.post("/admin/create")
def create(theme: str=Form(...), recipient: str=Form(...), sender: str=Form(...),
           teaser: str=Form(""), message: str=Form(...), extra_messages: str=Form(""),
           photo_url: str=Form(""), voice_url: str=Form(""), _=Depends(auth)):
    if theme not in THEMES:
        raise HTTPException(422, "Tema inválido")
    for value,limit in ((recipient,60),(sender,60),(teaser,120),(message,3000),(extra_messages,3500)):
        if len(value)>limit:
            raise HTTPException(422,"Texto muito longo")
    if not recipient.strip() or not sender.strip() or not message.strip():
        raise HTTPException(422,"Campos obrigatórios não preenchidos")
    key=secrets.token_urlsafe(12)
    with connect() as c:
        c.execute("""INSERT INTO gifts (id,theme,recipient,sender,teaser,message,voice_url,photo_url,extra_messages,created_at,enabled)
                  VALUES (?,?,?,?,?,?,?,?,?,?,1)""",
                  (key,theme,recipient.strip(),sender.strip(),teaser.strip(),message.strip(),
                   media(voice_url),media(photo_url),extra_messages,datetime.now(timezone.utc).isoformat()))
    return RedirectResponse("/admin/created/"+key,status_code=303)

@app.get("/admin/created/{key}")
def created(key: str, _=Depends(auth)):
    r=get_gift(key)
    url=BASE+"/p/"+key
    return page("Presente criado",'<main class="center panel"><h1>Presente para '+esc(r["recipient"])+ ' criado!</h1><p><a href="'+esc(url)+'">'+esc(url)+'</a></p><img class="largeqr" alt="QR Code" src="/qr/'+key+ '.png"><p><a class="btn" href="/tag/'+key+'">Imprimir cartão</a> <a href="/admin">Novo presente</a></p></main>')

@app.get("/qr/{key}.png")
def qr(key: str):
    get_gift(key)
    image=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H,box_size=8,border=4)
    image.add_data(BASE+"/p/"+key)
    image.make(fit=True)
    picture=image.make_image(fill_color="#542138",back_color="white")
    output=io.BytesIO()
    picture.save(output,format="PNG")
    output.seek(0)
    return StreamingResponse(output,media_type="image/png",headers={"Cache-Control":"private, no-store"})

@app.get("/tag/{key}")
def tag(key: str):
    r = get_gift(key)
    import json
    payload = {
        "id": r["id"], "theme": r["theme"],
        "recipient": r["recipient"], "sender": r["sender"],
        "teaser": r["teaser"]
    }
    # Escape the characters that could end an inline JSON script element.
    serialized = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    body = (
        '<main class="premium-page">'
        '<div class="premium-toolbar"><button id="premium-print">Imprimir 85 × 50 mm</button>'
        '<button id="premium-svg-download">Baixar SVG</button>'
        '<a href="/admin">Voltar ao Ateliê</a></div>'
        '<div class="premium-frame" id="premium-mount"></div>'
        '<p class="premium-note">Tag premium • QR funcional • faça uma prova de impressão antes da produção</p>'
        '</main><script type="application/json" id="tag-data">' + serialized + '</script>'
        '<script src="/static/tag-premium.js" defer></script>'
    )
    document = page("Cartão premium para " + r["recipient"], body, r["theme"])
    document.body = document.body.replace(
        b'</head>', b'<link rel="stylesheet" href="/static/tag-premium.css"></head>'
    )
    return document

@app.get("/p/{key}")
def present(key: str):
    r=get_gift(key)
    extras=[]
    for line in r["extra_messages"].splitlines():
        if "|" in line:
            author,msg=line.split("|",1)
            if author.strip() and msg.strip():
                extras.append('<div class="mini"><b>'+esc(author.strip())+'</b><p>'+esc(msg.strip())+'</p></div>')
    photo='<img class="memory" loading="lazy" alt="Fotografia especial" src="'+esc(r["photo_url"])+'">' if r["photo_url"] else ""
    audio='<p>Uma mensagem de voz para você</p><audio controls preload="none" src="'+esc(r["voice_url"])+'"></audio>' if r["voice_url"] else ""
    body='<main class="experience"><div class="panel"><span class="eyebrow">'+esc(THEMES[r["theme"]].upper())+ '</span><div class="symbol">✦ ♥ ✦</div><h1>'+esc(r["recipient"])+', este momento é seu.</h1>'+ '<p>Há palavras que merecem ser guardadas.</p><button id="openGift" aria-expanded="false" aria-controls="secret">Abrir meu presente ✨</button>'+ '<section id="secret" hidden><div class="letter"><span class="eyebrow">UMA CARTA PARA VOCÊ</span><p class="letterbody">'+esc(r["message"])+ '</p><p>Com carinho, <em>'+esc(r["sender"])+'</em></p></div>'+photo+audio+ ('<h2>Mensagens especiais</h2>'+"".join(extras) if extras else "")+ '<p class="closing">Feito com carinho para guardar na memória. ♥</p></section></div></main><script src="/static/experience.js" defer></script>'
    return page("Uma surpresa para "+r["recipient"],body,r["theme"])
