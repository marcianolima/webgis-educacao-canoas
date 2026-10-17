# Arquitetura e operação — WebGIS Educação Canoas

## Componentes
- **Frontend:** Vite 6, TypeScript, CSS modular próprio, MapLibre GL JS 4 e Apache ECharts 5. Publicação estática no GitHub Pages, caminho base `/webgis-educacao-canoas/`.
- **Dados públicos:** `public/data/summary.json` (indicadores municipais, status e proveniência); `schools.json` (cadastro individual público por INEP, inclusive sem coordenadas); `schools.geojson` (somente escolas com latitude/longitude conferidas); `inep_provenance.json` (quando coletado: integridade, nomes das colunas, cobertura, hash).
- **ETL:** Python 3.12, bibliotecas padrão, arquivo bruto ZIP temporário e CSV decodificado por stream; limite comprimido e descompactado; validação de cobertura e esquema antes de substituir arquivos.
- **Identificadores:** município IBGE 4304606, CO_MUNICIPIO INEP normalmente 430460; escola por código INEP de 8 algarismos.
- **CI/CD:** GitHub Actions, job `validate`, coleta condicional `collect`, job `deploy` com build TypeScript e inspeção dos arquivos dist.

## Contrato de dados
- `education.totalSchools` soma registros escolares do ano de referência; `activeSchools` considera TP_SITUACAO_FUNCIONAMENTO=1.
- `education.totalEnrollments` soma QT_MAT_BAS somente se esse campo existir e tiver valor em **todas** as escolas do recorte. Sem cobertura integral, publica **null** e não uma soma parcial.
- `infrastructure.{recurso}.yes/observed`: apenas resposta explícita de 1 ou 0 no campo IN_; ausentes excluídos do denominador; campo inexistente não aparece.
- `schools[].stages`: cada etapa recebe valor apenas se seu campo de 2025 realmente existir. Valores nulos não são transformados em zero.
- Coordenadas ausentes/fora dos limites geográficos plausíveis da cidade geram `null` e escola permanece na lista. Coordenadas da fonte não equivalem a levantamento de precisão.
- Nenhum indicador municipal IBGE é atribuído à escola. Fontes de IDEB, SAEB, FNDE pendentes não entram em cálculos nem são redistribuídas.

## Continuidade e riscos
Os ZIPs e CSVs nacionais nunca fazem parte do commit. A substituição dos snapshots ocorre apenas após conferência de cabeçalhos, quantidade de linhas nacionais, recorte de Canoas, unicidade dos INEP e geometria. Falhas de download mantêm a versão anterior, e o deploy do painel inicial continua possível. A CI registra `failure` no step de coleta, mas divulga aviso e preserva dados antigos. Frontend utiliza URLs relativas construídas com `import.meta.env.BASE_URL`. Testes de acessibilidade e navegadores físicos exigem homologação adicional.

## Implantação local
`npm ci`, `npm run dev`, `python -m unittest discover -s tests -v`, `npm run build`. Para disparo manual de coleta: `python scripts/inep_censo.py`; exige rede, espaço temporário e período suficiente, sem registrar brutos em disco permanente.

## Próxima evolução
Coletores separados: indicadores IDEB/SAEB, rendimento, distorção, FNDE/SIOPE e demografia SIDRA; validações cruzadas com Sinopse INEP; geocodificação orientada por geosserviços oficiais e posterior comparação geoespacial; filtros por etapa somente após integridade de campos e regras de interseção.
