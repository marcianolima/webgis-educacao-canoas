type IdebPoint={year:number;ideb:number};
type Grade={inep:string;name:string;stageLabel:string;year:number;has2025Result:boolean;
 current:{ideb:number|null;portugueseScore:number|null;mathScore:number|null;performanceScore:number|null;promotionFactor:number|null};
 history:IdebPoint[]};
type Category={source:string;sha256:string;withIDEB2025:number;totalCanoas:number;records:Record<string,Grade>};
type Dataset={schemaVersion:number;municipalityCode:string;year:number;sourceAgency:string;
 stages:Record<'fundamentalInitial'|'fundamentalFinal'|'highSchool',Category>};
let data:Dataset|null=null;
const groups=['fundamentalInitial','fundamentalFinal','highSchool'] as const;
const fmt=(n:number|null|undefined,d=1)=>n==null?'—':new Intl.NumberFormat('pt-BR',{maximumFractionDigits:d,minimumFractionDigits:d}).format(n);
const esc=(value:unknown)=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]||c));
export function setIdebSchoolData(value:unknown){
 const d=value as Dataset|undefined;
 data=d?.municipalityCode==='4304606'&&d.year===2025&&
  groups.every(k=>d.stages?.[k]?.records)?d:null;
}
export function schoolIdebSummary(){
 if(!data)return '';
 return '<div class="section"><section class="card pad"><h3>IDEB 2025 · resultados escolares divulgados</h3>'+
 '<p class="sub">INEP · três etapas com divulgação por código INEP · não representa todas as escolas do município</p>'+
 '<div class="grid kpis">'+groups.map(key=>{
  const x=data!.stages[key];
  return '<article class="card kpi"><span class="kpi-label">'+esc(key==='fundamentalInitial'?'Anos iniciais':key==='fundamentalFinal'?'Anos finais':'Ensino médio')+'</span>'+
  '<div class="kpi-value">'+fmt(x.withIDEB2025,0)+'</div><span class="kpi-foot">Escolas de Canoas com nota IDEB divulgada em 2025</span></article>';
 }).join('')+'</div><div class="notice info">A ausência de IDEB individual não significa nota zero. A divulgação depende de critérios de participação e disponibilidade definidos pelo INEP. O resultado do município e o das escolas não têm o mesmo denominador.</div></section></div>';
}
export function schoolIdebPanel(inep:string){
 if(!data)return '';
 const found=groups.map(group=>data!.stages[group].records[inep]).filter((v):v is Grade=>!!v);
 if(!found.length)return '<section class="section card pad"><h3>IDEB 2025 da escola</h3><p class="lead">Sem registro deste INEP nas planilhas públicas do IDEB 2025. Isso não indica desempenho igual a zero.</p></section>';
 return '<section class="section card pad"><h3>IDEB e proficiências divulgadas por escola · 2025</h3>'+
 '<p class="sub">INEP, resultados oficiais por código INEP. As diferentes etapas são indicadores distintos, não devem ser somadas.</p>'+
 '<div class="table-wrap"><table class="table"><thead><tr><th>Etapa</th><th>IDEB 2025</th><th>Proficiência Língua Portuguesa</th><th>Proficiência Matemática</th><th>Indicador rendimento (P)</th></tr></thead><tbody>'+
 found.map(g=>'<tr><td>'+esc(g.stageLabel)+'</td><td>'+fmt(g.current.ideb)+'</td><td>'+fmt(g.current.portugueseScore,2)+'</td><td>'+fmt(g.current.mathScore,2)+'</td><td>'+fmt(g.current.promotionFactor,3)+'</td></tr>').join('')+'</tbody></table></div>'+
 found.map(g=>'<div class="section"><h3>Série IDEB · '+esc(g.stageLabel)+'</h3>'+
 (g.history.length?
 '<div class="table-wrap"><table class="table"><thead><tr>'+g.history.map(i=>'<th>'+i.year+'</th>').join('')+'</tr></thead><tbody><tr>'+g.history.map(i=>'<td>'+fmt(i.ideb)+'</td>').join('')+'</tr></tbody></table></div>':
 '<p class="lead">Sem notas anteriores divulgadas para esta etapa.</p>')+
 '</div>').join('')+
 '<div class="notice info">As notas de Português e Matemática são resultados de proficiência do SAEB utilizados pelo INEP no cálculo do IDEB; o indicador de rendimento é distinto da nota final. Campos sem resultado publicado permanecem como indisponíveis.</div>'+
 '</section>';
}
export function schoolIdebCurrent(inep:string){
 if(!data)return null;
 const out:Record<string,number|null>={};
 for(const k of groups){out[k]=data.stages[k].records[inep]?.current.ideb??null}
 return out;
}
