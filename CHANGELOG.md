## Fonte primária de IDEB e SAEB por rede — 17/10/2026
- Série 2005–2025 oficial do IDEB para redes municipal/estadual em Canoas substituiu a dependência de sites secundários. IDEB municipal 2025: 5,3 anos iniciais, 4,6 anos finais.
- SAEB 2025 rede estadual em Canoas validado com planilha da SEDUC/RS; rede municipal ainda não consta como recorte dessa planilha.
- Portal qualidade apresenta proveniência e diferenciação municipal/estadual. 

## Ampliação pré-1.0 — 17/10/2026
- Rendimento escolar 2010–2025: aprovação, reprovação e abandono por rede/etapa, com séries e gráficos.
- Formação docente AFD 2013–2025 por rede e etapas; grupo 1 no ensino fundamental municipal de 2025: 73,6%.
- Complexidade de gestão ICG 2013–2025 por rede e níveis: municipal 2,79 em 2025.
- Nível socioeconômico INSE de 2019–2023, com referência explícita de 2023 e não projeção.
- Dados provenientes de 4 planilhas oficiais SEDUC/RS com SHA-256 e testes de reconciliação.

## 0.5.0 — 17/10/2026
- Séries Censo Escolar por município/rede/etapa 2010–2025 (fonte INEP via SEDUC/RS): 196 escolas e 68.490 matrículas em 2025; rede municipal 82 escolas e 30.597 matrículas.
- Fonte oficial FNDE PDDE Info por código INEP com programas, datas e valores efetivamente pagos: 82 escolas municipais respondentes positivos, R$ 3.769.394,00; uma escola consultada sem resposta oficial.
- Workflows independentes, testes de reconciliação e distinção entre cadastro geográfico 2023 e totais municipais 2025.
- Ainda pendentes matrículas/infraestrutura/IDEB por escola e SAEB por escola vindos do INEP 2025.

## 0.4.0 — 17/10/2026 — PNAE, demografia e oferta territorial
- Corrigidos cartões financeiros em celulares: grid de uma coluna, tipografia flexível e teste automático de overflow incluindo PNAE.
- PNAE 2024: planilha oficial FNDE recuperada por HTTPS com integridade SHA-256; cinco ações de Canoas e previsão total R$ 5.895.260,80. Indicadores rotulados como **previstos**, não transferidos.
- IBGE/SIDRA tabela 9514: população por idade simples de 0 a 24 anos, validada contra o total do Censo 2022 (347.657) e faixas quinquenais. Integração na página inicial e no módulo Educação Infantil.
- SEDUC/RS (cadastro geográfico 2023): ofertas educacionais, categorias, faixas de porte e filtros de etapa/porte, novos campos nas fichas por código INEP; dados estaduais sem período explícito não utilizados em agregados oficiais.
- Atualização separada por fonte via GitHub Actions; testes Python/TypeScript e Playwright desktop/tablet/celular.
- Continua pendente o download do microdado 2025 do INEP via host oficial (falhas de conexão/certificação), IDEB/SAEB originais por escola, repasses efetivamente pagos do PNAE/PDDE/PNATE/FUNDEB.

## 0.3.0 — 17/10/2026 — Qualidade, SICONFI e fontes complementares
- Fonte primária Tesouro Nacional SICONFI, DCA Anexo I-E, função Educação: séries anuais verificadas 2019–2025; estágios empenhada/liquidada/paga e subfunções sem dupla contagem.
- IDEB municipal por etapa 2005–2025, valores corroborados em portais secundários que referenciam o INEP; proveniência e limitações em destaque.
- SAEB 2025 na rede municipal, proficiências secundárias com nível de evidência diferenciado.
- Painel municipal e páginas específicas agora mostram indicadores e gráficos com tabelas acessíveis e unidades/anos identificados.
- Fontes adicionais catalogadas: Todos Pela Educação, UNICEF/Undime, Fundação Abrinq, Fundação Maria Cecilia Souto Vidigal, Instituto Unibanco, QEdu.
- Playwright emulação de layouts desktop/tablet/celular e capturas de tela no GitHub Actions. Não equivale a teste em dispositivos físicos.
- Bloqueio de download direto do INEP persiste; não contornar TLS.

# Histórico de alterações

## 0.2.0 — 17/10/2026 — Site publicado e testado

- Corrigido teste Python que confundia os campos cadastrais da Tabela_Escola com informações agregadas da Tabela_Matricula.
- Resolvido TS2339 em `import.meta.env` pelo arquivo `src/vite-env.d.ts`.
- Refatorados workflows: deploy Pages independente de fontes externas; atualização de dados em pipeline separado.
- Coletados, reconciliados e publicados 178 registros escolares georreferenciados da IDE/RS / SEDUC, referência **2023**, dos quais 83 municipais, 36 estaduais, 1 federal e 58 privados.
- Painel municipal contextualiza a cobertura geográfica de 2023 separadamente do total censitário de 2025.
- Verificação HTTP pós-publicação de index, JS e snapshots: **HTTP 200** na URL de produção, com 178 escolas e 178 geometrias.
- Tentativa de INEP 2025 identificou problema de conexão e cadeia de certificados no serviço HTTPS do órgão; números de matrículas e docentes permanecem indisponíveis (não presumidos).
- Testes Python, TypeScript, Vite, inspeção dos artefatos dist/ e deploy-pages concluíram com sucesso na execução 39038793085.
- Escopo: versão funcional inicial com dados geográficos oficiais; não é a versão 1.0 de indicadores educacionais completos.

## 0.1.0 — 17/10/2026
- Estrutura Vite/TypeScript, ECharts, MapLibre, temas e módulos de educação.
- Indicadores municipais IBGE, modelo de dados e coletores.
