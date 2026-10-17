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
