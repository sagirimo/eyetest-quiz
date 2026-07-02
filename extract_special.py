#!/usr/bin/env python3
"""
Special extractor for files that v5 can't handle well:
  - 黄婉雯: no option labels, no answers
  - 邬清杨: unlabeled options, no answers
  - 孙晟佳 PDF: shared-option groups + text answers
  - 邓敏智: multi-select + missing A. label + single-line options
  - Adds multi-select support to existing v5 output
"""
import sys, docx, pdfplumber, json, re, os

sys.stdout.reconfigure(encoding='utf-8')
BASE = os.path.dirname(os.path.abspath(__file__))
LABELS = ['A','B','C','D','E']


# ───────────────────────────────────────────────────────────────────
# 1. 黄婉雯 — no option labels, no answers
# ───────────────────────────────────────────────────────────────────

def parse_huangwanwen():
    fpath = os.path.join(BASE, '眼科出题第三组', '2210122918-黄婉雯-眼科.docx')
    doc = docx.Document(fpath)
    lines = [l.strip() for l in (p.text for p in doc.paragraphs) if l.strip()]
    questions = []
    current_q = None
    current_opts = []
    skip = {
        '眼科题目', '黄婉雯 2210122918',
        '眼科题_黄婉雯', '眼科题目黄婉雯',
    }

    def flush():
        nonlocal current_q, current_opts
        if current_q and len(current_opts) >= 4:
            questions.append({
                'question': current_q,
                'options': dict(zip(LABELS, current_opts[:5])),
                'answer': '', 'needs_answer': True, 'explanation': '',
                'author': '黄婉雯', 'group': '眼科出题第三组',
                'filename': '2210122918-黄婉雯-眼科.docx',
            })
        current_q = None
        current_opts = []

    for l in lines:
        if l in skip or re.match(r'^[一二三四五六七八九十][、\.]', l):
            flush()
            continue
        if current_q is None:
            current_q = l
            current_opts = []
        else:
            current_opts.append(l)
            if len(current_opts) == 5:
                flush()

    flush()
    print(f"黄婉雯: {len(questions)} questions (all need AI answers)")
    return questions


# ───────────────────────────────────────────────────────────────────
# 2. 邬清杨 — mixed, mostly no answers
# ───────────────────────────────────────────────────────────────────

def parse_wuqingyang(existing_qs):
    """Return questions NOT already in existing_qs."""
    fpath = os.path.join(BASE, '眼科出题第三组', '邬清杨-2210122916-眼科作业.docx')
    doc = docx.Document(fpath)
    lines = [l.strip() for l in (p.text for p in doc.paragraphs) if l.strip()]

    existing_texts = {q['question'][:60] for q in existing_qs}
    questions = []
    current_q = None
    current_opts = {}
    current_plain = []
    has_labels = False

    skip_lines = {'眼科作业', '邬清杨 2210122916', '邬清杨2210122916'}

    def flush(answer=''):
        nonlocal current_q, current_opts, current_plain, has_labels
        if not current_q:
            return
        q_key = current_q[:60]
        if q_key in existing_texts:
            current_q = None; current_opts = {}; current_plain = []; has_labels = False
            return
        if has_labels and len(current_opts) >= 4:
            questions.append({
                'question': current_q,
                'options': dict(current_opts),
                'answer': answer, 'needs_answer': not bool(answer), 'explanation': '',
                'author': '邬清杨', 'group': '眼科出题第三组',
                'filename': '邬清杨-2210122916-眼科作业.docx',
            })
            existing_texts.add(q_key)
        elif not has_labels and len(current_plain) >= 4:
            questions.append({
                'question': current_q,
                'options': dict(zip(LABELS, current_plain[:5])),
                'answer': answer, 'needs_answer': not bool(answer), 'explanation': '',
                'author': '邬清杨', 'group': '眼科出题第三组',
                'filename': '邬清杨-2210122916-眼科作业.docx',
            })
            existing_texts.add(q_key)
        current_q = None; current_opts = {}; current_plain = []; has_labels = False

    for l in lines:
        if l in skip_lines or re.match(r'^[一二三四五六七八九十][、\.]', l):
            flush()
            continue

        # Labeled option
        opt_m = re.match(r'^([A-Ea-e])\s*[\.\、\s]\s*(.+)', l)
        if opt_m and current_q:
            has_labels = True
            current_opts[opt_m.group(1).upper()] = opt_m.group(2).strip()
            continue

        # Answer marker
        ans_m = re.match(r'^(?:正确)?答案[：:]\s*([A-Ea-e])', l)
        if ans_m and current_q:
            flush(ans_m.group(1).upper())
            continue

        # Short answer (essay) - skip
        if re.match(r'^答[：:]', l) or l.startswith('（') or len(l) > 120:
            continue

        # New question
        is_opt = bool(re.match(r'^[A-Ea-e]\s*[\.\、]', l))
        is_ans = bool(re.match(r'^(?:正确)?答案', l))
        if not is_opt and not is_ans:
            if current_q:
                if (has_labels and len(current_opts) >= 4) or (not has_labels and len(current_plain) >= 4):
                    flush()
                elif not (current_opts or current_plain):
                    # Question continuation
                    current_q += ' ' + l
                    continue
                else:
                    flush()
            current_q = l
        else:
            if current_q and not has_labels:
                current_plain.append(l)

    flush()
    print(f"邬清杨 (new): {len(questions)} questions")
    return questions


