# Diagnóstico de falhas e recuperação do GitHub Pages
Data: 17/10/2026 · WebGIS Educação Canoas

## Falhas objetivamente confirmadas no Actions

### 1. Validação do Python impedia qualquer execução posterior
Workflows anteriores à correção: jobs `validate` falhavam e os jobs `collect` e `deploy` eram pulados. A rotina `convert_row` não deve criar uma contagem de matrículas usando o cadastro da `Tabela_Escola`; essa contagem é lida posteriormente da `Tabela_Matricula`, vinculada por `CO_ENTIDADE`. O teste `test_conversion_and_coordinates` exigia indevidamente `enrollments=240` em uma linha cadastral e foi corrigido.

### 2. Erro TypeScript bloqueava a produção
Run `39038399359`, job `117412759877`:
```
src/main.ts(59,76): error TS2339: Property 'env' does not exist on type 'ImportMeta'.
src/main.ts(59,147): error TS2339: Property 'env' does not exist on type 'ImportMeta'.
```
Causa: `src/main.ts` usa `import.meta.env.BASE_URL` (Vite), mas o projeto não possuía a referência ao tipo de ambiente Vite. Correção em `src/vite-env.d.ts`, mantendo `/// <reference types="vite/client" />`.

### 3. Arquitetura CI/CD introduzia dependência desnecessária
Antes: o job de deploy aguardava a execução de downloads externos no job update, embora o site fosse estático. Agora:
- `deploy.yml`: valida e publica a última versão íntegra dos snapshots, independentemente de fonte externa;
- `update-data.yml`: coletor INEP + SEDUC, com rastreabilidade; falhas preservam os snapshots anteriores;
- `bootstrap-map.yml`: carrega rapidamente o catálogo geográfico de 2023 e realiza commit automático;
- `bootstrap-inep.yml`: primeira tentativa de carga 2025, apenas quando disparado.

## Resultados confirmados

**Coleta cartográfica:** execução [39038399463](https://github.com/marcianolima/webgis-educacao-canoas/actions/runs/39038399463), sucesso, 178 escolas e 178 coordenadas do serviço `SEDUC/Escolas_no_RS/MapServer/0`, referência 2023.

**Publicação:** execução [39038793085](https://github.com/marcianolima/webgis-educacao-canoas/actions/runs/39038793085) com `verify=success`, `deploy=success`. Artefatos HTML, CSS, JS, summary, escolas e GeoJSON verificados após `vite build`. O teste HTTP **após o deploy** consultou `https://marcianolima.github.io/webgis-educacao-canoas/` e confirmou:
- HTTP **200** para a página principal;
- HTTP **200** para o JS compilado;
- resposta válida de `data/summary.json`, `data/schools.json`, `data/schools.geojson`;
- **178 escolas e 178 pontos**, ano **2023**, na instância publicada.

**Teste Python:** 13 testes passaram no GitHub Actions. TypeScript foi verificado com `tsc --noEmit`; Vite gerou pacote de produção (564 módulos processados na execução de referência).

## Pendência externa não escondida

O Censo Escolar 2025 ainda não foi publicado. Na execução [39038656207](https://github.com/marcianolima/webgis-educacao-canoas/actions/runs/39038656207), o servidor `download.inep.gov.br` retornou, em tentativas separadas, `Connection reset by peer` e `SSL: CERTIFICATE_VERIFY_FAILED`. É uma falha real de transporte/autenticação TLS fora do frontend. A integração deve ser retomada somente por conexão autenticada, cadeia confiável ou cópia oficial verificável com checksum. Não usar `verify=False` indiscriminadamente.

## Limites da homologação

O teste HTTP valida que a aplicação e suas bases são acessíveis ao cliente e que os artefatos são íntegros; **não** substitui inspeção visual em navegadores reais, teste de leitores de tela, usabilidade de mapas em Android/iOS, nem validação municipal independente das escolas ativas em 2025.
