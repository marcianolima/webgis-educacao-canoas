# WebGIS Educação Canoas — versão funcional 0.3.0

**Aplicação pública:** https://marcianolima.github.io/webgis-educacao-canoas/  
**Repositório:** https://github.com/marcianolima/webgis-educacao-canoas  
**Deploy confirmado:** https://github.com/marcianolima/webgis-educacao-canoas/actions/runs/39038793085

Plataforma pública de inteligência territorial educacional para **Canoas/RS**, código IBGE **4304606**. Vite + TypeScript, ECharts, MapLibre e pipeline de dados Python 3.12, publicação GitHub Pages.

## O que já funciona

- Página inicial municipal com IBGE: população do Censo 2022 (**347.657**), estimativa 2026 (**359.845**) e escolarização de 6–14 anos (**97,17%**, Censo 2022).
- Mapa interativo e catálogo georreferenciado de **178 escolas** da IDE/RS SEDUC, referência **2023**. Redes: **83 municipais, 36 estaduais, 1 federal e 58 privadas**. Inclui escolas privadas e públicas, filtros por rede, busca por nome e INEP, clustering e seleção.
- Ficha cadastral individual por código INEP, endereço quando disponível, rede, posição, seleção compartilhável por `?inep=...`, exportação CSV e tema claro/escuro.
- Separação rigorosa entre dados municipais e os indicadores de cada escola. Escolas do catálogo 2023 não são anunciadas como universo completo do Censo Escolar 2025.
- Painéis temáticos e metodologia com estados de indisponibilidade honestos enquanto fontes exigem integração.
- Deploy estático e verificação real da URL pública após publicação: HTML, JS e snapshots responderam HTTP 200.
- Testes de integridade, projeção e coordenadas, chaves INEP, ausência de identificadores pessoais e consistência entre JSON/GeoJSON.

## O que ainda **não** está integrado

- **Matrículas, docentes, turmas e infraestrutura 2025:** existe ETL para os microdados oficiais do INEP 2025, mas a primeira carga encontrou **reset de conexão e falha de validação de certificado HTTPS** no host `download.inep.gov.br`, conforme logs do runner. Sem bypass de TLS não houve publicação do Censo 2025. O código mantém os campos nulos, sem estimar valores.
- **IDEB/SAEB, fluxo, rendimento, distorção, FNDE/SIOPE:** fontes catalogadas, indicadores ainda não integrados.
- Georreferenciamento não foi realizado por inferência textual: posições vêm do serviço oficial SEDUC/RS, baseado no INEP 2023.

## Coleta e implantação — processos isolados

| Workflow | Papel | Disparo |
|---|---|---|
| `.github/workflows/deploy.yml` | Testes Python, typecheck TS, build Vite, inspeção da pasta dist e deploy GitHub Pages com teste HTTP público de ponta a ponta | Push na main ou manual |
| `.github/workflows/bootstrap-map.yml` | Coleta do MapServer SEDUC, validação de 178 registros e commit dos snapshots | Primeira publicação; manual |
| `.github/workflows/bootstrap-inep.yml` | Tentativa de primeira carga Censo 2025 e enriquecimento por SEDUC | Primeira publicação; manual |
| `.github/workflows/update-data.yml` | INEP/SEDUC independentes, preserva snapshots quando fonte falha; mostra avisos de qualidade | Mensal ou manual |

O **deploy não depende do sucesso do download externo**. Quando o coletor conseguir publicar novos snapshots válidos, o commit automático em `public/data/` disparará o deploy.

## Executar e verificar localmente

```bash
npm install
python -m unittest discover -s tests -v
npm run build
npm run dev
```

Requisitos: Node.js 22 e Python 3.12 ou superior. Para validar o Censo manualmente: `python scripts/inep_censo.py` (download do servidor oficial INEP requer TLS confiável, conectividade e espaço temporário).

## Documentação

- `docs/ARQUITETURA.md` — contratos e CI/CD;
- `docs/FONTES.md` — matriz e granularidades;
- `docs/METODOLOGIA.md` — indicadores e limites;
- `docs/DIAGNOSTICO_DEPLOY.md` — análise dos erros corrigidos e evidência de publicação;
- `CHANGELOG.md` — histórico e versão.

Os dados cadastrais escolares provêm de fontes públicas e são apresentados como base de consulta territorial exploratória; o sistema não substitui as publicações oficiais do INEP, FNDE, IBGE ou da Secretaria Municipal da Educação. O WebGIS Saúde não foi alterado.

