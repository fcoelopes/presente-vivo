# Presente Vivo — Catálogo de Experiências v1 (Natal 2026)

**Regra de produto:** um template é uma narrativa e interação distintas, não apenas uma troca de nomes, cores ou ornamentos.

## Modelo conceitual

- **Ocasião** (`occasion`): natal, aniversário, romance, gratidão, família.
- **Experiência digital** (`experience_template`): fluxo, estrutura, texto editorial e gesto de descoberta.
- **Cartão físico** (`card_template`): identidade visual e arquivo de impressão. Independente do template digital.
- **Tema** (`theme`): paleta/acabamento do cartão e da experiência, coordenados sem exigir que sejam idênticos.

## Templates oficiais

### 1. Carta Clássica — `classic_letter`

**Promessa:** a pessoa recebe um envelope particular e descobre uma carta dirigida a ela.

**Narrativa e interface:** papel texturizado, espaço em branco, selo e dobra de envelope; título intimista, texto com tipografia editorial, assinatura em evidência. Layout vertical como correspondência, não como cartão genérico.

**Gesto:** clicar/tocar em **Romper o lacre**; envelope abre e a carta se desdobra. Sem áudio automático.

**Microcopy:** abertura: “Algumas palavras merecem ser entregues devagar.”; CTA: “Abrir minha carta”; encerramento: “Guarde estas palavras por perto.”

**Dados essenciais:** destinatário, remetente, dedicatória; foto e áudio opcionais.

**Acessibilidade:** interação também por teclado; redução de movimento transforma abertura em transição imediata.

### 2. Presente Encantado — `enchanted_gift`

**Promessa:** descobrir o que há atrás de um presente digital natalino.

**Narrativa e interface:** caixa com fita e lacre, fundo festivo contido, três estados visuais (embrulho fechado → aberto → surpresa); pode combinar vinho/dourado ou verde/creme, sem ser uma carta disfarçada.

**Gesto:** clicar/tocar em **Desatar o laço** para abrir a caixa; então revelar a dedicatória e, opcionalmente, foto/áudio.

**Microcopy:** abertura: “Existe mais um presente esperando por você.”; CTA: “Desatar o laço”; encerramento: “O melhor presente é o carinho de quem lembrou de você.”

**Dados essenciais:** destinatário, remetente, mensagem; mídia opcional.

**Acessibilidade:** botões claros, animações discretas, sem flashes, redução de movimento suportada.

### 3. Álbum de Memórias — `memory_album`

**Promessa:** uma história compartilhada que pode ser folheada.

**Narrativa e interface:** capa de álbum e folhas com foto e pequena legenda, páginas numeradas, layout tipo scrapbook com papéis sobrepostos e navegação lateral.

**Gesto:** clicar/tocar em **Folhear nossas memórias**; capa abre e páginas são navegadas por controles de avançar/voltar. Não mostrar fotos futuras antes do avanço.

**Microcopy:** abertura: “Algumas histórias merecem ser revisitadas.”; CTA: “Abrir nosso álbum”; encerramento: “E ainda temos tantas páginas para viver.”

**Dados essenciais:** destinatário, remetente, dedicatória e coleção de 1–8 fotografias com legendas opcionais; sem fotos, o painel recomenda outro template.

**Acessibilidade:** navegação por teclado, rótulos acessíveis, alt text nas imagens; layouts adaptados ao celular.

## Fluxo do editor

1. Criar presente → escolher ocasião.
2. Selecionar template digital com prévias **de estrutura e interação**.
3. Escolher template do cartão físico separadamente.
4. Preencher conteúdo relevante (campos condicionais ao template).
5. Visualizar o fluxo no celular e o cartão em 85 × 50 mm.
6. Publicar URL opaca → gerar QR; o endereço não muda quando a identidade for atualizada.

## Compatibilidade e persistência

- Preservar os dados atuais da tabela `gifts`, o SQLite em volume e a rota `/p/{id}`.
- Migração aditiva: `experience_template TEXT` com default seguro `classic_letter`, `card_template TEXT` (ou valor legado), `occasion TEXT`; caso legado sem valor, selecionar `classic_letter`.
- Conteúdo de álbum: tabela `gift_media` com `gift_id`, `sort_order`, `media_type`, `url`, `caption`, `alt_text`; não sobrecarregar uma coluna JSON sem necessidade.
- Não alterar registros e IDs antigos na migração.
- Sanitizar textos no HTML; aceitar mídias com política definida; estabelecer retenção, exclusão e permissões antes de uso comercial.

## Critérios de aceitação

- [ ] Há três fluxos estruturalmente diferentes (envelope, caixa, álbum), não somente skins.
- [ ] Prévia fiel mobile/desktop antes de publicar.
- [ ] Cartão físico escolhido de forma independente.
- [ ] URLs existentes continuam funcionando, e presentes antigos usam fallback.
- [ ] Carta e surpresa permanecem ocultas até a ação explícita.
- [ ] Álbum oferece anterior/próximo e mantém a ordem de fotos.
- [ ] Sem áudio automático, flashes ou dependência de animação para entender o conteúdo.
- [ ] Testes de migração SQLite, regressão de URLs, acessibilidade básica e HTTP.
- [ ] Não colocar alterações em produção automaticamente: PR, CI, revisão visual, deploy controlado.
