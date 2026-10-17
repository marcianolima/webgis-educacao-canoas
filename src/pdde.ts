type Payment={program:string;paidBRL:number;paymentDate:string};
type School={inep:string;year:number;status:string;paidBRL:number|null;paymentCount?:number;payments:Payment[]};
type Report={schemaVersion:number;year:number;schoolsChecked:number;schoolsResponded:number;schoolsWithPublishedPayments:number;totalPaidRespondedBRL:number;coverageNote:string;byInep:Record<string,School>;source:string};
let pdde:Report|null=null;
export function setPdde(raw:unknown){
 const d=raw as Report|undefined;
 pdde=d?.year===2025 && d.schoolsWithPublishedPayments>0 && d.schoolsResponded>=d.schoolsChecked*.8 &&
  !!d.byInep?d:null;
}
const money=(v:number|null|undefined)=>v==null?'Não disponível':new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL'}).format(v);
const esc=(v:unknown)=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&gt;','"':'&quot;',"'":'&#39;'}[c]||c));
export function pddeSchoolPanel(inep:string){
 if(!pdde)return '';
 const item=pdde.byInep[inep];
 if(!item)return '<section class="section card pad"><h3>PDDE 2025 · dados por escola</h3><p class="lead">Esta escola não integra a cobertura do coletor PDDE da rede municipal, ou não teve consulta validada. Não é valor zero.</p></section>';
 if(item.status!=='ok')return '<section class="section card pad"><h3>PDDE 2025 · recursos pagos</h3><p class="lead">A consulta pública não retornou registro de pagamentos para o código INEP neste exercício. Isso não equivale a afirmar ausência de repasses.</p></section>';
 return '<section class="section card pad"><h3>PDDE 2025 · recursos pagos ao estabelecimento</h3>'+
 '<div class="grid finance-kpis"><article class="card kpi"><span class="kpi-label">Total pago · PDDE 2025</span><div class="kpi-value">'+money(item.paidBRL)+'</div><span class="kpi-foot">FNDE · PDDE Info · código INEP '+esc(inep)+'</span></article></div>'+
 '<p class="sub">Pagamentos individuais, por programa/ação e data. Não representam todos os recursos de financiamento da escola.</p>'+
 '<div class="table-wrap"><table class="table"><thead><tr><th>Programa ou ação</th><th>Data do pagamento</th><th>Valor pago</th></tr></thead><tbody>'+
 item.payments.map(p=>'<tr><td>'+esc(p.program)+'</td><td>'+esc(p.paymentDate)+'</td><td>'+money(p.paidBRL)+'</td></tr>').join('')+
 '</tbody></table></div>'+
 '<p class="lead"><a href="https://www.fnde.gov.br/pddeinfo/pddeinfo/escola/consultar?ano=2025&amp;co_escola='+encodeURIComponent(inep)+'&amp;consultar=Consultar" target="_blank" rel="noopener noreferrer">Verificar os valores na consulta oficial PDDE Info ↗</a></p>'+
 '</section>';
}
export function pddeCoverageInfo(){
 if(!pdde)return '';
 return '<section class="section card pad"><h3>PDDE 2025 · escolas municipais georreferenciadas</h3>'+
 '<p class="sub">FNDE · PDDE Info · cobertura parcial do catálogo SEDUC/RS 2023, consultas por INEP</p>'+
 '<div class="grid finance-kpis">'+
 '<article class="card kpi"><span class="kpi-label">Total pago às escolas com respostas válidas</span><div class="kpi-value">'+money(pdde.totalPaidRespondedBRL)+'</div><span class="kpi-foot">Não é o total de PDDE de todas as escolas de Canoas</span></article>'+
 '<article class="card kpi"><span class="kpi-label">Escolas consultadas</span><div class="kpi-value">'+pdde.schoolsChecked+'</div><span class="kpi-foot">'+pdde.schoolsResponded+' com resposta validada · '+pdde.schoolsWithPublishedPayments+' com pagamentos publicados</span></article>'+
 '</div><p class="lead">'+esc(pdde.coverageNote)+'</p></section>';
}
