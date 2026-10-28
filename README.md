# WebGIS Educação Canoas — versão 1.0.0

[**Abrir aplicação**](https://marcianolima.github.io/webgis-educacao-canoas/) · [Código-fonte](https://github.com/marcianolima/webgis-educacao-canoas) · [Testes e publicação](https://github.com/marcianolima/webgis-educacao-canoas/actions)

Observatório territorial de educação do município de **Canoas/RS** (IBGE **4304606**), com indicadores oficiais, séries históricas, cartografia interativa, fichas de escolas e transparência das fontes. Aplicação estática e responsiva, desenvolvida com **Vite, TypeScript, MapLibre GL JS e Apache ECharts** e publicada pelo GitHub Actions/Pages.

> **Escopo da 1.0:** a aplicação está estruturada para publicação, monitoramento e testes de regressão. Versão 1.0 **não** significa que todas as fontes públicas possam ser coletadas automaticamente nem que todos os indicadores tenham a mesma cobertura. Cada visualização informa período, escala e origem. Informação ausente não é zero.

## Dados disponíveis

| Domínio | Informação e granularidade | Competência |
| --- | --- | --- |
| Panorama | População residente de 347.657, estimativa de 359.845 e escolarização de 6–14 anos | IBGE, Censo 2022 e estimativa 2026 |
| Censo Escolar | 204 registros escolares, 196 em atividade, 68.490 matrículas e 3.567 funções docentes; indicadores e características por unidade | INEP, microdados oficiais 2025 V2, ZIP verificado por SHA-256 |
| Cartografia | 169 unidades do cadastro 2025 localizadas; as restantes continuam consultáveis na lista | SEDUC/RS, geometria com referência **2023** |
| Matrículas e infraestrutura | Séries por rede, etapa e indicadores de condições de oferta | INEP/SEDUC-RS, série 2010–2025 |
| Qualidade da educação | IDEB 2005–2025 por rede/etapa e IDEB 2025 **por escola quando divulgado**; rendimento, SAEB e INSE devidamente identificados | INEP/SEDUC-RS, competências específicas |
| Profissionais | Indicador de adequação da formação docente, complexidade de gestão escolar, rendimento | SEDUC/RS, 2025; INSE 2023 |
| Financiamento | Despesa municipal função 12, estágios empenhado, liquidado e pago | Tesouro Nacional, SICONFI/DCA 2019–2025 |
| PNAE/PNATE | PNAE 2024 **previsto**, série PNAE do campo oficial `Valor_Repasse` 2009–2025; PNATE com valores **a pagar** | FNDE |
| PDDE por escola | Pagamentos de 2025 para escolas municipais consultadas, cobertura parcial e identificada | FNDE PDDE Info |
| Demografia | Faixas etárias e idades simples de 0 a 24 anos | IBGE/SIDRA 2022 |

**Universos distintos:** os **204 registros** do Censo Escolar INEP 2025 incluem **8 escolas não ativas**; o universo **ativo tem 196 escolas**. As **169 coordenadas conciliadas** se originam do cadastro estadual de 2023 e podem não representar o endereço mais recente. Uma escola sem coordenada não é removida do catálogo.

## Interface e operação

A aplicação oferece Painel Municipal, Escolas e Mapa, Matrículas e Redes, Qualidade, Infraestrutura, Profissionais, Educação Infantil, Financiamento e Dados/Metodologia. Inclui menus agrupados, cabeçalho compacto, tema claro/escuro, busca escolar por nome ou código INEP com filtro instantâneo, filtros de rede/etapa/porte, agrupamento de pontos no mapa, ficha individual por `?inep=CODIGO`, exportação CSV e gráficos interativos.

A versão mobile possui menu lateral com página atual destacada, fechamento por Escape e retorno de foco, link de salto para conteúdo e preferência por movimento reduzido. A interface é **mobile first**, mas os testes automatizados não substituem uma auditoria independente de acessibilidade nem uma homologação com aparelhos físicos.

## Fonte, metodologia e restrições

- O **INEP 2025** contém indicadores de escolas, matrículas e funções docentes. Dados individuais de estudantes/professores ou ZIP nacional bruto **não** são publicados pela aplicação.
- O **IDEB escolar** está disponível apenas para unidades e etapas com resultado oficial publicado. Ausência não é nota zero. Não se aplicam médias municipais a escolas individuais.
- O **SAEB 2025 estadual** foi conciliado com dados SEDUC/RS. O resultado de proficiência **municipal** de fonte secundária permanece marcado como provisório até verificação no arquivo primário.
- O **PNAE** distingue previsão 2024 de valores anuais reportados como `Valor_Repasse`. O PNATE `vl_pagar_*` significa **valor a pagar**, não pagamento realizado. O PDDE publicado cobre escolas consultadas, não representa automaticamente o total municipal.
- O dado de **execução orçamentária SICONFI** não corresponde diretamente a repasse FNDE nem a gasto por escola.
- Novas séries e serviços estão **catalogados**, não necessariamente importados: INEP (distorção idade-série, esforço e regularidade docente, horas-aula e tamanho de turma), Censo Escolar 2026, FNDE/FUNDEB/PNLD e fontes de organizações da sociedade civil.

**Resiliência:** se a fonte remota do FNDE responder 404 ou falhar transitoriamente, o processo conserva o último snapshot validado e emite advertência, sem mudar sua data. Mudanças de esquema ou inconsistências nos valores permanecem erros, impedindo publicar valores não comprovados.

Consulte [Fontes](docs/FONTES.md), [Metodologia](docs/METODOLOGIA.md), [Arquitetura](docs/ARQUITETURA.md) e os diretórios `scripts/` e `public/data/` para proveniência detalhada.

## Instalar e testar

Requisitos: **Node.js 22+**, npm e **Python 3.12+**.

```bash
npm install
python -m unittest discover -s tests -v
npm run build
npx playwright install chromium
npm run test:e2e
npm run dev
```

O caminho de publicação está em `vite.config.ts`. Os snapshots ficam versionados em `public/data/`; novas cargas exigem validação de município, competência, integridade, denominadores, granularidade e privacidade.

### Workflows e homologação

- `.github/workflows/deploy.yml` executa testes Python, TypeScript e Vite, valida `dist/`, roda testes Playwright em **Chromium simulado** desktop (1440 px), tablet (810 px) e celular (390 px), disponibiliza capturas e verifica a URL pública após o deploy.
- `.github/workflows/collect-inep-windows.yml` baixa a edição INEP 2025 V2 com checksum verificado, concilia matrícula/docência por estabelecimento e incorpora coordenadas SEDUC de 2023.
- `.github/workflows/refresh-*.yml` atualiza independentemente as fontes estaduais/federais quando disponíveis.
- `tests/test_pipeline.py`, `tests/test_indicators.py` e `tests/test_release.py` validam snapshots, conceitos e cobertura; `tests/ui.e2e.spec.ts` cobre navegação, filtros, fichas, tema, acessibilidade básica, responsividade e transbordamento de cards.

Antes de atestar a versão publicada, verifique o **resultado da execução mais recente** no [GitHub Actions](https://github.com/marcianolima/webgis-educacao-canoas/actions). Homologação em dispositivos físicos, auditoria WCAG formal e disponibilidade permanente dos servidores externos continuam exigindo acompanhamento próprio.

## Direitos e responsabilidade

Consulte as condições de uso de cada fonte. Este é um projeto de análise territorial baseado em informações públicas, **não substitui** os sistemas certificados do INEP, IBGE, FNDE, SEDUC/RS ou Prefeitura de Canoas. Nenhuma licença de software foi declarada; a disponibilidade pública do código não implica concessão de licença para qualquer uso.

Veja [CHANGELOG.md](CHANGELOG.md) para histórico. **Versão 1.0.0 — 27 de outubro de 2026.**
