# Presente Vivo — Natal 2026

Aplicação para criar presentes digitais personalizados, com página-surpresa e cartão de 85 × 50 mm com QR Code. FastAPI + SQLite, pronta para Docker Compose em VPS Contabo.

## Implantação

```bash
git clone https://github.com/fcoelopes/presente-vivo.git
cd presente-vivo
cp .env.example .env
# Ajuste PUBLIC_BASE_URL, ADMIN_USER e ADMIN_PASSWORD em .env
mkdir -p data
sudo chown 10001:10001 data
docker compose up -d --build
curl -f http://127.0.0.1:8098/health
```

O serviço escuta somente em **127.0.0.1:8098** no host. Configure o proxy HTTPS (Traefik existente, Caddy ou Nginx) para essa porta. Não exponha a porta pública diretamente.

- Administração: `/admin` (HTTP Basic sob HTTPS)
- Surpresa pública: `/p/{id}`
- Impressão: `/tag/{id}`
- QR: `/qr/{id}.png`
- Banco SQLite: `./data/presentes.sqlite3` (volume persistente; não versionado)
- Backup consistente: `./scripts/backup-sqlite.sh`

O destinatário não precisa de conta, mas quem tiver o link consegue visualizar. Evite compartilhar dados sensíveis. URLs de mídia devem ser HTTPS direto para foto/áudio, com direitos de uso.

### Limitações conhecidas do MVP

Ainda faltam edição/exclusão/expiração, upload direto para object storage, rate limiting, consentimento e política de privacidade, backup periódico automatizado e suíte ampla de testes. **Não utilize para dados pessoais de clientes em escala antes desses controles.** Teste o QR impresso em aparelhos diferentes.

## Publicação na Contabo com Traefik

O `compose.yaml` usa a rede externa Docker `proxy` e o roteador HTTPS `presente-vivo` para o domínio `presente.arc.tec.br`. Pré-requisitos: rede `proxy` existente, Docker provider ativo, entrypoint `websecure` e resolvedor `letsencrypt` no Traefik. O serviço mantém a porta local `127.0.0.1:8098` para diagnóstico.

Antes de atualizar, confirme que `websecure` existe em `~/vps-proxy/traefik.yml` e configure `PUBLIC_BASE_URL=https://presente.arc.tec.br` no `.env` da VPS. Confira também que o registro DNS aponta para o IP público correto. Execute:

```bash
git pull --ff-only
docker compose config -q
docker compose up -d --build
docker compose ps
curl -fsS http://127.0.0.1:8098/health
curl -I https://presente.arc.tec.br/admin
```

O endpoint `/admin` deve responder **401 Unauthorized** sem credenciais: isso confirma a proteção HTTP Basic. O código **200** no endpoint `/health` confirma a verificação básica do banco SQLite.

**Atenção:** mantenha o `.env` e o banco fora do Git. Não faça `docker compose down -v`. Para backup consistente, use o script `scripts/backup-sqlite.sh` e copie os backups para outro host ou object storage. Confirme a emissão TLS no navegador ou com `curl -Iv` antes de cadastrar conteúdo real.
