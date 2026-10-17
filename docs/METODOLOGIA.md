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


## PNAE 2024: natureza do valor e sobreposição
A planilha `Previsão Repasse Financeiro PNAE - 2024` do FNDE apresenta `ENTIDADE_RESP=PREF MUN DE CANOAS`, `UF=RS`, `ACAO`, `QTDE_ALUNO` e `VALOR_PREVISTO`. O número financeiro divulgado é **previsão**, não transferência, empenho ou valor pago. A soma das cinco ações é R$ 5.895.260,80, verificada contra as linhas de origem. Os alunos considerados em AEE e demais ações podem se sobrepor; não somar como estudantes únicos nem distribuir às escolas. O arquivo público `pnae.json` armazena o SHA-256 do XLSX oficial.

## Faixas etárias — Censo 2022
A tabela IBGE/SIDRA 9514 traz idade simples por residência. O coletor usa `c2/0` (sexo total) e a dimensão total da forma de declaração da idade, reconcilia valores de 0 a 24 anos com grupos quinquenais e população total do Censo 2022 (347.657). As faixas publicadas são 0–3, 4–5, 6–14, 15–17, 18–24 e 0–17; o último é agregado dos anteriores até 17, não uma faixa mutuamente exclusiva em gráficos. Os valores não expressam demanda por vagas nem população projetada para 2026.

## Oferta escolar da IDE SEDUC
`etapas_modalidade`, `porte_escola`, `localizacao` e outros campos descritivos são de fonte geoespacial oficial com referência cartográfica INEP 2023. Etapas podem se sobrepor, portanto contagens por etapa não são somáveis para número único de escolas. A camada contém valores `num_matriculas` e `num_turmas` em escolas estaduais, mas o período próprio dessas quantidades não está documentado; a visualização individual inclui ressalva e não converte esses registros em totais municipais.

## Política de conciliação 2025
População de referência: 2025 Censo Escolar por localização do estabelecimento, rede administrativa, município 4304606, não residentes nem estudantes únicos. O conjunto SEDUC/RS contém 196 escolas e 68.490 matrículas em Canoas, 82 escolas e 30.597 matrículas municipais. O mapa geográfico 2023 contém 178 pontos e não pode ser somado ou comparado como mesma cobertura.
PDDE Info: consultas unitárias por código INEP e ano; usar apenas colunas Valor Pago Total e Data do Pagamento, ignorar linhas Subtotal, conferir com TOTAL GERAL. Ausência de resposta não significa zero. Valor agregado publicado apenas para respondentes, não total municipal censitário. Não publicar contas, agências, saldos bancários ou identificadores pessoais.


## Indicadores educacionais de rendimento e docência — 2025
Rendimento: aprovação, reprovação e abandono são taxas (%) por etapa e rede, somando aproximadamente 100% por etapa quando a informação é divulgada. Exemplo municipal, fundamental 2025: 89,1% + 9,8% + 1,1% = 100%.
AFD: adequação da formação docente (grupos 1–5) refere-se à proporção de **docências** e não número de professores distintos. Grupo 1 representa formação considerada adequada conforme INEP. O número de escolas consideradas na AFD não equivale ao número total de matrículas.
ICG: complexidade da gestão escolar por escola, agregada por rede/município e níveis 1–6; média e percentuais possuem denominador específico. Não transformar média da rede em ICG individual.
INSE: indicador socioeconômico com última referência observada de **2023**, não 2025; os estudantes da amostra INSE não são todos os matriculados.