## Ampliação de indicadores — v0.3
- **Financiamento municipal primário:** DCA/SICONFI da função 12 (Educação), série 2019–2025; valores nominais empenhados, liquidados e pagos; subfunções separadas (não aditivas). Scripts: `scripts/finance_siconfi.py` e `.github/workflows/refresh-finance.yml`.
- **IDEB 2005–2025 de Canoas por etapa:** duas fontes secundárias independentes reproduzem os dados atribuídos ao INEP; identificados claramente como *corroborados em fontes secundárias*, não extração original. O IDEB individual de cada escola ainda não foi coletado.
- **SAEB 2025:** valores municipais provenientes de uma fonte secundária, identificados como *aguardando conferência adicional*; não vinculados a escolas.
- **Pesquisa de ONGs:** `docs/FONTES_COMPLEMENTARES.md` e sessão de Fontes no site detalham fontes validadas de contexto, critérios e condições de acesso.
- **Testes:** Playwright em Chromium simulado nos tamanhos desktop, tablet e celular; capturas de tela e rastreamento de falhas ficam nos artefatos do workflow. Não é homologação com aparelhos físicos.
- **Censo Escolar 2025:** endpoint do ZIP e dicionário de tabelas identificados; conectividade TLS oficial `download.inep.gov.br` instável/indisponível no GitHub runner. Não desativamos a segurança nem publicamos contagens inventadas.

## Dados federais PNAE (2024)
Planilha XLSX oficial FNDE, `scripts/fnde_pnae.py`. A Prefeitura Municipal de Canoas tem **5 ações com previsão total de R$ 5.895.260,80 em 2024** (creche, AEE, EJA, ensino fundamental e pré-escola). O campo é previsão por ação, **não valor pago ou repassado**. Quantidades por ação não são estudantes únicos. O arquivo inclui SHA-256 do material original. Consulte `public/data/pnae.json`.


## Oferta escolar e classificação territorial
As escolas georreferenciadas da IDE/RS (referência INEP 2023) incluem etapa/modalidade ofertada, faixa de porte, tipo de localização, categoria privada e convênios, quando declarados. Os filtros de rede, etapa, porte e busca textual podem ser combinados. A mesma escola pode oferecer várias etapas, portanto a soma das contagens por etapa pode superar o total de escolas. Campos numéricos estaduais (`num_matriculas`, `num_turmas`) não têm competência explicitada pelo serviço e não entram nos totais do município.


## Perfil etário IBGE/SIDRA 9514 — Censo Demográfico 2022
O coletor `scripts/ibge_age.py` consulta a API SIDRA oficial por município IBGE 4304606, confirma população total de **347.657 residentes** e reconcilia idades simples 0–24 com faixas quinquenais. Publica as faixas 0–3, 4–5, 6–14, 15–17, 18–24 e o agregado 0–17, usadas no módulo Educação Infantil e Painel Municipal. Esses números representam residentes no Censo 2022, não matrículas em escolas nem estimativas de 2026. Atualização anual de verificação do arquivo está em `.github/workflows/refresh-ibge-age.yml`.


## Estado da v0.4 — fontes efetivamente novas
- **FNDE PNAE (2024):** R$ 5.895.260,80 **previstos**, em cinco ações, pela entidade executora Prefeitura Municipal de Canoas; estudantes contabilizados por ação (podem se sobrepor). `public/data/pnae.json`, `scripts/fnde_pnae.py`.
- **IBGE/SIDRA (2022):** população residente de 0–3, 4–5, 6–14, 15–17, 18–24 e 0–17, sem projeções artificiais. `public/data/ibge_age.json`, `scripts/ibge_age.py`.
- **SEDUC/RS (base cartográfica 2023):** oferta escolar, tipo de localização, porte e características das unidades, com filtros cruzados. Campos de matrículas e turmas do geosserviço estadual sem competência explícita não compõem somas municipais.
- **Em análise:** fontes FNDE/PAB para valores PNAE efetivamente transferidos, PNATE, SIOPE e PDDE; INEP Data para matrícula 2025 e IDEB/SAEB por escola.

## Versão 0.5 — Censo 2025 por rede e PDDE 2025 por escola
O Censo Escolar de 2025 passou a integrar indicadores oficiais agregados municipais derivados do INEP por planilhas SEDUC/RS: **196 escolas, 68.490 matrículas**, das quais **82 municipais e 30.597 matrículas municipais**. Séries históricas 2010–2025 de matrículas e percentuais de infraestrutura por rede. O cadastro territorial do mapa tem referência 2023 (178 pontos), não o mesmo universo.
Também foi integrada a consulta pública PDDE Info por código INEP 2025: 83 escolas municipais do cadastro 2023 consultadas, 82 com pagamentos confirmados e uma sem resultado; pagamentos válidos somam **R$ 3.769.394,00** somente nas escolas cobertas. Cada ficha mostra os programas, valores pagos e datas, sem dados bancários.
Arquivos públicos: public/data/rs_censo_municipal.json e public/data/pdde_schools.json. Coletores: scripts/rs_censo.py e scripts/fnde_pdde.py. Workflows: refresh-rs-censo.yml e refresh-pdde.yml.
Microdados individuais de matrículas e docentes por escola, IDEB individual e SAEB individual ainda pendem da extração nacional segura do INEP, cujo servidor permanece com falhas TCP/TLS no GitHub runner.
