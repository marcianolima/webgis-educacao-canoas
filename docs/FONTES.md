# Matriz de fontes investigadas — 17/10/2026

| Fonte | Órgão | URL oficial | Escala disponível | Ano/competência | Frequência | Formato / chave | Situação | Limitação |
|---|---|---|---|---|---|---|---|---|
| Censo Escolar, microdados | INEP | https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar | Brasil → escola e município | 2025, séries anteriores | Anual | ZIP/CSV; CO_ENTIDADE, CO_MUNICIPIO | Coletor implementado; download e reconciliação no runner pendentes | Layout deve ser conferido por edição; matrícula e coordenadas opcionais |
| IDEB resultados | INEP | https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb/resultados/2005-2025 | Município/rede/escola conforme publicação | 2005–2025 | Ciclo de avaliação | Arquivos oficiais; INEP e município após tratamento | Identificado, não integrado | Divulgações e supressões por elegibilidade |
| Rendimento escolar | INEP | https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais/taxas-de-rendimento-escolar | Brasil → município e escola | 2025 e anteriores | Anual | Planilhas; INEP e município | Identificado, não integrado | Conferir layout e denominação de taxas |
| Distorção idade-série | INEP | https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais/taxas-de-distorcao-idade-serie | Brasil → município e escola | 2025 e anteriores | Anual | Planilhas; INEP e município | Identificado, não integrado | Aplicável a anos/séries específicos |
| Outros indicadores docentes/turmas/INSE | INEP | https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais | Município e/ou escola segundo indicador | Edições distintas | Anual/irregular | Diversos; códigos INEP | Catálogo identificado, não integrado | Não combinar denominadores diferentes |
| IBGE — Canoas | IBGE | https://www.ibge.gov.br/cidades-e-estados/rs/canoas.html | Município | População Censo 2022, estimativa 2026, escolarização 2022 | Censo/estimativa | HTML e serviços IBGE; 4304606 | Valores municipais manualmente verificados e publicados | Escolarização baseada em população residente |
| IBGE SIDRA e geografia | IBGE | https://sidra.ibge.gov.br/ | Município/setor conforme tabela | Censo 2022 e outras | Diversa | API, planilhas; IBGE e geocódigos | Identificado, não integrado | Denominadores e recortes distintos |
| FNDE PNAE/FUNDEB/PDDE | FNDE | https://www.gov.br/fnde/pt-br/acesso-a-informacao/dados-abertos | Município/ente ou escola, segundo programa | Edições distintas | Mensal/anual | Bases variáveis; município, CNPJ, unidade executora ou INEP após verificação | Identificado, não integrado | Repasse municipal não é repasse escolar |
| SIOPE | FNDE | https://www.gov.br/fnde/pt-br/assuntos/sistemas/siope/siope | Ente federativo | Competência fiscal | Anual | Consulta pública | Identificado, não integrado | Execução financeira não é investimento por escola |
| Escolas no RS (geometria) | SEDUC/RS · IDE/RS | https://iede.rs.gov.br/server/rest/services/SEDUC/Escolas_no_RS/MapServer/0 | Escola (RS; filtro Canoas) | 2023 | Referência anual 2023 | ArcGIS REST JSON, codigo_inep / cod_ibge_mun | Coletor implementado; execução e cobertura pendentes | Fonte contém apenas registros georreferenciados; não é universo 2025; posições complementares por INEP |
| Educação RS | SEDUC/RS | https://educacao.rs.gov.br/ | Rede estadual | Variável | Variável | Páginas/catálogos | Investigação parcial | Existência de serviços de escolarização oficiais confirmada na IDE/RS |
| Educação Canoas | Prefeitura | https://www.canoas.rs.gov.br/ | Municipal/unidade | Variável | Variável | Páginas e serviços locais | Investigação pendente | Integrações institucionais requerem conferência |
| GeoCanoas | Prefeitura | https://geo.canoas.rs.gov.br/ | Geoespacial municipal | Dinâmica | Variável | ArcGIS REST/GeoJSON quando exposto | Investigação pendente | Precisão e licença de uso de geometrias |
| TCE/RS | TCE-RS | https://tcers.tc.br/ | Ente público | Variável | Variável | Portais públicos | Investigação pendente | Compatibilizar empenho, liquidação e pagamento |

Situação "Identificado" significa que há catálogo/página oficial, **não** que houve download, verificação de colunas ou dados municipais publicados. Os números populacionais do IBGE são os únicos indicadores oficiais carregados no snapshot inicial; as demais integrações precisam ser reconciliadas na execução do workflow.


## Coleta e validação da edição de 17/10/2026

- **SEDUC/RS / IDE/RS, escolas (2023):** consulta ArcGIS REST validada em 17/10/2026, resultando em 178 registros de Canoas e 178 geometrias, separadas por rede: 83 municipais, 36 estaduais, 1 federal e 58 privadas. Códigos INEP únicos e coordenadas verificadas dentro dos limites municipais plausíveis.
- **INEP 2025:** endereço oficial do ZIP identificado (`https://download.inep.gov.br/dados_abertos/microdados_censo_escolar_2025_.zip`). A tentativa efetiva no Actions de 17/10/2026 apresentou reset de conexão e `SSL: CERTIFICATE_VERIFY_FAILED`; microdados 2025 **não integrados**. Não desabilitar verificação de certificado sem mecanismo comprovável de autenticidade.
- **GitHub Pages:** publicação estática validada com HTTP 200 para HTML, JS, summary.json, schools.json e schools.geojson, contendo o catálogo de 178 escolas da SEDUC 2023.


## Novas fontes efetivamente utilizadas — versão 0.3
- SICONFI DCA Anexo I-E: `https://apidatalake.tesouro.gov.br/ords/cdwhprd/siconfi/tt/dca?an_exercicio=2025&id_ente=4304606&no_anexo=DCA-Anexo+I-E`. Fonte primária oficial, 2019–2025 com ano validado por `cod_ibge`, `exercicio`, `anexo`, `conta` e `coluna`. Despesa Educação, função 12, valores nominais. **Integrado**, sem distribuir para escolas.
- IDEB resultados 2005–2025: catálogo primário `https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb/resultados/2005-2025`. Arquivos ZIP reais identificados por fase; indisponíveis pelo runner. Série histórica municipal cruzada entre `https://prefeiturasemnumeros.com.br/municipios/canoas-rs` e `https://www.eleverconsultoria.com.br/dados/rs/canoas`, **provisória em relação ao dado primário**, publicada em `quality.json` com situação diferenciada.
- SAEB 2025: planilha oficial identificada em `https://download.inep.gov.br/saeb/resultados/saeb_2025_brasil_estados_municipios_censitario.xlsx`; indisponível pelo runner. Proficiências municipais publicadas a partir de fonte secundária, status **a validar com planilha oficial**.


## Campos adicionais do geosserviço SEDUC
A consulta `SEDUC/Escolas_no_RS/MapServer/0` retorna `etapas_modalidade`, `porte_escola`, `localizacao`, `categoria_esc_privada`, `conveniada`, `num_matriculas` e `num_turmas`. Os últimos dois são preenchidos somente em parte das escolas estaduais, sem período explícito de competência; por isso são contextualizados individualmente, não são somados nos indicadores do Censo 2025. A cobertura geográfica continua limitada às escolas com coordenadas da referência cadastral 2023.
