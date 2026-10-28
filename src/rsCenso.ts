import * as echarts from "echarts";
type Row={year:number;schools:number;mat_total:number;mat_infantil:number;mat_fundamental:number;mat_fund_ai:number;mat_fund_af:number;mat_medio:number;mat_eja:number};
type Infra={year:number;schools:number;[key:string]:number|null};
type Source={municipalityCode:string;sourceAgency:string;reference:string;sourceURLs:{enrollments:string;infrastructure:string};enrollments:Record<string,Row[]>;infrastructure:Record<string,Infra[]>};
let data:Source|null=null;
const NETWORKS=["Municipal","Estadual","Federal","Privada"] as const;
const NETWORK_LABEL:{[key:string]:string}={"Todas":"Todas as redes",Municipal:"Municipal",Estadual:"Estadual",Federal:"Federal",Privada:"Privada"};
export function setMunicipalCenso(value:unknown){
 const x=value as Source|undefined;
 data=x?.municipalityCode==="4304606" && !!x.enrollments?.Todas?.find(r=>r.year===2025)?x:null;
}
function n(x:number|null|undefined):string{return x==null?"—":new Intl.NumberFormat("pt-BR").format(x)}
function esc(s:string){return s.replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]||c))}
function panel(title:string,subtitle:string,body:string){return '<section class="card pad"><h3>'+title+'</h3><p class="sub">'+subtitle+'</p>'+body+'</section>'}
function tile(label:string,value:string,foot:string){return '<article class="card kpi"><span class="kpi-label">'+label+'</span><div class="kpi-value">'+value+'</div><span class="kpi-foot">'+foot+'</span></article>'}
function row(network:string,year:number){return data?.enrollments?.[network]?.find(r=>r.year===year)}
function tableNetwork(year:number){
 const header='<div class="table-wrap"><table class="table"><thead><tr><th>Rede</th><th>Escolas</th><th>Matrículas</th><th>Infantil</th><th>Fundamental</th><th>Médio</th><th>EJA</th></tr></thead><tbody>';
 const body=[...NETWORKS,"Todas"].map(network=>{const r=row(network,year);return '<tr><td>'+NETWORK_LABEL[network]+'</td><td>'+n(r?.schools)+'</td><td>'+n(r?.mat_total)+'</td><td>'+n(r?.mat_infantil)+'</td><td>'+n(r?.mat_fundamental)+'</td><td>'+n(r?.mat_medio)+'</td><td>'+n(r?.mat_eja)+'</td></tr>'}).join("");
 return header+body+'</tbody></table></div>';
}
export function municipalCensoPanel(){
 if(!data)return '';
 const t=row("Todas",2025),m=row("Municipal",2025);
 return '<section class="section">'+
 panel('Censo Escolar 2025 · Canoas','SEDUC/RS com base no INEP · consolidação municipal por rede · NÃO são números individuais das escolas',
 '<div class="grid kpis">'+
 tile('Matrículas · todas as redes',n(t?.mat_total),'Censo Escolar 2025 · estabelecimentos de Canoas')+
 tile('Matrículas · rede municipal',n(m?.mat_total),'Censo Escolar 2025 · rede municipal')+
 tile('Escolas · todas as redes',n(t?.schools),'Censo Escolar 2025 · universo censitário')+
 tile('Escolas · rede municipal',n(m?.schools),'Censo Escolar 2025 · rede municipal')+'</div>'+
 tableNetwork(2025)+
 '<p class="lead">Os totais são agregados do município no Censo Escolar 2025; o mapa utiliza 178 pontos de uma fonte geográfica com referência cadastral 2023. Os dois conjuntos NÃO possuem os mesmos critérios de cobertura ou o mesmo ano.</p>'+
 '<div style="margin-top:12px"><button class="button light" data-page="enrollments">Explorar rede e séries históricas →</button></div>')+
 '</section>';
}
export function enrollmentsPage(){
 if(!data)return '<div class="empty">Dados de matrículas municipais ainda indisponíveis.</div>';
 return '<div class="heading-row"><div><h2>Rede escolar e matrículas</h2><p class="lead">Matrículas por rede, etapa e ano; município de Canoas.</p></div><span class="tag">INEP/SEDUC · 2010–2025</span></div>'+
 '<div class="notice info">O Censo Escolar é apurado pelo local da escola. Matrículas não são estudantes únicos nem residentes. Os valores a seguir abrangem a rede escolar municipal no Censo 2025, enquanto o mapa apresenta apenas escolas georreferenciadas na referência 2023.</div>'+
 '<div class="grid kpis">'+
 tile('Matrículas em 2025',n(row("Todas",2025)?.mat_total),'Todas as redes')+
 tile('Rede municipal',n(row("Municipal",2025)?.mat_total),'2025 · Municipal')+
 tile('Rede estadual',n(row("Estadual",2025)?.mat_total),'2025 · Estadual')+
 tile('Rede privada',n(row("Privada",2025)?.mat_total),'2025 · Privada')+'</div>'+
 '<div class="section">'+panel('Matrículas por rede · 2025','Total e etapas; subtotais infantil/fundamental/médio/EJA não incluem necessariamente todas as modalidades',
 tableNetwork(2025))+'</div>'+
 '<div class="section">'+panel('Evolução das matrículas em Canoas','Séries anuais de 2010 a 2025 · município, não escola',
 '<div id="rs-enrollments-chart" class="chart" style="min-height:340px" role="img" aria-label="Matrículas por rede ao longo dos anos"></div>'+
 '<div class="table-wrap"><table class="table"><thead><tr><th>Ano</th><th>Total</th><th>Municipal</th><th>Estadual</th><th>Federal</th><th>Privada</th></tr></thead><tbody>'+
 data.enrollments.Todas.map(r=>'<tr><td>'+r.year+'</td>'+["Todas",...NETWORKS].map(k=>'<td>'+n(row(k,r.year)?.mat_total)+'</td>').join('')+'</tr>').join('')+
 '</tbody></table></div>')+'</div>'+
 '<p class="lead"><a href="'+esc(data.sourceURLs.enrollments)+'" target="_blank" rel="noopener noreferrer">Planilha oficial SEDUC/RS de matrículas e redes ↗</a></p>';
}
export function infrastructurePage(){
 if(!data)return '<div class="empty">Infraestrutura municipal ainda não integrada.</div>';
 const columns=["Acesso a Internet (%)","Banda Larga (%)","Computador (%)","Lab. Informatica (%)",
   "Biblioteca (%)","Biblioteca ou Sala de Leitura (%)","Lab. Ciencias (%)","Quadra de Esportes (%)"];
 const rows=[...NETWORKS,"Todas"].map(k=>({name:k,record:data?.infrastructure?.[k]?.find(r=>r.year===2025)}));
 return '<div class="heading-row"><div><h2>Infraestrutura escolar</h2><p class="lead">Percentuais de escolas com recurso, por rede de ensino, Censo Escolar 2025.</p></div><span class="tag">INEP/SEDUC · 2025</span></div>'+
 '<div class="notice info">Os percentuais informados pela SEDUC/RS usam como denominador as escolas da rede e município em cada exercício. Não representam quantidades de alunos e não são atribuídos automaticamente a uma escola selecionada.</div>'+
 '<section class="card pad">'+
 '<h3>Infraestrutura declarada · Canoas</h3><p class="sub">Percentual (%) e número de escolas por rede — 2025</p>'+
 '<div class="table-wrap"><table class="table"><thead><tr><th>Indicador</th>'+rows.map(x=>'<th>'+NETWORK_LABEL[x.name]+'</th>').join('')+'</tr></thead><tbody>'+
 columns.map(key=>'<tr><td>'+esc(key)+'</td>'+
 rows.map(x=>'<td>'+(x.record?.[key]==null?'—':new Intl.NumberFormat("pt-BR",{maximumFractionDigits:1}).format(x.record[key] as number)+'%')+'</td>').join('')+'</tr>').join('')+
 '<tr><td><b>Escolas no denominador</b></td>'+rows.map(x=>'<td>'+n(x.record?.schools)+'</td>').join('')+'</tr>'+
 '</tbody></table></div>'+
 '<p class="lead"><a href="'+esc(data.sourceURLs.infrastructure)+'" target="_blank" rel="noopener noreferrer">Fonte SEDUC/RS — planilha oficial de infraestrutura ↗</a></p></section>';
}
export function mountEnrollmentChart(dark:boolean){
 const el=document.getElementById("rs-enrollments-chart");if(!el||!data)return null;
 const years=data.enrollments.Todas.map(r=>r.year);
 const chart=echarts.init(el,dark?"dark":undefined);
 chart.setOption({animation:!window.matchMedia('(prefers-reduced-motion: reduce)').matches,backgroundColor:"transparent",tooltip:{trigger:"axis"},legend:{top:0},
 grid:{top:65,bottom:45,left:70,right:15},xAxis:{type:"category",data:years.map(String)},
 yAxis:{type:"value"},series:NETWORKS.map(network=>({name:network,type:"line",
 data:years.map(y=>row(network,y)?.mat_total??null),connectNulls:false,symbolSize:4}))});
 return chart;
}
