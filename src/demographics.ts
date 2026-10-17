import * as echarts from 'echarts';
type Demography={municipalityCode:string;year:number;totalPopulation:number;ageGroups:Record<string,number>;source:string;definition:string};
let demographic:Demography|null=null;
export function setDemography(value:unknown){
 const d=value as Demography|undefined;
 demographic=d?.municipalityCode==='4304606' && d.year===2022 && d.totalPopulation===347657 && d.ageGroups?.['0–17 anos']>0?d:null;
}
const fmt=(x:number|null|undefined)=>x==null?'Não disponível':new Intl.NumberFormat('pt-BR').format(x);
const esc=(s:string)=>s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]||c));
const card=(label:string,n:number|null|undefined,foot:string)=>'<article class="card kpi"><span class="kpi-label">'+esc(label)+'</span><div class="kpi-value">'+fmt(n)+'</div><span class="kpi-foot">'+esc(foot)+'</span></article>';
export function municipalAgeSummary(){
 if(!demographic)return '';
 const g=demographic.ageGroups;
 return '<div class="section">'+
 '<section class="card pad"><h3>População em idade escolar · Censo 2022</h3>'+
 '<p class="sub">IBGE/SIDRA 9514 · residentes em Canoas, não matrículas nem projeções de demanda</p>'+
 '<div class="grid kpis">'+
 card('Crianças e adolescentes (0–17 anos)',g['0–17 anos'],'IBGE · Censo 2022 · residentes')+
 card('Primeira infância (0–5 anos)',(g['0–3 anos']||0)+(g['4–5 anos']||0),'IBGE · idade 0 a 5 anos')+
 card('Idade 6–14 anos',g['6–14 anos'],'IBGE · Censo 2022 · residentes')+
 card('Idade 15–17 anos',g['15–17 anos'],'IBGE · Censo 2022 · residentes')+
 '</div><p class="lead">Os residentes dessas faixas etárias podem estudar fora do município e as escolas locais podem receber alunos de outros municípios; não usar como taxa de atendimento escolar sem matrículas por residência e etapa.</p>'+
 '<div style="margin-top:12px"><button class="button light" data-page="childhood">Explorar perfil etário e primeira infância →</button></div>'+
 '</section></div>';
}
export function childhoodDemographyPage(){
 if(!demographic)return '<div class="empty">Perfil etário do Censo 2022 ainda não carregado.</div>';
 const g=demographic.ageGroups;
 const keys=['0–3 anos','4–5 anos','6–14 anos','15–17 anos','18–24 anos'];
 return '<div class="heading-row"><div><h2>Educação infantil e demografia territorial</h2><p class="lead">População residente por idade, Censo 2022. Referência para planejamento, não contagem de vagas ou demanda reprimida.</p></div><span class="tag">IBGE · 2022</span></div>'+
 '<div class="grid kpis">'+card('Crianças de 0–3 anos',g['0–3 anos'],'Faixa de idade típica para creche · IBGE 2022')+
 card('Crianças de 4–5 anos',g['4–5 anos'],'Faixa etária da pré-escola · IBGE 2022')+
 card('Crianças e adolescentes de 6–14',g['6–14 anos'],'Faixa etária do ensino fundamental · IBGE 2022')+
 card('Adolescentes de 15–17',g['15–17 anos'],'Faixa etária do ensino médio · IBGE 2022')+'</div>'+
 '<section class="card pad section"><h3>Distribuição da população por idade · Censo 2022</h3>'+
 '<p class="sub">Contagens por idade de residência — faixas mutuamente exclusivas</p>'+
 '<div id="age-chart" class="chart" role="img" aria-label="População residente por faixa etária"></div>'+
 '<div class="table-wrap"><table class="table"><thead><tr><th>Idade</th><th>Residentes</th><th>Base</th></tr></thead><tbody>'+
 keys.map(k=>'<tr><td>'+esc(k)+'</td><td>'+fmt(g[k])+'</td><td>IBGE 2022</td></tr>').join('')+
 '</tbody></table></div>'+
 '<div class="notice info"><b>Interpretação:</b> esses quantitativos representam crianças, adolescentes e jovens residentes em Canoas em 2022. Não representam crianças aguardando vagas, número de matrículas, taxa de cobertura ou população em 2026. Para estimar déficit de vagas, é necessário associar procura, residência, capacidade e oferta disponível em dados da Secretaria da Educação.</div>'+
 '<p class="lead"><a href="'+esc(demographic.source)+'" target="_blank" rel="noopener noreferrer">Fonte primária: IBGE/SIDRA · tabela 9514 ↗</a></p></section>';
}
export function mountAgeChart(dark:boolean){
 const el=document.getElementById('age-chart');if(!el||!demographic)return null;
 const labels=['0–3 anos','4–5 anos','6–14 anos','15–17 anos','18–24 anos'];
 const chart=echarts.init(el,dark?'dark':undefined);
 chart.setOption({backgroundColor:'transparent',tooltip:{trigger:'axis'},
 grid:{top:10,bottom:35,left:60,right:20},
 xAxis:{type:'category',data:labels,axisLabel:{interval:0,color:dark?'#eee':'#64748b'}},
 yAxis:{type:'value',axisLabel:{color:dark?'#eee':'#64748b'}},
 series:[{type:'bar',data:labels.map(k=>demographic!.ageGroups[k]),itemStyle:{color:'#12838b',borderRadius:[5,5,0,0]}}]});
 return chart;
}
