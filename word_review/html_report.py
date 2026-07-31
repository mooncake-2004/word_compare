"""產生完全離線、可互動的單一 HTML 報告。"""

from __future__ import annotations

import html
import json
from pathlib import Path

from .models import AnalysisReport


def generate_html(report: AnalysisReport, output_path: str | Path) -> Path:
    """將分析結果寫成內嵌 CSS、JavaScript 及資料的 HTML。"""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    # 防止文件內容中的結束 script 標記跳出 JSON 腳本區塊。
    data_json = json.dumps(report.to_dict(), ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    safe_title = html.escape(report.title, quote=True)
    document = f"""<!doctype html>
<html lang="zh-Hant">
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
.para-number{{font-size:11px;color:#98a2b3;margin-bottom:3px}} ins{{color:var(--green);background:var(--green-bg);text-decoration:none}} del{{color:var(--red);background:var(--red-bg)}} .empty{{color:var(--muted);padding:20px;text-align:center}}
@media(max-width:760px){{header{{height:auto}}.layout{{grid-template-columns:1fr;height:auto}}.sidebar{{height:46vh;border-right:0;border-bottom:1px solid var(--line)}}.preview{{height:54vh;padding:16px}}}}
</style>
</head>
<body>
<header><div><h1>{safe_title}</h1><div id="summary" class="summary"></div></div><div class="summary">本地離線報告</div></header>
<main class="layout">
<section class="sidebar"><div class="toolbar"><div id="filters" class="filters"></div><input id="search" type="search" placeholder="搜尋作者、日期或內容"></div><div id="items"></div></section>
<section id="preview" class="preview"><div class="hint">點擊左側項目，查看對應段落及前後各 3 段。</div><div id="detail"></div><div id="paragraphs"></div></section>
</main>
<script id="report-data" type="application/json">{data_json}</script>
<script>
const report=JSON.parse(document.getElementById('report-data').textContent);
const escapeHtml=value=>String(value??'').replace(/[&<>\"']/g,ch=>({{'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}}[ch]));
const labels={{insert:'新增',delete:'刪除',comment:'批註',modify:'修改'}};
let selected=null, currentFilter='all';
function records(){{
 if(report.mode==='compare') return report.differences.map(d=>({{...d,type:d.diff_type,id:d.diff_id,index:d.context_index,author:'',date:'',snippet:d.new_text||d.old_text}}));
 return [...report.revisions.map(r=>({{...r,type:r.revision_type,id:r.location_id,index:r.paragraph_index,snippet:r.after_text||r.before_text}})),...report.comments.map(c=>({{...c,type:'comment',id:c.location_id,index:c.start_paragraph,snippet:c.content}}))];
}}
const allRecords=records();
function renderFilters(){{
 const types=[...new Set(allRecords.map(x=>x.type))];
 document.getElementById('filters').innerHTML=[['all','全部'],...types.map(t=>[t,labels[t]])].map(([key,label])=>`<button class="filter ${{key===currentFilter?'active':''}}" data-filter="${{key}}">${{label}}</button>`).join('');
 document.querySelectorAll('.filter').forEach(button=>button.onclick=()=>{{currentFilter=button.dataset.filter;renderFilters();renderItems();}});
}}
function searchable(item){{return [item.author,item.date,item.snippet,item.before_text,item.after_text,item.quoted_text,item.old_text,item.new_text].join(' ').toLowerCase()}}
function renderItems(){{
 const query=document.getElementById('search').value.trim().toLowerCase();
 const shown=allRecords.filter(x=>(currentFilter==='all'||x.type===currentFilter)&&(!query||searchable(x).includes(query)));
 document.getElementById('items').innerHTML=shown.length?shown.map(item=>`<button class="item ${{selected===item.id?'active':''}}" data-id="${{escapeHtml(item.id)}}"><span class="item-head"><span class="badge ${{item.type}}">${{labels[item.type]}}</span><span class="meta">${{escapeHtml(item.author||'')}} ${{escapeHtml(item.date||'')}}</span></span><span class="snippet">${{escapeHtml(item.snippet||'（無文字）')}}</span></button>`).join(''):'<div class="empty">沒有符合條件的項目</div>';
 document.querySelectorAll('.item').forEach(button=>button.onclick=()=>selectRecord(button.dataset.id));
}}
function renderParagraphWindow(index){{
 const start=Math.max(0,index-3), end=Math.min(report.paragraphs.length,index+4);
 const list=report.paragraphs.slice(start,end);
 document.getElementById('paragraphs').innerHTML=list.length?list.map(p=>`<article id="paragraph-${{p.index}}" class="paragraph ${{p.index===index?'target':''}}"><div class="para-number">第 ${{p.index+1}} 段</div>${{escapeHtml(p.current_text||'（空白段落）')}}</article>`).join(''):'<div class="empty">文件沒有可預覽的段落</div>';
}}
function inlineHtml(parts){{return (parts||[]).map(p=>p.type==='insert'?`<ins>${{escapeHtml(p.text)}}</ins>`:p.type==='delete'?`<del>${{escapeHtml(p.text)}}</del>`:escapeHtml(p.text)).join('')}}
function detailHtml(item){{
 const head=`<h2><span class="badge ${{item.type}}">${{labels[item.type]}}</span> 詳細內容</h2>`;
 if(item.type==='comment') return head+`<div class="detail-row"><span class="label">作者／時間</span>${{escapeHtml(item.author)}}　${{escapeHtml(item.date)}}</div><div class="detail-row"><span class="label">被批註原文</span>${{escapeHtml(item.quoted_text||'（未找到錨定文字）')}}</div><div class="detail-row"><span class="label">批註</span>${{escapeHtml(item.content)}}</div>`;
 if(report.mode==='compare') return head+`<div class="detail-row"><span class="label">修改前</span>${{escapeHtml(item.old_text||'（無）')}}</div><div class="detail-row"><span class="label">修改後</span>${{escapeHtml(item.new_text||'（無）')}}</div>${{item.type==='modify'?`<div class="detail-row"><span class="label">字元差異</span>${{inlineHtml(item.inline_changes)}}</div>`:''}}`;
 return head+`<div class="detail-row"><span class="label">作者／時間</span>${{escapeHtml(item.author)}}　${{escapeHtml(item.date)}}</div><div class="detail-row"><span class="label">修改前</span>${{escapeHtml(item.before_text||'（無）')}}</div><div class="detail-row"><span class="label">修改後</span>${{escapeHtml(item.after_text||'（無）')}}</div>`;
}}
function selectRecord(id){{
 const item=allRecords.find(x=>x.id===id);if(!item)return;selected=id;renderItems();
 document.getElementById('detail').innerHTML=`<div class="detail">${{detailHtml(item)}}</div>`;renderParagraphWindow(item.index);
 requestAnimationFrame(()=>document.getElementById(`paragraph-${{item.index}}`)?.scrollIntoView({{behavior:'smooth',block:'center'}}));
}}
document.getElementById('search').addEventListener('input',renderItems);
document.getElementById('summary').textContent=report.mode==='compare'?`${{allRecords.length}} 項段落差異`:`${{report.revisions.length}} 項修訂，${{report.comments.length}} 條批註`;
renderFilters();renderItems();renderParagraphWindow(0);if(allRecords.length)selectRecord(allRecords[0].id);
</script>
</body>
</html>"""
    output.write_text(document, encoding="utf-8")
    return output
