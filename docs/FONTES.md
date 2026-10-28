# Matriz de fontes — auditoria 1.0 (27/10/2026)

**Integrada** significa que dados numéricos foram coletados, conferidos e publicados em `public/data/`. **Catalogada** significa que há referência para pesquisa, mas nenhum valor municipal novo foi importado automaticamente. A chave municipal é IBGE **4304606**; escolas, INEP de **8 dígitos**.

| Fonte | Escala, período | Estado | Cautela de uso |
|---|---|---|---|
| [INEP Censo Escolar](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar) | Escola, 2025 V2 | Integrada; ZIP verificado por SHA-256 | 204 registros, 196 ativos, 68.490 matrículas; arquivo sem coordenadas |
| [INEP IDEB](https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb/resultados) | Município/rede/escola, 2005–2025 | Integrada | Resultado por escola só quando divulgado; não extrapolar |
| [SEDUC/RS escolas](https://iede.rs.gov.br/server/rest/services/SEDUC/Escolas_no_RS/MapServer/0) | Escola, geometria 2023 | Integrada parcialmente | 169 registros do catálogo 2025 com ponto conciliado |
| [Dados abertos SEDUC/RS](https://dados.rs.gov.br/) | Município e redes, 2010–2025 | Integrada | Matrículas, rendimento, infraestrutura, docentes, SAEB estadual |
| [IBGE Censo e SIDRA](https://sidra.ibge.gov.br/) | Residentes, 2022 | Integrada | Residentes por idade não equivalem a matrículas ou vagas |
| [Tesouro Nacional SICONFI](https://apidatalake.tesouro.gov.br/ords/cdwhprd/siconfi/tt/dca) | Município, 2019–2025 | Integrada | DCA anexo I-E, função 12, empenho, liquidação e pagamento distintos |
| [FNDE Dados Abertos](https://www.gov.br/fnde/pt-br/acesso-a-informacao/dados-abertos/o-que-se-pode-acessar) | Município/ente e escola | Parcial | PNAE previsão 2024; Valor_Repasse 2009–2025; PNATE a pagar; PDDE 2025 por escola consultada |
| [INEP Indicadores Educacionais](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais) | Município/rede/escola conforme indicador | Catalogada | Distorção idade-série, regularidade/esforço docente, turma e horas-aula |
| [INEP resultados Censo Escolar](https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/censo-escolar/resultados) | Anual, inclusive 2026 | Catalogada | Distinguir divulgação preliminar de resultados definitivos |
| [TCE-RS](https://tcers.tc.br/) | Fiscalização municipal | Catalogada | Não distribuir empenhos por escola sem lançamento individual |
| [UNICEF Busca Ativa Escolar](https://www.unicef.org/brazil/innocenti/busca-ativa-escolar) | Metodologia | Catalogada | Não importar dados pessoais ou casos de crianças |
| [QEdu](https://qedu.org.br/), [Fundação Abrinq](https://observatoriocrianca.org.br/) | Dados e indicadores derivados | Catalogada | Conferência secundária, não substitui a publicação primária |

## Controle de qualidade

1. Verificar autoridade, competência, arquivo original e SHA256, quando aplicável.
2. Filtrar município e rede antes de agregar ou mapear; ligar escolas por código INEP.
3. Diferenciar valor *previsto*, *informado como repassado*, *a pagar*, *liquidado* e *pago*.
4. Manter `null` quando falta valor; não confundir ausência com zero.
5. Preservar o último arquivo validado quando um endpoint estiver indisponível; divergência de conteúdo deve interromper publicação.
6. Nunca inferir coordenadas de endereços sem validação cartográfica; dados do Censo 2025 e geometria 2023 têm competências distintas.

Mais detalhes em `docs/METODOLOGIA.md`, `public/data/`, `scripts/` e na execução de Actions correspondente.
