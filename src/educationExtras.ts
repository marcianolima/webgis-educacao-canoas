import * as echarts from 'echarts';

type IdebEntry={year:number;initialMunicipal:number|null;finalMunicipal:number|null;highState:number|null};
type SaebStage={stage:string;portuguese:number|null;math:number|null};
type Quality={status:string;note:string;ideb:{sourcePrimary:string;secondarySources:string[];series:IdebEntry[]};saeb:{year:number;status:string;stages:SaebStage[];secondarySource:string;sourcePrimary:string}};
type FinanceYear={year:number;education:{committed:number|null;liquidated:number|null;paid:number|null};subfunctions:{earlyChildhood:{committed:number|null;liquidated:number|null;paid:number|null};specialEducation:{committed:number|null;liquidated:number|null;paid:number|null}}};
type Finance={source:string;unit:string;series:FinanceYear[];definition:string;annex:string;updatedAt:string};
let quality:Quality|null=null;
let finance:Finance|null=null;

export function setEducationExtras(a:unknown,b:unknown){
 const q=a as Quality|undefined;const f=b as Finance|undefined;
 quality=q?.ideb?.series&&Array.isArray(q.ideb.series)?q:null;
 finance=f?.series&&Array.isArray(f.series)?f:null;
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
 return '<section class="section" aria-label="Qualidade e financiamento municipal">'+
 '<div class="grid two">'+
 panel('Qualidade da educação · IDEB 2025','Rede municipal de Canoas · dados secundários corroborados',
  '<div class="grid" style="grid-template-columns:repeat(2,minmax(0,1fr));gap:10px">'+
  kpi('Anos iniciais',num(latest?.initialMunicipal),'IDEB 2025 · rede municipal')+
  kpi('Anos finais',num(latest?.finalMunicipal),'IDEB 2025 · rede municipal')+
  '</div><p class="lead">Confirmação cruzada em duas fontes secundárias. As planilhas oficiais do INEP permanecem pendentes de acesso confiável.</p><button class="button light" data-page="quality">Explorar evolução do IDEB e SAEB →</button>')+
 panel('Despesa com educação · 2025','Tesouro Nacional / SICONFI · DCA, função 12',
  '<div class="grid" style="gap:8px">'+kpi('Despesa empenhada',money(fin?.education.committed),'2025 · valor nominal · função 12')+
  '<button class="button light" data-page="finance">Ver execução financeira e série histórica →</button></div>')+
 '</div></section>';
}
export function qualityEducationPage(){
 if(!quality)return '<div class="empty">Dados de IDEB e SAEB ainda não disponíveis.</div>';
 const rows=quality.ideb.series;
 const last=rows.find(r=>r.year===2025);
 return '<div class="heading-row"><div><h2>Qualidade e aprendizagem</h2><p class="lead">IDEB por etapa e rede, com evolução histórica. Sem atribuir resultados municipais às escolas.</p></div><span class="tag">IDEB 2005–2025</span></div>'+
 '<div class="notice" role="status"><b>Proveniência e grau de confiança:</b> notas municipais compiladas e conferidas entre dois portais independentes que referenciam o INEP. Ainda não foram auditadas contra os arquivos originais do INEP 2025, indisponíveis no coletor. Resultados de escolas individuais continuam indisponíveis.</div>'+
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
 '<div class="grid kpis">'+kpi('Empenhado em '+last.year,money(last.education.committed),'Função educação · exercício '+last.year)+
 kpi('Liquidado em '+last.year,money(last.education.liquidated),'Função educação · exercício '+last.year)+
 kpi('Pago em '+last.year,money(last.education.paid),'Função educação · exercício '+last.year)+
 kpi('Educação infantil',money(last.subfunctions.earlyChildhood.committed),'Subfunção 12.365 · empenhado · parte do total')+'</div>'+
 '<div class="notice info"><b>Natureza dos recursos:</b> valores nominais informados pelo município ao Tesouro (DCA). Empenho, liquidação e pagamento são estágios da mesma despesa, portanto não devem ser somados. Educação Infantil é subfunção incluída na função Educação. Repasses PNAE/PDDE/FUNDEB são programas diferentes e permanecem em integração própria. Nenhum valor foi atribuído a escolas.</div>'+
 '<div class="section">'+panel('Evolução anual da despesa com educação','2019–2025 · valores nominais sem correção pelo IPCA',
 '<div id="finance-chart" class="chart" style="min-height:350px" role="img" aria-label="Série anual de despesas de educação por estágio"></div>'+
 '<div class="table-wrap"><table class="table"><thead><tr><th>Ano</th><th>Empenhado</th><th>Liquidado</th><th>Pago</th><th>Infantil (empenhado)</th></tr></thead><tbody>'+
 s.map(x=>'<tr><td>'+x.year+'</td><td>'+money(x.education.committed)+'</td><td>'+money(x.education.liquidated)+'</td><td>'+money(x.education.paid)+'</td><td>'+money(x.subfunctions.earlyChildhood.committed)+'</td></tr>').join('')+
 '</tbody></table></div>')+'</div>'+
 '<div class="section">'+panel('Programas FNDE e fonte oficial','FUNDEB, PNAE, PDDE e FNDE não devem ser tratados como sinônimos da função orçamentária 12',
 '<p class="lead">Os valores repassados para entes municipais e unidades executoras precisam de conciliação específica antes de entrar na aplicação. A série acima é exclusivamente a despesa declarada no SICONFI.</p>'+
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
