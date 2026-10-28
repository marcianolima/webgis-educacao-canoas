import * as echarts from 'echarts';
type Metrics={year:number;[key:string]:number|string|null};
type Data={municipalityCode:string;sourceURLs:Record<string,string>;
managementComplexity:Record<string,Metrics[]>;teacherAdequacy:Record<string,Metrics[]>;
schoolFlow:Record<string,Metrics[]>;socioeconomic:Record<string,Metrics[]>};
let data:Data|null=null;
const NETWORKS=['Municipal','Estadual','Federal','Privada','Todas'];
const names:Record<string,string>={Municipal:'Municipal',Estadual:'Estadual',Federal:'Federal',Privada:'Privada',Todas:'Todas as redes'};
export function setAdditionalIndicators(value:unknown){
 const x=value as Data|undefined;
 data=x?.municipalityCode==='4304606' && x.schoolFlow?.Municipal?.some(r=>r.year===2025)&&x.teacherAdequacy?.Municipal?.some(r=>r.year===2025)?x:null;
}
function get(key:'managementComplexity'|'teacherAdequacy'|'schoolFlow'|'socioeconomic',network:string,year:number){
 return data?.[key]?.[network]?.find(r=>r.year===year);
}
const fmt=(value:unknown,precision=1)=>typeof value==='number'&&Number.isFinite(value)?
 new Intl.NumberFormat('pt-BR',{minimumFractionDigits:precision,maximumFractionDigits:precision}).format(value):'—';
