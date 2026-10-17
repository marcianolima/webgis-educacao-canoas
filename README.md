# WebGIS Educação Canoas

Plataforma WebGIS pública de inteligência educacional de Canoas/RS (IBGE **4304606**).

**Acesso previsto:** https://marcianolima.github.io/webgis-educacao-canoas/  
**GitHub Actions:** https://github.com/marcianolima/webgis-educacao-canoas/actions/workflows/deploy.yml

## Estado da versão 0.1

Frontend TypeScript + Vite + CSS responsivo, ECharts e MapLibre GL JS. A primeira página é o **Painel Municipal de Educação**, independente de qualquer escola escolhida. As abas incluem cadastro/mapa, matrículas, qualidade, infraestrutura, docentes, educação infantil, financiamento e metodologia; módulos ainda sem dados oficiais validados apresentam seu estado.

Snapshot inicial IBGE verificado: **347.657** habitantes (Censo 2022), **359.845** habitantes (estimativa 2026), escolarização de 6–14 anos **97,17%** (2022). Fonte: https://www.ibge.gov.br/cidades-e-estados/rs/canoas.html. Não são indicadores de matrículas por escola.

O coletor `scripts/inep_censo.py` está implementado para baixar e validar o pacote oficial de microdados do Censo Escolar **2025** durante o GitHub Actions. Une as tabelas **Escola, Matrícula e Docente** pelo identificador INEP, preservando diferenças metodológicas entre matrícula e função docente. **Até o workflow confirmar a extração nacional e a contagem municipal, escolas, matrículas e mapa escolar não devem ser apresentados como integrados.** Coleta incompleta conserva arquivos anteriores. Se o arquivo do INEP não possuir campos opcionais, preserva valores nulos.

## Organização

- `src/main.ts`: interface, navegação, filtros, mapa, fichas por código INEP, CSV e gráficos.
- `src/style.css`: identidade visual e temas claro/escuro.
- `public/data/`: snapshots municipais e dados cadastrais escolares públicos.
- `scripts/inep_censo.py`: processamento seletivo do ZIP anual sem armazenar microdados.
- `scripts/seduc_geo.py`: consulta ArcGIS REST SEDUC/RS (escolas 2023) por código INEP; preserva escola 2025 e fonte de coordenadas, ou constrói cadastro parcial georreferenciado de 2023 quando INEP ainda não validado.
- `tests/test_pipeline.py`: testes de chaves, coordenadas, agregados, privacidade e nulos.
- `.github/workflows/deploy.yml`: testes, coleta inicial/monitoramento mensal e GitHub Pages.
- `docs/FONTES.md`: matriz de fontes, granularidade, condições e limitações.
- `docs/METODOLOGIA.md`: dicionário, denominadores, confidencialidade e regras.
- `docs/ARQUITETURA.md`: arquitetura, ETL e procedimentos de operação.

## Desenvolvimento

Requer Node 22+ e Python 3.12+.

```bash
npm ci
python -m unittest discover -s tests -v
npm run dev
npm run build
```

Para coletar o INEP manualmente, quando houver rede e espaço temporário disponíveis: `python scripts/inep_censo.py`. O GitHub Actions também executa quando houver fonte INEP pendente na primeira publicação e mensalmente para checagem, e tenta integrar a camada SEDUC/RS de 2023 em coletor independente. Uma nova edição anual exige atualizar explicitamente o ano, a URL e o dicionário antes da publicação.

## Implantação e limitações

A publicação exige **Settings → Pages → Source: GitHub Actions** caso o fluxo não consiga habilitá-la automaticamente. O deploy verifica todos os JSONs após compilar. A existência do workflow não garante sucesso do download nem da habilitação do Pages: devem ser conferidos os logs e os números efetivos.

O WebGIS Saúde foi consultado somente como referência arquitetural; **nenhum arquivo de seu repositório é modificado por este projeto**.

Esta versão é um instrumento de exploração de dados públicos e não substitui sistemas oficiais da Secretaria Municipal da Educação, INEP ou FNDE. Não inclui dados pessoais de estudantes ou profissionais.