# ───────────────────────────────────────────────────────────────────
# 3. 孙晟佳 PDF — shared option groups + text answers
# ───────────────────────────────────────────────────────────────────

def parse_sunshengijia(existing_qs):
    fpath = os.path.join(BASE, '眼科出题第二组', '孙晟佳_2110122903_眼科命题.pdf')
    with pdfplumber.open(fpath) as pdf:
        text = '\n'.join(p.extract_text() or '' for p in pdf.pages)

    lines = [l.strip() for l in text.split('\n') if l.strip()]
    existing_texts = {q['question'][:60] for q in existing_qs}
    questions = []

    # Step 1: find shared-option blocks ("N～M题共用选项")
    shared_map = {}  # qnum → {A: text, B: text, ...}
    i = 0
    while i < len(lines):
        l = lines[i]
        m = re.match(r'^(\d+)[～~、，,到-](\d+)题共用(?:选项|题干)?', l)
        # Also try "N、M题共用" (comma separated)
        if not m:
            m = re.match(r'^(\d+)[、，,]\s*(\d+)\s*题共用', l)
        if m:
            start, end = int(m.group(1)), int(m.group(2))
            opts = {}
            j = i + 1
            while j < len(lines) and len(opts) < 5:
                om = re.match(r'^([A-E])\s+(.+)', lines[j])
                if om:
                    opts[om.group(1)] = om.group(2).strip()
                    j += 1
                elif re.match(r'^\d+\s', lines[j]) or re.match(r'^第\d+题', lines[j]):
                    break
                else:
                    j += 1
            if opts:
                for n in range(start, end + 1):
                    shared_map[n] = opts
        i += 1

    # Step 2: parse questions
    i = 0
    while i < len(lines):
        l = lines[i]

        # Shared-option question with inline text answer: "N question 【answer_text】"
        m = re.match(r'^(\d+)\s+(.+?)\s*【(.+?)】\s*$', l)
        if m:
            qnum = int(m.group(1))
            qtext = m.group(2).strip()
            ans_text = m.group(3).strip()
            if qnum in shared_map and 1 <= qnum <= 50:
                opts = dict(shared_map[qnum])
                answer = ''
                for ltr, val in opts.items():
                    if ans_text in val or val in ans_text:
                        answer = ltr
                        break
                q_key = qtext[:60]
                if q_key not in existing_texts:
                    questions.append({
                        'question': qtext,
                        'options': opts,
                        'answer': answer,
                        'needs_answer': not bool(answer),
                        'explanation': '',
                        'author': '孙晟佳',
                        'group': '眼科出题第二组',
                        'filename': '孙晟佳_2110122903_眼科命题.pdf',
                    })
                    existing_texts.add(q_key)
                i += 1
                continue

        # Regular numbered question: "N question_start"
        m2 = re.match(r'^(\d+)[\.\s]\s*(.+)', l)
        if m2:
            qnum = int(m2.group(1))
            if 1 <= qnum <= 50 and qnum not in shared_map:
                qtext = m2.group(2).strip()
                # Collect options
                opts = {}
                j = i + 1
                while j < len(lines) and len(opts) < 5:
                    om = re.match(r'^([A-E])\s+(.+)', lines[j])
                    if om:
                        opts[om.group(1)] = om.group(2).strip()
                        j += 1
                    elif re.match(r'^\d+[\.\s]', lines[j]) and not re.match(r'^[A-E]\s', lines[j]):
                        break
                    elif re.match(r'^[○●]', lines[j]):
                        j += 1  # skip multi-choice format lines
                    else:
                        # Could be question continuation
                        if not opts:
                            qtext += ' ' + lines[j].strip()
                        j += 1
                        if len(opts) == 0 and j - i > 5:
                            break

                if len(opts) >= 4:
                    q_key = qtext[:60]
                    if q_key not in existing_texts:
                        questions.append({
                            'question': qtext,
                            'options': opts,
                            'answer': '',
                            'needs_answer': True,
                            'explanation': '',
                            'author': '孙晟佳',
                            'group': '眼科出题第二组',
                            'filename': '孙晟佳_2110122903_眼科命题.pdf',
                        })
                        existing_texts.add(q_key)
                i = j
                continue

        i += 1

    print(f"孙晟佳 (new): {len(questions)} questions")
    return questions