const esc=(s:unknown)=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]||c));
const panel=(title:string,subtitle:string,contents:string)=>'<section class="card pad section"><h3>'+title+'</h3><p class="sub">'+subtitle+'</p>'+contents+'</section>';
const kpi=(name:string,value:string,source:string)=>'<article class="card kpi"><span class="kpi-label">'+name+'</span><div class="kpi-value">'+value+'</div><span class="kpi-foot">'+source+'</span></article>';
export function officialPerformanceSummary(){
 if(!data)return '';
 const flow=get('schoolFlow','Municipal',2025);
 const teacher=get('teacherAdequacy','Municipal',2025);
 const management=get('managementComplexity','Municipal',2025);
 return '<section class="section"><h3>Rendimento, formação docente e gestão · 2025</h3>'+
 '<p class="lead">Fonte INEP/SEDUC-RS · indicadores da rede municipal, não de estabelecimentos individuais</p>'+
 '<div class="grid kpis section">'+
 kpi('Aprovação · ensino fundamental',fmt(flow?.aprov_fund)+'%','2025 · rede municipal')+
 kpi('Abandono · ensino fundamental',fmt(flow?.aband_fund)+'%','2025 · rede municipal')+
 kpi('Formação docente adequada · grupo 1',fmt(teacher?.['fund_total.g1'])+'%','2025 · fundamental · proporção de docências')+
 kpi('Complexidade média de gestão',fmt(management?.nivel_medio,2),'2025 · rede municipal')+'</div>'+
 '<div class="toolbar"><button class="button light" data-page="teachers">Explorar formação docente →</button><button class="button light" data-page="quality">Explorar rendimento →</button></div></section>';
}
export function teacherIndicatorsPage(){
 if(!data)return '<div class="empty">Indicadores docentes oficiais ainda não disponíveis.</div>';
 const x=get('teacherAdequacy','Municipal',2025);
 if(!x)return '<div class="empty">Adequação da formação docente não disponível para 2025.</div>';
 const stages:[string,string][]=[['Educação infantil','ed_inf'],['Ensino fundamental','fund_total'],
 ['Anos iniciais','fund_ai'],['Anos finais','fund_af'],['Ensino médio','medio']];
 return '<div class="heading-row"><div><h2>Docentes e formação adequada</h2><p class="lead">Adequação da formação docente (AFD) por rede e etapa · INEP/SEDUC-RS</p></div><span class="tag">Censo Escolar 2025</span></div>'+
 '<div class="notice info">Os cinco grupos representam proporções de <b>docências</b>, não a quantidade de professores únicos. O grupo 1 indica formação considerada adequada à etapa ou disciplina conforme metodologia INEP. Os resultados são da rede e não de cada escola individualmente.</div>'+
 '<div class="grid kpis">'+
 kpi('Grupo 1 · educação infantil',fmt(x['ed_inf.g1'])+'%','Rede municipal · 2025')+
 kpi('Grupo 1 · fundamental',fmt(x['fund_total.g1'])+'%','Rede municipal · 2025')+
 kpi('Grupo 1 · anos iniciais',fmt(x['fund_ai.g1'])+'%','Rede municipal · 2025')+
 kpi('Grupo 1 · anos finais',fmt(x['fund_af.g1'])+'%','Rede municipal · 2025')+'</div>'+
 panel('Adequação da formação por etapa','Distribuição percentual das docências entre os cinco grupos',
 '<div class="table-wrap"><table class="table"><thead><tr><th>Etapa</th><th>Grupo 1</th><th>Grupo 2</th><th>Grupo 3</th><th>Grupo 4</th><th>Grupo 5</th></tr></thead><tbody>'+
 stages.map(([name,key])=>'<tr><td>'+name+'</td>'+
 [1,2,3,4,5].map(i=>'<td>'+fmt(x[key+'.g'+i])+'%</td>').join('')+'</tr>').join('')+
 '</tbody></table></div>')+
 panel('Evolução do grupo 1 · Ensino Fundamental','Percentual de docências com formação adequada, rede municipal',
 '<div id="teacher-chart" class="chart" style="min-height:320px" role="img" aria-label="Evolução anual da adequação docente"></div>')+
 panel('Comparação de redes · 2025','Percentuais por rede e cobertura própria do indicador',
 '<div class="table-wrap"><table class="table"><thead><tr><th>Rede</th><th>Escolas abrangidas</th><th>Fundamental · grupo 1</th></tr></thead><tbody>'+
 NETWORKS.map(n=>{const v=get('teacherAdequacy',n,2025);return '<tr><td>'+names[n]+'</td><td>'+fmt(v?.total_escolas,0)+'</td><td>'+fmt(v?.['fund_total.g1'])+'%</td></tr>'}).join('')+
 '</tbody></table></div><p class="lead"><a href="'+esc(data.sourceURLs.teacherAdequacy)+'" target="_blank" rel="noopener noreferrer">Fonte oficial SEDUC/RS — AFD ↗</a></p>');
}
export function performanceContextPage(){
 if(!data)return '';
 const flow=get('schoolFlow','Municipal',2025);
 const icg=get('managementComplexity','Municipal',2025);
 const inse=get('socioeconomic','Municipal',2023);
 return '<div class="section">'+
 panel('Taxas de rendimento · Ensino Fundamental 2025','Aprovação, reprovação e abandono (%) por rede · dados oficiais INEP/SEDUC-RS',
 '<div class="grid kpis">'+kpi('Aprovação · municipal',fmt(flow?.aprov_fund)+'%','2025')+
 kpi('Reprovação · municipal',fmt(flow?.reprov_fund)+'%','2025')+
 kpi('Abandono · municipal',fmt(flow?.aband_fund)+'%','2025')+'</div>'+
 '<div class="table-wrap"><table class="table"><thead><tr><th>Rede</th><th>Aprovação</th><th>Reprovação</th><th>Abandono</th><th>Médio · aprovação</th></tr></thead><tbody>'+
 NETWORKS.map(n=>{const x=get('schoolFlow',n,2025);return '<tr><td>'+names[n]+'</td><td>'+fmt(x?.aprov_fund)+'%</td><td>'+fmt(x?.reprov_fund)+'%</td><td>'+fmt(x?.aband_fund)+'%</td><td>'+fmt(x?.aprov_med)+'%</td></tr>'}).join('')+
 '</tbody></table></div>')+
 panel('Evolução do rendimento escolar','Fundamental · rede municipal, conforme anos disponíveis',
 '<div id="school-flow-chart" class="chart" style="min-height:330px" role="img" aria-label="Série histórica de aprovação, reprovação e abandono"></div>')+
 panel('Complexidade da gestão escolar (ICG) · 2025','Distribuição de escolas pelos níveis 1–6 e índice médio da rede',
 '<div class="grid kpis">'+kpi('ICG médio · municipal',fmt(icg?.nivel_medio,2),'2025')+
 kpi('Escolas consideradas no ICG',fmt(icg?.total_escolas,0),'2025 · denominador próprio')+'</div>'+
 '<div class="table-wrap"><table class="table"><thead><tr><th>Rede</th><th>Escolas</th><th>ICG médio</th><th>N1</th><th>N2</th><th>N3</th><th>N4</th><th>N5</th><th>N6</th></tr></thead><tbody>'+
 NETWORKS.map(n=>{const x=get('managementComplexity',n,2025);return '<tr><td>'+names[n]+'</td><td>'+fmt(x?.total_escolas,0)+'</td><td>'+fmt(x?.nivel_medio,2)+'</td>'+
 [1,2,3,4,5,6].map(i=>'<td>'+fmt(x?.['nivel_'+i+'.pct'])+'%</td>').join('')+'</tr>'}).join('')+
 '</tbody></table></div>')+
 panel('Índice de nível socioeconômico (INSE) · referência 2023','Última edição observada. Não há valor 2025 nesta planilha e ele não será estimado.',
 '<div class="grid kpis">'+kpi('INSE · municipal',fmt(inse?.inse,2),'Referência 2023')+
 kpi('Nível socioeconômico',esc(inse?.nivel||'Não disponível'),'Rede municipal · 2023')+'</div>'+
 '<div class="table-wrap"><table class="table"><thead><tr><th>Rede</th><th>INSE</th><th>Nível</th><th>Escolas da amostra</th><th>Alunos da amostra</th></tr></thead><tbody>'+
 NETWORKS.map(n=>{const x=get('socioeconomic',n,2023);return '<tr><td>'+names[n]+'</td><td>'+fmt(x?.inse,2)+'</td><td>'+esc(x?.nivel||'—')+'</td><td>'+fmt(x?.n_escolas,0)+'</td><td>'+fmt(x?.n_alunos,0)+'</td></tr>'}).join('')+
 '</tbody></table></div><p class="lead">A cobertura do INSE não equivale ao universo do Censo Escolar 2025. O indicador é por município e rede, não por estabelecimento.</p>')+
 '</div>';
}
export function mountAdvancedChart(page:'teachers'|'quality',dark:boolean){
 if(!data)return null;
 const id=page==='teachers'?'teacher-chart':'school-flow-chart';
 const target=document.getElementById(id);if(!target)return null;
 const rows=page==='teachers'?data.teacherAdequacy.Municipal:data.schoolFlow.Municipal;
 const chart=echarts.init(target,dark?'dark':undefined);
 const series=page==='teachers'?[
 {name:'Grupo 1 · fundamental',type:'line',connectNulls:false,data:rows.map(r=>r['fund_total.g1'])}
 ]:['aprov','reprov','aband'].map(label=>({
 name:label==='aprov'?'Aprovação':label==='reprov'?'Reprovação':'Abandono',type:'line',connectNulls:false,
 data:rows.map(r=>r[label+'_fund'])
 }));
 chart.setOption({animation:!window.matchMedia('(prefers-reduced-motion: reduce)').matches,backgroundColor:'transparent',tooltip:{trigger:'axis'},legend:{top:0},
 grid:{top:60,bottom:45,left:55,right:18},
 xAxis:{type:'category',data:rows.map(r=>String(r.year))},
 yAxis:{type:'value',min:0,max:100,axisLabel:{formatter:'{value}%'}},
 series});
 return chart;
}
