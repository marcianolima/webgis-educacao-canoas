import * as echarts from 'echarts';

type IdebEntry={year:number;initialMunicipal:number|null;finalMunicipal:number|null;highState:number|null};
type SaebStage={stage:string;portuguese:number|null;math:number|null};
type Quality={status:string;note:string;ideb:{sourcePrimary:string;secondarySources:string[];series:IdebEntry[]};saeb:{year:number;status:string;stages:SaebStage[];secondarySource:string;sourcePrimary:string}};
type FinanceYear={year:number;education:{committed:number|null;liquidated:number|null;paid:number|null};subfunctions:{earlyChildhood:{committed:number|null;liquidated:number|null;paid:number|null};specialEducation:{committed:number|null;liquidated:number|null;paid:number|null}}};
type Finance={source:string;unit:string;series:FinanceYear[];definition:string;annex:string;updatedAt:string};
type Pnae={year:number;municipalityCode:number;fundingStatus:"planned";totalPlannedBRL:number;source:string;definition:string;actions:{code:string;name:string;studentsForAction:number;amountPlannedBRL:number}[]};
let quality:Quality|null=null;
type RSOfficial={municipalityCode:string;sourceAgency:string;sourceURLs:{ideb:string;saeb:string};idebByNetwork:Record<string,{year:number;[key:string]:number|null}[]>;saebStateByMunicipality:{year:number;[key:string]:number|null}[]};
let officialRS:RSOfficial|null=null;
export function setOfficialQuality(value:unknown){
 const v=value as RSOfficial|undefined;
 if(v?.municipalityCode!=='4304606'||!v.idebByNetwork?.Municipal?.some(x=>x.year===2025))return;
 officialRS=v;
 if(!quality)return;
 quality.ideb.series=v.idebByNetwork.Municipal.map(x=>({
  year:x.year,
  initialMunicipal:x['AI.ideb']??null,
  finalMunicipal:x['AF.ideb']??null,
  highState:v.idebByNetwork.Estadual.find(r=>r.year===x.year)?.['EM.ideb']??null,
 }));
}

let finance:Finance|null=null;
let pnae:Pnae|null=null;
type PNAETransfer={year:number;studentsConsidered:number;schoolsServed:number;reportedTransferredBRL:number|null};
type FndeTransfers={municipalityCode:string;pnae:{series:PNAETransfer[];sourcePage:string;measure:string};pnate:{totalToPayBRL:number;toPayBRL:Record<string,number>;reportedAt:string;measure:string;sourcePage:string}};
let transfers:FndeTransfers|null=null;