# ───────────────────────────────────────────────────────────────────
# 4. 邓敏智 — multi-select + missing A. + single-line options
# ───────────────────────────────────────────────────────────────────

def parse_dengmingzhi(existing_qs):
    fpath = os.path.join(BASE, '眼科出题第一组', '邓敏智-眼科出题.docx')
    doc = docx.Document(fpath)
    lines = [l.strip() for l in (p.text for p in doc.paragraphs) if l.strip()]

    existing_texts = {q['question'][:60] for q in existing_qs}
    questions = []
    i = 0
    current_q = None
    current_opts = {}

    def try_inline_opts(l):
        """Extract options from 'Text B. xxx C. xxx D. xxx E. xxx' format."""
        parts = re.split(r'\s+(?=[B-Ea-e]\.\s)', l)
        if len(parts) >= 2:
            opts = {}
            opts['A'] = parts[0].strip()
            for part in parts[1:]:
                pm = re.match(r'^([B-Ea-e])\.\s*(.+)', part)
                if pm:
                    opts[pm.group(1).upper()] = pm.group(2).strip()
            if len(opts) >= 4:
                return opts
        return None

    def flush(answer=''):
        nonlocal current_q, current_opts
        if not current_q or len(current_opts) < 2:
            current_q = None; current_opts = {}
            return
        q_key = current_q[:60]
        if q_key not in existing_texts:
            is_multi = len(answer) > 1
            questions.append({
                'question': current_q,
                'options': dict(current_opts),
                'answer': answer,
                'needs_answer': not bool(answer),
                'explanation': '',
                'author': '邓敏智',
                'group': '眼科出题第一组',
                'filename': '邓敏智-眼科出题.docx',
                'type': 'multi' if is_multi else 'single',
            })
            existing_texts.add(q_key)
        current_q = None; current_opts = {}

    while i < len(lines):
        l = lines[i]

        # Section headers
        if re.match(r'^[一二三四五六七八九十][、\.]', l) or re.match(r'^【第', l):
            i += 1; continue

        # Answer marker (single or multi-letter)
        ans_m = (re.match(r'^(?:【?正确?】?)?答案[：:】]\s*([A-Ea-e]{1,5})', l) or
                 re.match(r'^【答案】\s*([A-Ea-e]{1,5})', l) or
                 re.match(r'^答案[：:]\s*([A-Ea-e]{1,5})', l))
        if ans_m and current_q:
            flush(ans_m.group(1).upper())
            i += 1; continue

        # Labeled option: A. xxx
        opt_m = re.match(r'^([A-Ea-e])\s*[\.\、．]\s*(.+)', l)
        if opt_m and current_q:
            current_opts[opt_m.group(1).upper()] = opt_m.group(2).strip()
            i += 1; continue

        # Standalone multi-letter answer: "ABC", "ABCDE", etc.
        if current_q and current_opts and re.match(r'^([A-Ea-e]{2,5})\s*$', l):
            flush(l.strip().upper())
            i += 1; continue

        # Inline options: "text B. xxx C. xxx D. xxx E. xxx"
        if current_q and not current_opts:
            inline = try_inline_opts(l)
            if inline:
                current_opts = inline
                i += 1; continue

        # Unlabeled options (5 separate lines)
        # Heuristic: if current_q and no opts yet and line is short (< 50 chars) and not a question
        if current_q and not current_opts and len(l) < 60 and not re.search(r'[？?]', l):
            # Might be unlabeled option A - collect up to 5
            opts_plain = [l]
            j = i + 1
            while j < len(lines) and len(opts_plain) < 5:
                nl = lines[j]
                if (re.match(r'^[A-Ea-e]\s*[\.\、]', nl) or
                    re.match(r'^(?:正确)?答案', nl) or
                    re.match(r'^【答案】', nl) or
                    len(nl) > 80):
                    break
                opts_plain.append(nl)
                j += 1
            # Check if next line after opts is an answer
            if len(opts_plain) >= 4 and j < len(lines):
                next_l = lines[j]
                ans_m2 = (re.match(r'^(?:【?正确?】?)?答案[：:】]\s*([A-Ea-e]{1,5})', next_l) or
                          re.match(r'^【答案】\s*([A-Ea-e]{1,5})', next_l) or
                          re.match(r'^答案[：:]\s*([A-Ea-e]{1,5})', next_l))
                if ans_m2:
                    current_opts = dict(zip(LABELS, opts_plain[:5]))
                    flush(ans_m2.group(1).upper())
                    i = j + 1
                    continue

        # New question (not option, not answer)
        is_opt = bool(re.match(r'^[A-Ea-e]\s*[\.\、]', l))
        is_ans = bool(re.match(r'^(?:正确)?答案|^【答案】', l))
        is_ref = bool(re.match(r'^【参考答案】', l))
        if not is_opt and not is_ans and not is_ref and len(l) > 8:
            if current_q:
                # If we have enough options, save; otherwise append to question
                if len(current_opts) >= 2:
                    flush()
                else:
                    current_q += ' ' + l
                    i += 1; continue
            current_q = l

        i += 1

    flush()
    print(f"邓敏智 (new): {len(questions)} questions")
    return questions


