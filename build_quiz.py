#!/usr/bin/env python3
"""Generate quiz.html with authors grouped by 组别."""
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE, 'questions.json'), encoding='utf-8') as f:
    questions = json.load(f)

# Group mapping
GROUP_LABEL = {
    '眼科出题第一组': '第一组',
    '眼科出题第二组': '第二组',
    '眼科出题第三组': '第三组',
}

# Build author list per group for the JS dropdown
group_authors = {}
for q in questions:
    g = q.get('group', '')
    a = q.get('author', '')
    if g not in group_authors:
        group_authors[g] = {}
    group_authors[g][a] = group_authors[g].get(a, 0) + 1

# Groups in correct order
sorted_groups = ['眼科出题第一组', '眼科出题第二组', '眼科出题第三组']

clean = []
for q in questions:
    clean.append({
        'q': q['question'],
        'o': q.get('options', {}),
        'a': q.get('answer', ''),
        'e': q.get('explanation', ''),
        'author': q.get('author', ''),
        'group': q.get('group', ''),
    })

# Build the JS author data structure
import json as jmod
authors_js = {}
for g in sorted_groups:
    authors_js[GROUP_LABEL.get(g, g)] = sorted(group_authors[g].keys())

html = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>眼科学刷题 - 期末复习</title>
<style>
:root {
  --bg: #0d1117;
  --surface: #161b22;
  --surface2: #21262d;
  --text: #e6edf3;
  --text2: #8b949e;
  --accent: #6366f1;
  --accent2: #818cf8;
  --success: #22c55e;
  --danger: #ef4444;
  --warning: #f59e0b;
  --border: #30363d;
  --radius: 12px;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{
  font-family: -apple-system, "PingFang SC", "Microsoft YaHei", "Helvetica Neue", sans-serif;
  background: var(--bg); color: var(--text);
  min-height: 100vh; line-height: 1.6;
  -webkit-tap-highlight-color: transparent;
}

/* ── Header ── */
.topbar{
  background: var(--surface); border-bottom: 1px solid var(--border);
  padding: 8px 16px; position: sticky; top: 0; z-index: 100;
}
.topbar-inner{
  max-width: 860px; margin: 0 auto;
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
}
.brand{font-weight:700;font-size:1.05em;color:var(--accent2);white-space:nowrap}
.brand span{color:var(--text2);font-weight:400;font-size:.75em}

/* mode toggle pill */
.pill{display:flex;background:var(--surface2);border-radius:20px;overflow:hidden;border:1px solid var(--border)}
.pill button{
  border:none;background:transparent;color:var(--text2);
  padding:5px 14px;font-size:.78em;font-weight:500;cursor:pointer;transition:.15s;white-space:nowrap
}
.pill button.on{background:var(--accent);color:#fff}
.pill button:hover:not(.on){color:var(--text)}

/* controls row */
.ctrls{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.ctrls select,.ctrls .btn{
  padding:5px 10px;border-radius:8px;border:1px solid var(--border);
  background:var(--surface2);color:var(--text);font-size:.78em;
  cursor:pointer;font-family:inherit;transition:.15s
}
.ctrls select{min-width:90px}
.ctrls select option.optgroup{font-weight:700;color:var(--accent2);background:var(--surface)}
.btn{font-weight:500;white-space:nowrap}
.btn:hover{border-color:var(--accent);color:var(--accent2)}
.btn.on{background:var(--accent);border-color:var(--accent);color:#fff}

/* ── Progress ── */
.prog{max-width:860px;margin:0 auto;padding:6px 16px}
.prog-bar{height:4px;background:var(--surface2);border-radius:2px;overflow:hidden}
.prog-fill{height:100%;background:var(--accent);border-radius:2px;transition:width .3s}
.prog-info{display:flex;justify-content:space-between;font-size:.72em;color:var(--text2);margin-top:3px}

/* ── Question ── */
main{max-width:860px;margin:0 auto;padding:16px}

.card{
  background:var(--surface);border:1px solid var(--border);
  border-radius:var(--radius);padding:20px 24px;
  animation: fadeUp .25s ease;
}
@keyframes fadeUp{from{opacity:0;transform:translateY(8px)}}

.qmeta{font-size:.75em;color:var(--text2);margin-bottom:6px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.qmeta .star{cursor:pointer;font-size:1.1em;user-select:none}
.qmeta .grp{font-size:.7em;padding:2px 6px;border-radius:10px;background:var(--surface2);color:var(--accent2)}

.qtext{font-size:1.05em;font-weight:500;margin-bottom:16px;line-height:1.7}

/* options */
.opts{display:flex;flex-direction:column;gap:6px}
.opt{
  display:flex;align-items:flex-start;gap:12px;
  padding:11px 14px;border:1.5px solid var(--border);border-radius:10px;
  cursor:pointer;transition:all .12s;background:var(--surface);
  -webkit-user-select:none;user-select:none
}
.opt:hover{border-color:var(--accent);background:var(--surface2)}
.opt.ok{border-color:var(--success)!important;background:rgba(34,197,94,.06)!important}
.opt.bad{border-color:var(--danger)!important;background:rgba(239,68,68,.06)!important}
.opt.dim{pointer-events:none;opacity:.65}
.opt-letter{
  width:26px;height:26px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-weight:600;font-size:.82em;flex-shrink:0;
  background:var(--surface2);border:1px solid var(--border);transition:.12s
}
.opt.ok .opt-letter{background:var(--success);border-color:var(--success);color:#fff}
.opt.bad .opt-letter{background:var(--danger);border-color:var(--danger);color:#fff}
.opt-text{flex:1;padding-top:1px}

/* feedback box */
.fb{
  margin-top:14px;padding:14px 16px;border-radius:10px;font-size:.85em;
  display:none;line-height:1.6
}
.fb.on{display:block}
.fb.good{background:rgba(34,197,94,.06);border:1px solid rgba(34,197,94,.25)}
.fb.bad{background:rgba(239,68,68,.06);border:1px solid rgba(239,68,68,.25)}
.fb-title{font-weight:600;margin-bottom:3px}
.fb.good .fb-title{color:var(--success)}
.fb.bad .fb-title{color:var(--danger)}
.fb-expl{margin-top:6px;color:var(--text2)}

/* actions */
.acts{display:flex;gap:8px;margin-top:16px;flex-wrap:wrap}
.act{
  padding:9px 18px;border-radius:10px;border:1px solid var(--border);
  background:var(--surface2);color:var(--text);cursor:pointer;
  font-size:.85em;font-weight:500;transition:.15s;font-family:inherit
}
.act:hover{border-color:var(--accent)}
.act.go{background:var(--accent);border-color:var(--accent);color:#fff}
.act.go:hover{background:var(--accent2)}
.act:disabled{opacity:.35;pointer-events:none}

/* key hints */
kbd{
  display:inline-block;padding:1px 5px;border-radius:3px;
  background:var(--surface2);border:1px solid var(--border);
  font-size:.72em;font-family:"SF Mono","Fira Code",monospace;margin:0 1px
}

/* empty state */
.empty{text-align:center;padding:60px 20px}
.empty h2{font-size:1.3em;margin-bottom:6px}
.empty p{color:var(--text2);margin-bottom:16px}

/* toast */
.toast{
  position:fixed;top:16px;left:50%;transform:translateX(-50%);
  padding:8px 18px;border-radius:20px;
  background:var(--surface);border:1px solid var(--border);
  z-index:300;font-size:.85em;font-weight:500;
  animation:toastIn .25s ease;pointer-events:none;opacity:0;transition:opacity .2s
}
.toast.on{opacity:1}
.toast.ok{border-color:var(--success);color:var(--success)}
.toast.ng{border-color:var(--danger);color:var(--danger)}
@keyframes toastIn{from{opacity:0;transform:translateX(-50%) translateY(-8px)}}

/* dark scrollbar */
::-webkit-scrollbar{width:6px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}

/* responsive */
@media(max-width:600px){
  .card{padding:14px 16px}
  .qtext{font-size:.98em}
  .opt{padding:9px 12px}
}
</style>
</head>
<body>

<div class="topbar">
  <div class="topbar-inner">
    <div class="brand">👁 眼科刷题<span>期末复习</span></div>
    <div class="pill" id="modePill">
      <button class="on" data-m="study" onclick="S.setMode('study')">📖 解析</button>
      <button data-m="speed" onclick="S.setMode('speed')">⚡ 速刷</button>
    </div>
    <div class="ctrls">
      <select id="selAuthor" onchange="S.apply()">
        <option value="all">👤 全部出题人</option>
      </select>
      <select id="selScope" onchange="S.apply()">
        <option value="all">📋 全部</option>
        <option value="unanswered">❓ 未做</option>
        <option value="wrong">❌ 错题</option>
        <option value="starred">⭐ 收藏</option>
      </select>
      <button class="btn" id="btnShuffle" onclick="S.toggleShuffle()">🔀 随机</button>
      <button class="btn" onclick="S.reset()" style="color:var(--danger)">🔄</button>
    </div>
  </div>
</div>

<div class="prog">
  <div class="prog-bar"><div class="prog-fill" id="progFill"></div></div>
  <div class="prog-info"><span id="progLabel">准备中...</span><span id="progCount"></span></div>
</div>

<main id="main"></main>
<div class="toast" id="toast"></div>

<script>
// ═══════════════ DATA ═══════════════
const QS = ''' + jmod.dumps(clean, ensure_ascii=False) + r''';
const GROUP_AUTHORS = ''' + jmod.dumps(authors_js, ensure_ascii=False) + r''';

// ═══════════════ STATE ═══════════════
const S = {
  mode: 'study',
  idx: 0,
  pool: [],
  answered: false,
  shuffle: false,
  history: {},
  starred: {},

  init() {
    try{this.history=JSON.parse(localStorage.eyetest_h||'{}')}catch(e){}
    try{this.starred=JSON.parse(localStorage.eyetest_s||'{}')}catch(e){}

    // build author dropdown with optgroups
    const sel=document.getElementById('selAuthor');
    for(const [groupName, authors] of Object.entries(GROUP_AUTHORS)){
      // Add a group separator option
      const og = document.createElement('option');
      og.textContent = '── ' + groupName + ' ──';
      og.value = 'group:' + groupName;
      og.className = 'optgroup';
      og.style.fontWeight = '700';
      og.style.color = 'var(--accent2)';
      sel.appendChild(og);
      // Add author options
      authors.forEach(a => {
        const o = document.createElement('option');
        o.value = a;
        o.textContent = '  ' + a;
        sel.appendChild(o);
      });
    }

    this.apply();
    this.kbd();
  },

  save(){localStorage.eyetest_h=JSON.stringify(this.history);localStorage.eyetest_s=JSON.stringify(this.starred)},

  apply(){
    let pool=QS.map((q,i)=>({...q,orig:i}));
    const author=document.getElementById('selAuthor').value;
    const scope=document.getElementById('selScope').value;

    if(author!=='all'){
      if(author.startsWith('group:')){
        // Filter by group
        const groupLabel = author.replace('group:', '');
        const reverseMap = {'第一组':'眼科出题第一组','第二组':'眼科出题第二组','第三组':'眼科出题第三组'};
        const realGroup = reverseMap[groupLabel] || groupLabel;
        pool=pool.filter(q=>q.group===realGroup);
      } else {
        pool=pool.filter(q=>q.author===author);
      }
    }

    if(scope==='unanswered') pool=pool.filter(q=>!(q.orig in this.history));
    else if(scope==='wrong') pool=pool.filter(q=>this.history[q.orig]&&!this.history[q.orig].ok);
    else if(scope==='starred') pool=pool.filter(q=>q.orig in this.starred);

    if(this.shuffle){for(let i=pool.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[pool[i],pool[j]]=[pool[j],pool[i]]}}

    this.pool=pool;this.idx=0;
    if(pool.length===0){this.renderEmpty()}else{this.render()}
    this.updateProg();
  },

  toggleShuffle(){
    this.shuffle=!this.shuffle;
    document.getElementById('btnShuffle').classList.toggle('on',this.shuffle);
    this.apply();
  },

  setMode(m){
    this.mode=m;
    document.querySelectorAll('#modePill button').forEach(b=>b.classList.toggle('on',b.dataset.m===m));
    if(this.pool.length&&this.answered)this.render();
  },

  // ── render ──
  render(){
    if(this.idx>=this.pool.length){this.idx=0;if(this.shuffle)return this.apply()}
    const q=this.pool[this.idx];
    const oKeys=Object.keys(q.o).sort();
    const star=this.starred[q.orig];
    const prev=this.history[q.orig];
    const grp = q.group ? q.group.replace('眼科出题','') : '';

    let prevBadge='';
    if(prev){prevBadge=prev.ok
      ?'<span style="color:var(--success)">✓ 上次对</span>'
      :'<span style="color:var(--danger)">✗ 上次错</span>'}

    let opts='';
    oKeys.forEach((l,i)=>{
      opts+=`<div class="opt" data-l="${l}" onclick="S.pick('${l}')">
        <div class="opt-letter">${l}</div>
        <div class="opt-text">${this.esc(q.o[l])}</div></div>`;
    });

    document.getElementById('main').innerHTML=`
      <div class="card">
        <div class="qmeta">
          <span>${this.idx+1}/${this.pool.length} · ${this.esc(q.author)}</span>
          <span class="grp">${this.esc(grp)}</span>
          <span class="star" onclick="S.toggleStar(${q.orig})">${star?'⭐':'☆'}</span>
          ${prevBadge}
        </div>
        <div class="qtext">${this.esc(q.q)}</div>
        <div class="opts">${opts}</div>
        <div class="fb" id="fb"></div>
        <div class="acts">
          <button class="act go" id="btnNext" style="display:none" onclick="S.next()">
            下一题 <kbd>Space</kbd>
          </button>
          <button class="act" onclick="S.toggleStar(${q.orig})">${star?'⭐':'☆'} 收藏 <kbd>S</kbd></button>
        </div>
      </div>`;
    this.answered=false;
    this.updateProg();
    window.scrollTo({top:0,behavior:'smooth'});
  },

  renderEmpty(){
    document.getElementById('main').innerHTML=`
      <div class="empty">
        <h2>🎉 ${this.pool.length===0?'没有匹配的题目':'完成!'}</h2>
        <p>当前筛选条件下暂无题目，换个筛选试试</p>
        <button class="act go" onclick="S.apply()">🔄 刷新</button>
      </div>`;
    this.updateProg();
  },

  // ── answer ──
  pick(letter){
    if(this.answered)return;
    this.answered=true;

    const q=this.pool[this.idx];
    const correct=q.a.toUpperCase();
    const ok=letter===correct;

    document.querySelectorAll('.opt').forEach(el=>{
      el.classList.add('dim');
      const l=el.dataset.l;
      if(l===correct)el.classList.add('ok');
      if(l===letter&&!ok)el.classList.add('bad');
    });

    this.history[q.orig]={ok,ts:Date.now(),chosen:letter};
    this.save();

    const fb=document.getElementById('fb');
    fb.className='fb on '+(ok?'good':'bad');
    let html=ok?`<div class="fb-title">✅ 正确!</div>`:`<div class="fb-title">❌ 错误 — 答案是 <b>${correct}</b></div>`;
    if(q.e)html+=`<div class="fb-expl">💡 ${this.esc(q.e)}</div>`;
    fb.innerHTML=html;

    document.getElementById('btnNext').style.display='inline-block';
    document.getElementById('btnNext').focus();

    this.updateProg();
    this.toast(ok?'✅ 正确!':'❌ 错误',ok);

    if(this.mode==='speed'&&ok)setTimeout(()=>this.next(),650);
  },

  next(){
    this.idx++;
    if(this.idx>=this.pool.length){
      this.idx=0;
      if(this.shuffle)return this.apply();
    }
    this.render();
  },

  toggleStar(orig){
    this.starred[orig]=!(orig in this.starred);
    this.save();
    if(this.pool.length&&this.pool[this.idx].orig===orig)this.render();
  },

  reset(){
    if(!confirm('清除所有做题记录？不可撤销。'))return;
    this.history={};this.starred={};this.save();this.apply();
  },

  // ── progress ──
  updateProg(){
    const t=this.pool.length;
    if(!t){
      document.getElementById('progFill').style.width='0%';
      document.getElementById('progLabel').textContent='没有题目';
      document.getElementById('progCount').textContent='0/0';
      return;
    }
    let done=0,ok=0;
    this.pool.forEach(q=>{if(q.orig in this.history){done++;if(this.history[q.orig].ok)ok++}});
    document.getElementById('progFill').style.width=Math.round(done/t*100)+'%';
    document.getElementById('progLabel').textContent=`完成 ${done}/${t} · 正确率 ${done?Math.round(ok/done*100):0}%`;
    document.getElementById('progCount').textContent=`${this.idx+1}/${t}`;
  },

  // ── keyboard ──
  kbd(){
    document.addEventListener('keydown',e=>{
      if(e.target.tagName==='INPUT'||e.target.tagName==='TEXTAREA')return;
      const k=e.key.toUpperCase();

      if(!this.answered&&this.pool.length){
        const letters=Object.keys(this.pool[this.idx].o).sort();
        if(k>='1'&&k<='5'){const idx=parseInt(k)-1;if(idx<letters.length)this.pick(letters[idx])}
        else if(k>='A'&&k<='E')this.pick(k);
      }

      if(k===' '||k==='ENTER'||k==='ARROWRIGHT'){e.preventDefault();if(this.answered)this.next()}
      if(k==='M')this.setMode(this.mode==='study'?'speed':'study');
      if(k==='S'&&this.pool.length){const q=this.pool[this.idx];this.toggleStar(q.orig)}
      if(k==='ARROWLEFT'&&this.idx>0){this.idx--;this.render()}
    });
  },

  esc(s){const d=document.createElement('div');d.textContent=s;return d.innerHTML},

  toast(msg,ok){
    const t=document.getElementById('toast');
    t.textContent=msg;t.className='toast on '+(ok?'ok':'ng');
    clearTimeout(this._tt);this._tt=setTimeout(()=>t.className='toast',1200);
  }
};

S.init();
</script>
</body>
</html>'''

outpath = os.path.join(BASE, 'quiz.html')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write(html)

size = os.path.getsize(outpath) / 1024
print(f"quiz.html written ({size:.0f} KB, {len(clean)} questions)")
# Print groups
for g in sorted_groups:
    label = GROUP_LABEL.get(g, g)
    total = sum(group_authors[g].values())
    authors_list = ', '.join(f'{a}({c})' for a,c in sorted(group_authors[g].items(), key=lambda x:-x[1]))
    print(f"  {label}: {total}题 — {authors_list}")
