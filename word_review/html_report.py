"""產生完全離線、可互動的單一 HTML 報告。"""

from __future__ import annotations

import html
import json
from pathlib import Path

from .i18n import get_translations, t
from .models import AnalysisReport


def generate_html(report: AnalysisReport, output_path: str | Path, lang: str = "zh") -> Path:
    """將分析結果寫成內嵌 CSS、JavaScript 及資料的 HTML。"""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    # 防止文件內容中的結束 script 標記跳出 JSON 腳本區塊。
    data_json = json.dumps(report.to_dict(), ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    translations = get_translations(lang)["html"]
    i18n_json = json.dumps(translations, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    html_lang = "zh-Hant" if lang == "zh" else "en"
    if report.mode == "compare":
        title = t(
            "html.report_title.compare",
            old=Path(report.metadata["old_source"]).name,
            new=Path(report.metadata["new_source"]).name,
        )
    else:
        title = t(
            "html.report_title.extract",
            file=Path(report.metadata["source"]).name,
        )
    safe_title = html.escape(title, quote=True)
    document = f"""<!doctype html>
<html lang="{html_lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{safe_title}</title>
<style>
:root{{--green:#16803c;--green-bg:#eaf8ef;--red:#c42b32;--red-bg:#fff0f0;--blue:#1769aa;--blue-bg:#edf6ff;--amber:#9a5b00;--amber-bg:#fff6df;--line:#d9dee7;--muted:#667085;--ink:#172033}}
*{{box-sizing:border-box}} body{{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft JhengHei",sans-serif;color:var(--ink);background:#f5f7fa}}
header{{height:76px;padding:13px 22px;background:#fff;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;gap:20px}}
h1{{font-size:20px;margin:0 0 5px}} .summary{{color:var(--muted);font-size:13px}}
.layout{{display:grid;grid-template-columns:minmax(330px,38%) 1fr;height:calc(100vh - 76px)}}
.sidebar,.preview{{overflow:auto}} .sidebar{{background:#fff;border-right:1px solid var(--line)}}
.toolbar{{position:sticky;top:0;z-index:3;background:#fff;padding:12px;border-bottom:1px solid var(--line)}}
.filters{{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:9px}} button{{font:inherit;cursor:pointer}}
.filter{{border:1px solid var(--line);border-radius:16px;padding:5px 10px;background:#fff;color:#344054}} .filter.active{{background:#172033;color:#fff;border-color:#172033}}
#search{{width:100%;padding:8px 10px;border:1px solid var(--line);border-radius:6px}}
.item{{width:100%;border:0;border-bottom:1px solid #edf0f4;background:#fff;text-align:left;padding:12px 14px;display:block}} .item:hover,.item.active{{background:#f1f5fb}}
.item.active{{box-shadow:inset 4px 0 #3448c5}} .item-head{{display:flex;align-items:center;gap:7px;margin-bottom:5px}} .badge{{font-size:12px;font-weight:700;border-radius:4px;padding:2px 6px}}
.badge.insert{{color:var(--green);background:var(--green-bg)}} .badge.delete{{color:var(--red);background:var(--red-bg)}} .badge.comment{{color:var(--blue);background:var(--blue-bg)}} .badge.modify{{color:var(--amber);background:var(--amber-bg)}}
.meta{{font-size:12px;color:var(--muted)}} .snippet{{font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.preview{{padding:24px max(24px,6vw) 60px}} .hint{{padding:11px 14px;color:#475467;background:#eef2f8;border-radius:7px;margin-bottom:18px}}
.detail{{background:#fff;border:1px solid var(--line);border-radius:8px;padding:14px;margin-bottom:18px;box-shadow:0 2px 7px #2030500d}} .detail h2{{font-size:16px;margin:0 0 9px}} .detail-row{{margin-top:6px;line-height:1.55}} .label{{color:var(--muted);font-size:12px;margin-right:8px}}
.paragraph{{background:#fff;border:1px solid var(--line);border-radius:7px;margin:9px 0;padding:14px 16px;line-height:1.75;scroll-margin-top:20px;transition:.2s}} .paragraph.target{{border-color:#4c63d2;background:#f1f3ff;box-shadow:0 0 0 3px #4c63d224}}
.para-number{{font-size:11px;color:#98a2b3;margin-bottom:3px}} ins{{color:var(--green);background:#bff0cd;text-decoration:none;padding:1px 2px;border-radius:2px}} del{{color:var(--red);background:#ffd1d1;padding:1px 2px;border-radius:2px}} mark{{background:#ffe36e;padding:1px 2px;border-radius:2px}}
.preview-nav{{position:sticky;top:-24px;z-index:4;display:flex;gap:7px;align-items:center;background:#f5f7fa;padding:10px 0;margin-bottom:8px}} .nav-button{{border:1px solid var(--line);background:#fff;border-radius:5px;padding:7px 11px}} .nav-button:hover{{background:#eef2ff}}
.compare-header,.compare-row{{display:grid;grid-template-columns:1fr 1fr;gap:10px}} .compare-header{{position:sticky;top:45px;z-index:3;font-size:12px;font-weight:700;color:#475467;background:#e9edf4;border-radius:6px;padding:8px 12px}}
.compare-row{{scroll-margin-top:95px;margin:8px 0;border:1px solid var(--line);border-radius:7px;background:#fff;transition:.2s}} .compare-row.target{{border-color:#4c63d2;box-shadow:0 0 0 3px #4c63d224}}
.version-cell{{padding:12px 14px;line-height:1.75;min-width:0}} .version-cell+ .version-cell{{border-left:1px solid var(--line)}} .cell-meta{{font-size:11px;color:#7b8494;margin-bottom:5px}} .row-equal{{opacity:.72}} .row-insert .version-cell:last-child{{background:var(--green-bg)}} .row-delete .version-cell:first-child{{background:var(--red-bg)}}
.empty{{color:var(--muted);padding:20px;text-align:center}}
@media(max-width:760px){{header{{height:auto}}.layout{{grid-template-columns:1fr;height:auto}}.sidebar{{height:46vh;border-right:0;border-bottom:1px solid var(--line)}}.preview{{height:54vh;padding:16px}}}}
</style>
</head>
<body>
<header><div><h1>{safe_title}</h1><div id="summary" class="summary"></div></div><div class="summary">{translations['header.offline']}</div></header>
<main class="layout">
<section class="sidebar"><div class="toolbar"><div id="filters" class="filters"></div><input id="search" type="search" placeholder="{translations['search.placeholder']}"></div><div id="items"></div></section>
<section id="preview" class="preview"><div class="preview-nav"><button id="previous" class="nav-button">{translations['nav.previous']}</button><button id="next" class="nav-button">{translations['nav.next']}</button><button id="toggle-full" class="nav-button">{translations['nav.expand']}</button><span id="position" class="summary"></span></div><div class="hint">{translations['hint.jump']}</div><div id="detail"></div><div id="paragraphs"></div></section>
</main>
<script id="report-data" type="application/json">{data_json}</script>
<script>
const I18N={i18n_json};
const listSeparator={json.dumps("、" if lang == "zh" else ", ")};
const tr=(key,values={{}})=>String(I18N[key]??key).replace(/\\{{(\\w+)\\}}/g,(_,name)=>String(values[name]??''));
const report=JSON.parse(document.getElementById('report-data').textContent);
const escapeHtml=value=>String(value??'').replace(/[&<>\"']/g,ch=>({{'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}}[ch]));
const labels={{insert:tr('badge.insert'),delete:tr('badge.delete'),comment:tr('badge.comment'),modify:tr('badge.modify')}};
let selected=null,currentFilter='all',fullDocument=false;
function records(){{
 if(report.mode==='compare') return report.differences.map(d=>({{...d,type:d.diff_type,id:d.diff_id,index:d.context_index,author:[...(d.old_authors||[]),...(d.new_authors||[])].join(listSeparator),date:'',snippet:d.new_text||d.old_text}}));
 return [...report.revisions.map(r=>({{...r,type:r.revision_type,id:r.location_id,index:r.paragraph_index,snippet:r.after_text||r.before_text}})),...report.comments.map(c=>({{...c,type:'comment',id:c.location_id,index:c.start_paragraph,snippet:c.content}}))];
}}
const allRecords=records();
function renderFilters(){{
 const types=[...new Set(allRecords.map(x=>x.type))];
 document.getElementById('filters').innerHTML=[['all',tr('filter.all')],...types.map(t=>[t,labels[t]])].map(([key,label])=>`<button class="filter ${{key===currentFilter?'active':''}}" data-filter="${{key}}">${{label}}</button>`).join('');
 document.querySelectorAll('.filter').forEach(button=>button.onclick=()=>{{currentFilter=button.dataset.filter;renderFilters();renderItems();}});
}}
function searchable(item){{return [item.author,item.date,item.snippet,item.before_text,item.after_text,item.quoted_text,item.old_text,item.new_text,item.old_authors,item.new_authors].join(' ').toLowerCase()}}
function renderItems(){{
 const query=document.getElementById('search').value.trim().toLowerCase();
 const shown=allRecords.filter(x=>(currentFilter==='all'||x.type===currentFilter)&&(!query||searchable(x).includes(query)));
 document.getElementById('items').innerHTML=shown.length?shown.map(item=>`<button class="item ${{selected===item.id?'active':''}}" data-id="${{escapeHtml(item.id)}}"><span class="item-head"><span class="badge ${{item.type}}">${{labels[item.type]}}</span><span class="meta">${{escapeHtml(item.author||'')}}</span></span><span class="snippet">${{escapeHtml(item.snippet||tr('empty.no_text'))}}</span></button>`).join(''):`<div class="empty">${{tr('empty.no_items')}}</div>`;
 document.querySelectorAll('.item').forEach(button=>button.onclick=()=>selectRecord(button.dataset.id));
}}
function inlineSide(parts,side){{return (parts||[]).filter(p=>p.type==='equal'||p.type===side).map(p=>p.type==='insert'?`<ins>${{escapeHtml(p.text)}}</ins>`:p.type==='delete'?`<del>${{escapeHtml(p.text)}}</del>`:escapeHtml(p.text)).join('')}}
function authors(values){{return (values&&values.length)?escapeHtml(values.join(listSeparator)):tr('author.unrecorded')}}
function compareCell(row,side){{
 const text=row[`${{side}}_text`],index=row[`${{side}}_index`],people=row[`${{side}}_authors`];
 let content=escapeHtml(text||tr('paragraph.no_match'));
 if(row.diff_type==='modify') content=inlineSide(row.inline_changes,side==='old'?'delete':'insert');
 else if(row.diff_type==='delete'&&side==='old') content=`<del>${{escapeHtml(text)}}</del>`;
 else if(row.diff_type==='insert'&&side==='new') content=`<ins>${{escapeHtml(text)}}</ins>`;
 return `<div class="version-cell"><div class="cell-meta">${{index===null?'—':tr('paragraph.number',{{number:index+1}})}} · ${{tr(side==='old'?'detail.old_author':'detail.new_author')}}: ${{authors(people)}}</div>${{content}}</div>`;
}}
function renderCompare(index){{
 const rows=report.comparison_rows||[];const start=fullDocument?0:Math.max(0,index-3),end=fullDocument?rows.length:Math.min(rows.length,index+4);
 const header=`<div class="compare-header"><div>${{tr('compare.before',{{value:escapeHtml(report.metadata.old_name||tr('compare.version_one'))}})}}</div><div>${{tr('compare.after',{{value:escapeHtml(report.metadata.new_name||tr('compare.version_two'))}})}}</div></div>`;
 const body=rows.slice(start,end).map(row=>`<article id="comparison-row-${{row.context_index}}" class="compare-row row-${{row.diff_type}} ${{row.context_index===index?'target':''}}">${{compareCell(row,'old')}}${{compareCell(row,'new')}}</article>`).join('');
 document.getElementById('paragraphs').innerHTML=header+(body||`<div class="empty">${{tr('empty.no_preview')}}</div>`);
}}
function markText(text,needle,kind){{
 if(!needle)return escapeHtml(text||tr('paragraph.blank'));const at=text.indexOf(needle);if(at<0)return escapeHtml(text);
 const tag=kind==='delete'?'del':kind==='comment'?'mark':'ins';return escapeHtml(text.slice(0,at))+`<${{tag}}>${{escapeHtml(needle)}}</${{tag}}>`+escapeHtml(text.slice(at+needle.length));
}}
function renderExtract(index,item){{
 const start=fullDocument?0:Math.max(0,index-3),end=fullDocument?report.paragraphs.length:Math.min(report.paragraphs.length,index+4);
 document.getElementById('paragraphs').innerHTML=report.paragraphs.slice(start,end).map(p=>{{
  let text=p.current_text,needle='';if(p.index===index&&item){{needle=item.after_text||item.before_text||item.quoted_text||'';if(item.type==='delete')text=p.original_text;}}
  return `<article id="paragraph-${{p.index}}" class="paragraph ${{p.index===index?'target':''}}"><div class="para-number">${{tr('paragraph.number',{{number:p.index+1}})}}</div>${{p.index===index?markText(text,needle,item?.type):escapeHtml(text||tr('paragraph.blank'))}}</article>`;
 }}).join('');
}}
function renderPreview(item){{if(report.mode==='compare')renderCompare(item?.index||0);else renderExtract(item?.index||0,item)}}
function detailHtml(item){{
 const head=`<h2><span class="badge ${{item.type}}">${{labels[item.type]}}</span> ${{tr('detail.title')}}</h2>`;
 if(item.type==='comment')return head+`<div class="detail-row"><span class="label">${{tr('detail.author_time')}}</span>${{escapeHtml(item.author)}}　${{escapeHtml(item.date)}}</div><div class="detail-row"><span class="label">${{tr('detail.quoted_text')}}</span>${{escapeHtml(item.quoted_text||tr('detail.unanchored'))}}</div><div class="detail-row"><span class="label">${{tr('detail.comment')}}</span>${{escapeHtml(item.content)}}</div>`;
 if(report.mode==='compare')return head+`<div class="detail-row"><span class="label">${{tr('detail.old_author')}}</span>${{authors(item.old_authors)}}</div><div class="detail-row"><span class="label">${{tr('detail.before')}}</span>${{inlineSide(item.inline_changes,'delete')||escapeHtml(item.old_text||tr('detail.none'))}}</div><div class="detail-row"><span class="label">${{tr('detail.new_author')}}</span>${{authors(item.new_authors)}}</div><div class="detail-row"><span class="label">${{tr('detail.after')}}</span>${{inlineSide(item.inline_changes,'insert')||escapeHtml(item.new_text||tr('detail.none'))}}</div>`;
 return head+`<div class="detail-row"><span class="label">${{tr('detail.author_time')}}</span>${{escapeHtml(item.author)}}　${{escapeHtml(item.date)}}</div><div class="detail-row"><span class="label">${{tr('detail.before')}}</span>${{escapeHtml(item.before_text||tr('detail.none'))}}</div><div class="detail-row"><span class="label">${{tr('detail.after')}}</span>${{escapeHtml(item.after_text||tr('detail.none'))}}</div>`;
}}
function selectRecord(id){{
 const item=allRecords.find(x=>x.id===id);if(!item)return;selected=id;renderItems();document.getElementById('detail').innerHTML=`<div class="detail">${{detailHtml(item)}}</div>`;renderPreview(item);
 const position=allRecords.indexOf(item);document.getElementById('position').textContent=`${{position+1}} / ${{allRecords.length}}`;
 const targetId=report.mode==='compare'?`comparison-row-${{item.index}}`:`paragraph-${{item.index}}`;requestAnimationFrame(()=>document.getElementById(targetId)?.scrollIntoView({{behavior:'smooth',block:'center'}}));
}}
function move(delta){{if(!allRecords.length)return;let at=allRecords.findIndex(x=>x.id===selected);at=(at+delta+allRecords.length)%allRecords.length;selectRecord(allRecords[at].id)}}
document.getElementById('previous').onclick=()=>move(-1);document.getElementById('next').onclick=()=>move(1);
document.getElementById('toggle-full').onclick=()=>{{fullDocument=!fullDocument;document.getElementById('toggle-full').textContent=fullDocument?tr('nav.nearby'):tr('nav.expand');const item=allRecords.find(x=>x.id===selected);renderPreview(item);if(item){{const id=report.mode==='compare'?`comparison-row-${{item.index}}`:`paragraph-${{item.index}}`;requestAnimationFrame(()=>document.getElementById(id)?.scrollIntoView({{block:'center'}}));}}}};
document.getElementById('search').addEventListener('input',renderItems);
document.getElementById('summary').textContent=report.mode==='compare'?tr('summary.compare',{{count:allRecords.length}}):tr('summary.extract',{{revisions:report.revisions.length,comments:report.comments.length}});
renderFilters();renderItems();if(allRecords.length)selectRecord(allRecords[0].id);else renderPreview(null);
</script>
</body>
</html>"""
    output.write_text(document, encoding="utf-8")
    return output