export function setEducationExtras(a:unknown,b:unknown,c?:unknown,d?:unknown){
 const q=a as Quality|undefined;const f=b as Finance|undefined;
 quality=q?.ideb?.series&&Array.isArray(q.ideb.series)?q:null;
 finance=f?.series&&Array.isArray(f.series)?f:null;
 const p=c as Pnae|undefined;
 pnae=p?.municipalityCode===4304606 && p.fundingStatus==="planned" && Array.isArray(p.actions)?p:null;
 const t=d as FndeTransfers|undefined;
 transfers=t?.municipalityCode==="4304606" && Array.isArray(t.pnae?.series)?t:null;
}
const esc=(v:unknown)=>String(v??'').replace(/[&<>"']/g,x=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[x]||x));
const num=(v:number|null|undefined,dec=1)=>v===null||v===undefined?'—':new Intl.NumberFormat('pt-BR',{maximumFractionDigits:dec,minimumFractionDigits:dec}).format(v);
const money=(v:number|null|undefined)=>v===null||v===undefined?'Não disponível':new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL',maximumFractionDigits:2}).format(v);
const kpi=(head:string,value:string,source:string)=>'<article class="card kpi"><span class="kpi-label">'+esc(head)+'</span><div class="kpi-value">'+esc(value)+'</div><span class="kpi-foot">'+esc(source)+'</span></article>';
const panel=(title:string,desc:string,body:string)=>'<section class="card pad"><h3>'+esc(title)+'</h3><p class="sub">'+esc(desc)+'</p>'+body+'</section>';
const link=(url:string,label:string)=>/^https:\/\//.test(url)?'<a target="_blank" rel="noopener noreferrer" href="'+esc(url)+'">'+esc(label)+' ↗</a>':'';

export function municipalEducationExtras(){
 if(!quality&&!finance)return '';
 const latest=quality?.ideb?.series.find(s=>s.year===2025);
 const fin=finance?.series.find(s=>s.year===2025);
 const paid2025=transfers?.pnae.series.find(s=>s.year===2025);
 return '<section class="section" aria-label="Qualidade e financiamento municipal">'+
 '<div class="grid two">'+
 panel('Qualidade da educação · IDEB 2025',officialRS?'Rede municipal · SEDUC/RS, resultados oficiais INEP':'Rede municipal · dados secundários corroborados',
  '<div class="grid" style="grid-template-columns:repeat(2,minmax(0,1fr));gap:10px">'+
  kpi('Anos iniciais',num(latest?.initialMunicipal),'IDEB 2025 · rede municipal')+
  kpi('Anos finais',num(latest?.finalMunicipal),'IDEB 2025 · rede municipal')+
  '</div>'+(officialRS?'<p class="lead">Série oficial do IDEB 2005–2025, publicada pela SEDUC/RS com base nos resultados INEP; valores por estabelecimento são tratados separadamente.</p>':'<p class="lead">Confirmação cruzada em duas fontes secundárias; aguarda validação oficial.</p>')+'<button class="button light" data-page="quality">Explorar evolução do IDEB e SAEB →</button>')+
 panel('Despesa com educação · 2025','Tesouro Nacional / SICONFI · DCA, função 12',
  '<div class="grid finance-summary" style="gap:8px">'+kpi('Despesa empenhada',money(fin?.education.committed),'2025 · valor nominal · função 12')+
  '<button class="button light" data-page="finance">Ver execução financeira e série histórica →</button></div>')+
 '</div>'+
 (paid2025?'<div class="notice info"><b>PNAE 2025 · campo Valor_Repasse informado pelo FNDE:</b> '+money(paid2025.reportedTransferredBRL)+' · '+new Intl.NumberFormat('pt-BR').format(paid2025.schoolsServed)+' escolas atendidas · '+new Intl.NumberFormat('pt-BR').format(paid2025.studentsConsidered)+' alunos considerados. Indicadores por ente executor, não por escola. <button class="button light" data-page="finance">Ver série histórica →</button></div>':'')+
 (pnae?'<div class="notice info"><b>PNAE '+pnae.year+':</b> previsão de repasses FNDE para o Município de Canoas: '+money(pnae.totalPlannedBRL)+'. Trata-se de <b>valor previsto</b>, não comprovante de transferência. <button class="button light" data-page="finance">Detalhar ações →</button></div>':'')+
 '</section>';
}
export function qualityEducationPage(){
 if(!quality)return '<div class="empty">Dados de IDEB e SAEB ainda não disponíveis.</div>';
 const rows=quality.ideb.series;
 const last=rows.find(r=>r.year===2025);
 return '<div class="heading-row"><div><h2>Qualidade e aprendizagem</h2><p class="lead">IDEB por etapa e rede, com evolução histórica. Sem atribuir resultados municipais às escolas.</p></div><span class="tag">IDEB 2005–2025</span></div>'+
 (officialRS?
 '<div class="notice info" role="status"><b>Fonte primária conciliada:</b> IDEB por rede e município, série 2005–2025 elaborada pela SEDUC/RS a partir dos resultados oficiais do INEP; referência de 2025 validada. Resultados individuais por escola só aparecem quando divulgados em arquivo próprio.</div>':
 '<div class="notice" role="status"><b>IDEB municipal em conferência:</b> por enquanto, valores de fontes secundárias; aguarda processamento das planilhas oficiais.</div>')+
 '<div class="grid kpis">'+kpi('IDEB 2025 — anos iniciais',num(last?.initialMunicipal),'Rede municipal · índice de 0 a 10')+
 kpi('IDEB 2025 — anos finais',num(last?.finalMunicipal),'Rede municipal · índice de 0 a 10')+
 kpi('IDEB 2025 — ensino médio',num(last?.highState),'Rede estadual · não municipal')+
 '</div>'+
 '<div class="section">'+panel('Evolução do IDEB por etapa','Os valores ausentes não representam zero · eixo de 0 a 10',
 '<div id="quality-chart" class="chart" style="min-height:360px" role="img" aria-label="Evolução de IDEB 2005 a 2025"></div>'+
 '<div class="table-wrap"><table class="table"><thead><tr><th>Ano</th><th>Iniciais (municipal)</th><th>Finais (municipal)</th><th>Ensino médio (estadual)</th></tr></thead><tbody>'+
 rows.map(s=>'<tr><td>'+s.year+'</td><td>'+num(s.initialMunicipal)+'</td><td>'+num(s.finalMunicipal)+'</td><td>'+num(s.highState)+'</td></tr>').join('')+
 '</tbody></table></div>')+'</div>'+
 '<div class="section">'+panel('SAEB 2025 — proficiência','Rede municipal de Canoas · pontos na escala SAEB · valor secundário em validação adicional',
 '<div class="table-wrap"><table class="table"><thead><tr><th>Etapa</th><th>Língua Portuguesa</th><th>Matemática</th></tr></thead><tbody>'+
 quality.saeb.stages.map(s=>'<tr><td>'+esc(s.stage)+'</td><td>'+num(s.portuguese)+'</td><td>'+num(s.math)+'</td></tr>').join('')+
 '</tbody></table></div><p class="lead">A escala SAEB não equivale à escala IDEB. Proficiências escolares dependem de critérios de divulgação do INEP.</p>')+'</div>'+
 (officialRS?'<div class="section">'+panel('SAEB 2025 · rede ESTADUAL em Canoas','Média de proficiência da rede estadual nos estabelecimentos do município; não equivale à nota da rede municipal',
 '<div class="table-wrap"><table class="table"><thead><tr><th>Etapa</th><th>Língua Portuguesa</th><th>Matemática</th></tr></thead><tbody>'+
 ([
  ['5º ano EF','5EF'],['9º ano EF','9EF'],['Ensino Médio','EM']
 ] as [string,string][]).map(([name,k])=>{
  const r=officialRS?.saebStateByMunicipality.find(s=>s.year===2025);
  return '<tr><td>'+name+'</td><td>'+num(r?.[k+'.media_lp'])+'</td><td>'+num(r?.[k+'.media_mt'])+'</td></tr>';
 }).join('')+'</tbody></table></div>'+
 '<p class="lead">'+link(officialRS.sourceURLs.saeb,'SEDUC/RS · planilha SAEB por rede e município')+'</p>')+'</div>':'')+
 '<div class="section">'+panel('Fontes e interpretação','Conferência por mais de uma publicação, sem substituir o dado primário',
 '<div class="grid" style="gap:10px">'+link(quality.ideb.sourcePrimary,'INEP — resultados originais IDEB 2025')+
 quality.ideb.secondarySources.map((u,i)=>link(u,'Fonte secundária '+(i+1))).join('')+
 link(quality.saeb.sourcePrimary,'INEP — resultados originais SAEB 2025')+
 link(quality.saeb.secondarySource,'SAEB · fonte complementar')+'</div>')+'</div>';
}
export function financeEducationPage(){
 if(!finance)return '<div class="empty">A integração oficial SICONFI ainda não foi concluída.</div>';
 const s=finance.series;
 const last=s.find(x=>x.year===2025)||s[s.length-1];
 if(!last)return '<div class="empty">Sem exercícios financeiros verificados.</div>';
 return '<div class="heading-row"><div><h2>Financiamento público da educação</h2><p class="lead">Execução orçamentária municipal · DCA Anexo I-E, Função 12.</p></div><span class="tag">Tesouro Nacional · 2019–2025</span></div>'+
 '<div class="grid kpis finance-kpis">'+kpi('Empenhado em '+last.year,money(last.education.committed),'Função educação · exercício '+last.year)+
 kpi('Liquidado em '+last.year,money(last.education.liquidated),'Função educação · exercício '+last.year)+
 kpi('Pago em '+last.year,money(last.education.paid),'Função educação · exercício '+last.year)+
 kpi('Educação infantil',money(last.subfunctions.earlyChildhood.committed),'Subfunção 12.365 · empenhado · parte do total')+'</div>'+
 '<div class="notice info"><b>Natureza dos recursos:</b> valores nominais informados pelo município ao Tesouro (DCA). Empenho, liquidação e pagamento são estágios da mesma despesa, portanto não devem ser somados. Educação Infantil é subfunção incluída na função Educação. Repasses PNAE/PDDE/FUNDEB são programas diferentes e permanecem em integração própria. Nenhum valor foi atribuído a escolas.</div>'+
 '<div class="section">'+panel('Evolução anual da despesa com educação','2019–2025 · valores nominais sem correção pelo IPCA',
 '<div id="finance-chart" class="chart" style="min-height:350px" role="img" aria-label="Série anual de despesas de educação por estágio"></div>'+
 '<div class="table-wrap"><table class="table"><thead><tr><th>Ano</th><th>Empenhado</th><th>Liquidado</th><th>Pago</th><th>Infantil (empenhado)</th></tr></thead><tbody>'+
 s.map(x=>'<tr><td>'+x.year+'</td><td>'+money(x.education.committed)+'</td><td>'+money(x.education.liquidated)+'</td><td>'+money(x.education.paid)+'</td><td>'+money(x.subfunctions.earlyChildhood.committed)+'</td></tr>').join('')+
 '</tbody></table></div>')+'</div>'+
 (transfers?'<div class="section">'+panel('PNAE · valores informados como repassados ao município','FNDE · Plataforma Antonieta de Barros, produto 82 · por ente executor, não por unidade escolar',
 '<div class="grid finance-kpis">'+
 kpi('PNAE 2025 · Valor_Repasse',money(transfers.pnae.series.find(y=>y.year===2025)?.reportedTransferredBRL),'FNDE · exercício 2025 · Prefeitura de Canoas')+
 kpi('Escolas atendidas 2025',num(transfers.pnae.series.find(y=>y.year===2025)?.schoolsServed,0),'PNAE 2025 · escolas do programa, não total censitário')+
 kpi('Alunos considerados 2025',num(transfers.pnae.series.find(y=>y.year===2025)?.studentsConsidered,0),'PNAE 2025 · não estudantes únicos do município')+
 '</div><div class="table-wrap"><table class="table"><thead><tr><th>Ano</th><th>Valor_Repasse</th><th>Alunos considerados</th><th>Escolas atendidas</th></tr></thead><tbody>'+
 transfers.pnae.series.slice().reverse().map(v=>'<tr><td>'+v.year+'</td><td>'+money(v.reportedTransferredBRL)+'</td><td>'+num(v.studentsConsidered,0)+'</td><td>'+num(v.schoolsServed,0)+'</td></tr>').join('')+'</tbody></table></div>'+
 '<p class="lead">Campo oficial <code>Valor_Repasse</code>. O arquivo não contém repasses individualizados às escolas, nem identifica parcelas por data. O ano de 2026 ainda aparece sem valor nesse arquivo e não deve ser interpretado como zero.</p>'+
 '<p class="lead">'+link(transfers.pnae.sourcePage,'FNDE · produto 82')+'</p>')+'</div>':'')+
 (transfers?'<div class="section">'+panel('PNATE · valores a pagar (não pagamentos realizados)','FNDE · produto 56 · arquivo com referência de atualização própria e competência não presumida',
 '<div class="grid finance-kpis">'+kpi('Valor a pagar · PNATE',money(transfers.pnate.totalToPayBRL),'Colunas vl_pagar_* · registro consultado, não pagamento')+'</div>'+
 '<p class="lead">A planilha registra a delegação da rede estadual e valores a pagar por etapa. O total é uma obrigação indicada, não um comprovante de repasse, despesa liquidada ou efetivamente paga.</p>'+
 '<p class="lead">'+link(transfers.pnate.sourcePage,'FNDE · produto 56')+'</p>')+'</div>':'')+
  (pnae?'<div class="section">'+panel('PNAE · previsão de repasses por ação ('+pnae.year+')','FNDE · ente executor Prefeitura de Canoas · valores previstos, não pagos',
 '<div class="grid finance-kpis">'+kpi('Total previsto PNAE',money(pnae.totalPlannedBRL),'Fonte FNDE · ano '+pnae.year)+'</div>'+
 '<div class="table-wrap"><table class="table"><thead><tr><th>Ação</th><th>Alunos considerados nesta ação</th><th>Valor previsto</th></tr></thead><tbody>'+
 pnae.actions.map(a=>'<tr><td>'+esc(a.name)+' ('+esc(a.code)+')</td><td>'+new Intl.NumberFormat('pt-BR').format(a.studentsForAction)+'</td><td>'+money(a.amountPlannedBRL)+'</td></tr>').join('')+'</tbody></table></div>'+
 '<p class="lead">Os alunos de diferentes ações podem se sobrepor; essas contagens não devem ser somadas como estudantes únicos. A previsão não é evidência de pagamento e não representa recursos repassados diretamente às escolas.</p>'+
 '<p class="lead">'+link(pnae.source,'Planilha oficial FNDE 2024')+'</p>')+'</div>':'')+
 '<div class="section">'+panel('Programas FNDE e fonte oficial','FUNDEB, PNAE, PDDE e FNDE não devem ser tratados como sinônimos da função orçamentária 12',
 '<p class="lead">O PNAE por ente está integrado e o PNATE apresenta valores a pagar. O PDDE por escola e os pagamentos bancários detalhados ainda exigem reconciliação própria. A série SICONFI permanece separada.</p>'+
 '<p class="lead">'+link('https://apidatalake.tesouro.gov.br/docs/siconfi/','SICONFI · documentação da API')+' · '+link('https://www.gov.br/fnde/pt-br/acesso-a-informacao/dados-abertos','FNDE · dados abertos')+'</p>')+'</div>';
}
export function mountEducationChart(page:'quality'|'finance',isDark:boolean):echarts.ECharts|null{
 const el=document.getElementById(page==='quality'?'quality-chart':'finance-chart');
 if(!el)return null;
 const years=page==='quality'?quality?.ideb.series.map(x=>x.year)||[]:finance?.series.map(x=>x.year)||[];
 const chart=echarts.init(el,isDark?'dark':undefined);
 const data=page==='quality'?[
  {name:'Anos iniciais · Municipal',data:quality?.ideb.series.map(x=>x.initialMunicipal)||[]},
  {name:'Anos finais · Municipal',data:quality?.ideb.series.map(x=>x.finalMunicipal)||[]},
  {name:'Ensino médio · Estadual',data:quality?.ideb.series.map(x=>x.highState)||[]}
 ]:[
  {name:'Empenhada',data:finance?.series.map(x=>x.education.committed)||[]},
  {name:'Liquidada',data:finance?.series.map(x=>x.education.liquidated)||[]},
  {name:'Paga',data:finance?.series.map(x=>x.education.paid)||[]}
 ];
 chart.setOption({
  backgroundColor:'transparent',
  legend:{top:0,textStyle:{color:isDark?'#d6e8ee':'#496579'}},
  tooltip:{trigger:'axis'},
  grid:{top:65,bottom:40,left:page==='finance'?95:48,right:20},
  xAxis:{type:'category',data:years.map(String),axisLabel:{color:isDark?'#d6e8ee':'#496579'}},
  yAxis:{type:'value',min:page==='quality'?0:undefined,max:page==='quality'?10:undefined,
   axisLabel:{formatter:page==='finance'?((value:number)=>(value/1e6).toFixed(0)+' mi'):undefined,
   color:isDark?'#d6e8ee':'#496579'}},
  series:data.map(x=>({name:x.name,type:'line',connectNulls:false,smooth:false,data:x.data,symbolSize:7}))
 });
 return chart;
}

export function trustedEducationSources(){
 const sources=[
  ['Todos Pela Educação','Anuário Brasileiro da Educação Básica 2026, recorte RS','Contextualização estadual e nacional, com metodologia INEP; não confundir com indicadores de Canoas.','https://anuario.todospelaeducacao.org.br/2026/estados-rs.html'],
  ['UNICEF / Undime','Busca Ativa Escolar','Metodologia de combate à exclusão e abandono; dados individuais e plataforma de casos não são públicos.','https://www.unicef.org/brazil/innocenti/busca-ativa-escolar'],
  ['Fundação Abrinq','Observatório da Criança e do Adolescente','Indicadores territoriais de infância e adolescência, com acesso a metadados e fontes originais; extração municipal pendente.','https://observatoriocrianca.org.br/'],
  ['Fundação Maria Cecilia Souto Vidigal','Primeira Infância em Dados','Mais de 40 indicadores municipais: creches, pré-escola e primeira infância; download condicionado a cadastro não automatizado.','https://fundacaomariacecilia.org.br/o-que-fazemos/portal-primeira-infancia-em-dados/'],
  ['Instituto Unibanco','Observatório de Educação','Análises integradas de fluxo, desempenho e desigualdades, com foco especial no ensino médio.','https://observatoriodeeducacao.institutounibanco.org.br/educacao-em-numeros/analises-integradas'],
  ['QEdu / ecossistema Fundação Lemann','Painéis com dados oficiais reorganizados','Referência de conferência cruzada de escolas, IDEB e infraestrutura; não substituir INEP ou atribuir granularidade não comprovada.','https://qedu.org.br/'],
  ['INEP · Indicadores Educacionais','Catálogo de indicadores oficiais','Novas séries de distorção idade-série, regularidade e esforço docente, média de alunos por turma e horas-aula. Disponibilidade e granularidade ainda precisam de reconciliação.','https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais'],
  ['INEP · Censo Escolar','Resultados anuais','Edições e tabelas de matrícula inicial, incluindo 2026. Verificar estágio preliminar/definitivo e nunca misturar com dados de 2025.','https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/censo-escolar/resultados'],
  ['FNDE · Dados Abertos','Programas e execução financeira','Fontes para FUNDEB, PNATE, PDDE, PNAE, PNLD e infraestrutura escolar; importação apenas após validação de competência, entidade e estágio financeiro.','https://www.gov.br/fnde/pt-br/acesso-a-informacao/dados-abertos/o-que-se-pode-acessar']
 ];
 return '<div class="section">'+panel('Organizações e plataformas de apoio','Fontes complementares confiáveis; apenas catalogadas, sem importar informações de crianças ou números não conciliados',
 '<div class="grid" style="gap:12px">'+sources.map(([name,title,note,url])=>'<div class="source"><b>'+esc(name)+' — '+esc(title)+'</b><p>'+esc(note)+'</p>'+link(url,'Visitar fonte e metodologia')+'</div>').join('')+'</div>')+'</div>';
}
