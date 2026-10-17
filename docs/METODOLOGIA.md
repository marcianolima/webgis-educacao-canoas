# Dicionário de indicadores, qualidade e privacidade

**Unidade territorial:** Canoas/RS, código IBGE 4304606 (ou 430460 em cadastros com seis algarismos). **Unidade escolar:** código INEP de oito algarismos, uma linha por escola e ano do catálogo.

| Medida | Numerador/contagem | Denominador/escopo | Competência | Observações |
|---|---|---|---|---|
| População no Censo | 347.657 residentes | Não é taxa | 2022 | IBGE, município de residência |
| População estimada | 359.845 residentes | Não é taxa | 2026 | IBGE; não comparar diretamente com matrículas sem método |
| Escolarização 6–14 anos | Residentes de 6 a 14 anos matriculados no ensino regular | Residentes de 6 a 14 anos | 2022 | 97,17%; não significa taxa de matrícula em escolas sediadas em Canoas |
| Escolas cadastradas | Registros únicos CO_ENTIDADE em Canoas | Não é taxa | Censo 2025 | Inclui situações de funcionamento distintas |
| Escolas em atividade | Escolas com TP_SITUACAO_FUNCIONAMENTO=1 | Não é taxa | Censo 2025 | Não confundir com série histórica de escolas existentes |
| Matrículas declaradas | Soma QT_MAT_BAS da Tabela_Matricula unida a Tabela_Escola por CO_ENTIDADE | Não é taxa | Censo 2025 | Não equivale a estudantes únicos; sob cobertura parcial das escolas em atividade permanece null |
| Funções docentes | Soma QT_DOC_BAS da Tabela_Docente vinculada a CO_ENTIDADE | Não é taxa | Censo 2025 | Pode contar a mesma pessoa em diferentes escolas; só com cobertura integral |
| Infraestrutura | Escolas com IN_*=1 | Escolas com resposta 0/1 naquele campo | Censo 2025 | Não contam respostas nulas no denominador |
| IDEB / SAEB | Conforme metodologia oficial e edição | Conforme regras de elegibilidade | 2025 e anteriores | Não integrados; não inferir pontuações |
| Financiamento | Repasses oficiais conforme programa e ente beneficiário | Variável | Várias | Não redistribuir repasses de município entre escolas |

**Governança de esquema:** o coletor mantém no arquivo `inep_provenance.json` a lista de colunas observadas e ausentes, além do SHA-256 do pacote, do nome do CSV, do número nacional de linhas e da quantidade de escolas no município. Campo obrigatório faltante bloqueia o lote inteiro; campo opcional faltante aparece como nulo.

**Categorias de matrículas:** creche e pré-escola estão contidas na educação infantil; educação especial é recorte transversal e pode se sobrepor a outras etapas. Não somar todos os campos de etapa para recompor a matrícula básica, usando sempre `QT_MAT_BAS` como total oficial.\n\n**Qualidade temporal:** nenhuma série histórica será criada pela simples soma de microdados de anos diferentes; cada edição exigirá seu próprio dicionário e período. Situações de zero somente podem vir de campos declarados com zero. Indicadores municipais não são transformados em pontuações escolares.

**LGPD:** dados expostos limitados a cadastro institucional, infraestrutura, localização oficial e agregados escolares. Não publicar nomes de docentes ou estudantes, CPFs, NIS, matrículas individuais, endereços residenciais, atributos sensíveis ou recortes passíveis de reidentificação. Quando futuras fontes apresentarem pequenas contagens sensíveis, aplicar supressão e explicar a regra.

**Inspeção pós-deploy:** testar `dist/index.html`, `dist/data/summary.json`, `dist/data/schools.json`, `dist/data/schools.geojson`; conferir totais, referências e status além do resultado dos jobs. Homologação visual com navegadores e leitores de tela físicos ainda necessária.
