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