# ───────────────────────────────────────────────────────────────────
# 5. Multi-select fix: add multi-select questions missed by v5
# ───────────────────────────────────────────────────────────────────

def extract_multiselect_from_v5_files(existing_qs):
    """Find multi-select questions from files where v5 got single-select only."""
    existing_texts = {q['question'][:60] for q in existing_qs}
    new_qs = []

    multiselect_files = [
        (os.path.join(BASE, '眼科出题第一组', '刘霁影45题(1).docx'), '刘霁影', '眼科出题第一组'),
        (os.path.join(BASE, '眼科出题第一组', '眼科见习复习题 2110902813 李明准.docx'), '李明准', '眼科出题第一组'),
    ]

    for fpath, author, group in multiselect_files:
        fname = os.path.basename(fpath)
        try:
            doc = docx.Document(fpath)
        except Exception as e:
            print(f"  SKIP {fname}: {e}")
            continue

        lines = [l.strip() for l in (p.text for p in doc.paragraphs) if l.strip()]
        i = 0
        current_q = None
        current_opts = {}
        current_type = ''

        while i < len(lines):
            l = lines[i]

            # Detect multi-select question header
            type_m = re.match(r'^【[^】]*多选[^】]*】|【[^】]*判断[^】]*】', l)
            if type_m:
                current_type = '多选' if '多选' in l else '判断'
                i += 1; continue

            # Skip single-select markers
            if re.match(r'^【[^】]*单选[^】]*】', l):
                current_type = '单选'
                i += 1; continue

            # Question start
            q_m = re.match(r'^(\d+)\s*[\.\、]\s*(?:【多选题】|【单选题】|【判断题】)?\s*(.+)', l)
            if q_m:
                if current_q and len(current_opts) >= 2:
                    q_key = current_q[:60]
                    if q_key not in existing_texts:
                        new_qs.append({
                            'question': current_q,
                            'options': dict(current_opts),
                            'answer': current_q.get('_ans', ''),
                            'needs_answer': not bool(current_q.get('_ans', '')),
                            'explanation': '',
                            'author': author, 'group': group, 'filename': fname,
                            'type': current_type,
                        })
                        existing_texts.add(q_key)
                current_q = {'text': q_m.group(2), '_ans': ''}
                current_opts = {}
                i += 1; continue

            # Options
            opt_m = re.match(r'^([A-Ea-e])\s*[\.\、]\s*(.+)', l)
            if opt_m and current_q:
                current_opts[opt_m.group(1).upper()] = opt_m.group(2).strip()
                i += 1; continue

            # Multi-letter answer
            ans_m = re.match(r'^答案[：:]\s*([A-Ea-e]{1,5})', l)
            if ans_m and current_q:
                current_q['_ans'] = ans_m.group(1).upper()
                q_key = current_q['text'][:60]
                if q_key not in existing_texts and len(current_opts) >= 2:
                    new_qs.append({
                        'question': current_q['text'],
                        'options': dict(current_opts),
                        'answer': current_q['_ans'],
                        'needs_answer': False,
                        'explanation': '',
                        'author': author, 'group': group, 'filename': fname,
                        'type': current_type,
                    })
                    existing_texts.add(q_key)
                current_q = None; current_opts = {}
                i += 1; continue

            i += 1

        print(f"{author} (multi-select new): {sum(1 for q in new_qs if q['author'] == author)}")

    return new_qs


# ───────────────────────────────────────────────────────────────────
# MAIN
# ───────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    # Load existing v5 questions
    with open(os.path.join(BASE, 'questions.json'), encoding='utf-8') as f:
        existing = json.load(f)
    print(f"Loaded {len(existing)} existing questions from questions.json")
    print()

    new_questions = []

    # Run special parsers
    new_questions += parse_huangwanwen()
    new_questions += parse_wuqingyang(existing + new_questions)
    new_questions += parse_sunshengijia(existing + new_questions)
    new_questions += parse_dengmingzhi(existing + new_questions)
    # new_questions += extract_multiselect_from_v5_files(existing + new_questions)

    # Combine
    all_qs = existing + new_questions

    # Renumber
    for idx, q in enumerate(all_qs, 1):
        q['num'] = idx

    answered = sum(1 for q in all_qs if q.get('answer') and not q.get('needs_answer'))
    needs_ai = sum(1 for q in all_qs if q.get('needs_answer') or not q.get('answer'))

    print(f"\n{'='*60}")
    print(f"Total questions: {len(all_qs)}")
    print(f"  With answers:  {answered}")
    print(f"  Needs AI:      {needs_ai}")

    # Save full combined
    out = os.path.join(BASE, 'questions_combined.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(all_qs, f, ensure_ascii=False, indent=2)
    print(f"Saved to {out}")

    # Save just unanswered for AI processing
    unanswered = [q for q in new_questions if q.get('needs_answer') or not q.get('answer')]
    unanswered_out = os.path.join(BASE, 'needs_ai_answers.json')
    with open(unanswered_out, 'w', encoding='utf-8') as f:
        json.dump(unanswered, f, ensure_ascii=False, indent=2)
    print(f"Unanswered new questions: {len(unanswered)} → {unanswered_out}")
