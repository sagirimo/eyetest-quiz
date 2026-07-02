#!/usr/bin/env python3
"""Add ophthalmology explanations to questions that lack them."""
import json, re, os

BASE = "/Users/moliex/projects/eyetest"
with open(os.path.join(BASE, 'questions.json')) as f:
    questions = json.load(f)

missing = [q for q in questions if not q.get('explanation') or len(q['explanation'].strip()) < 5]
print(f"Questions needing explanations: {len(missing)}/{len(questions)}")


def generate_explanation(q):
    """Generate a concise, medically accurate explanation."""
    q_text = q.get('question', '')
    answer = q.get('answer', '').upper()
    opts = q.get('options', {})
    correct_text = opts.get(answer, '')
    qt = q_text

    # ── CORNEA ──
    if any(kw in qt for kw in ['角膜屈光', '角膜约占']):
        return "角膜屈光力约43D，占眼球总屈光力的2/3（约70%），是眼球最主要的屈光介质。"
    if any(kw in qt for kw in ['角膜五层', '角膜组织学', '角膜从外到内', '角膜从前向后', '角膜分层']):
        return "角膜从外到内分五层：上皮细胞层→前弹力层→基质层→后弹力层→内皮细胞层。上皮和后弹力层可再生。"
    if '可再生' in qt or '再生能力' in qt or '具有再生' in qt:
        return "角膜中上皮细胞层和后弹力层可再生；前弹力层和内皮细胞层损伤后不能再生。基质层损伤后由瘢痕修复。"
    if '角膜透明' in qt or '维持角膜透明' in qt:
        return "角膜透明性依赖上皮完整、基质胶原规则排列、无血管、内皮泵功能。内皮细胞层是维持透明的关键。"
    if '角膜营养' in qt:
        return "角膜无血管，营养主要来自房水、泪膜及角膜缘血管网。"
    if '角膜内皮' in qt:
        return "角膜内皮细胞几乎不进行有丝分裂，损伤后依靠邻近细胞扩张移行填补，不能真正再生。"
    if '角膜厚度' in qt or '角膜中央' in qt:
        return "角膜中央厚约0.5mm，周边约1mm。基质层占全层约90%。"
    if '角膜横径' in qt or '小角膜' in qt:
        return "正常成人角膜横径约11.5-12mm，<10mm为病理性小角膜。"
    if '角膜感觉' in qt or '角膜神经' in qt:
        return "角膜感觉神经丰富，由三叉神经眼支支配。"

    # ── AQUEOUS / IOP ──
    if '房水' in qt and ('产生' in qt or '分泌' in qt or '生成' in qt):
        return "房水由睫状突非色素上皮细胞主动分泌产生。"
    if '房水' in qt and ('途径' in qt or '循环' in qt or '外流' in qt or '排出' in qt or '顺序' in qt):
        return "房水主要外流途径：睫状突→后房→瞳孔→前房→小梁网→Schlemm管→集液管→睫状前静脉。次要途径（10-20%）为葡萄膜巩膜途径。"
    if '眼压' in qt and ('正常' in qt or '范围' in qt or '统计学' in qt):
        return "正常眼压统计学范围10~21mmHg，24h波动<8mmHg，双眼差值<5mmHg。"
    if '眼压测量' in qt or ('金标准' in qt and '眼压' in qt):
        return "Goldmann压平眼压计是眼压测量的金标准。指测法正常记为Tn。"

    # ── CRYSTALLINE LENS / CATARACT ──
    if '白内障' in qt and '定义' in qt:
        return "白内障是晶状体透明度降低或颜色改变导致光学质量下降的退行性改变。"
    if '白内障' in qt and '膨胀期' in qt:
        return "膨胀期：晶状体吸水膨胀→前房变浅+虹膜投影阳性，可能诱发急性闭角型青光眼。"
    if '白内障' in qt and '初发期' in qt:
        return "初发期：晶状体周边皮质楔形、车轮样混浊，向中央发展。"
    if '白内障' in qt and '成熟期' in qt:
        return "成熟期：晶状体全混浊，虹膜投影消失，视力严重下降。"
    if '白内障' in qt and '过熟期' in qt:
        return "过熟期：囊膜皱缩，核下沉，皮质液化，可发生晶状体溶解性青光眼。"
    if '白内障' in qt and ('手术时机' in qt or '何时手术' in qt):
        return "白内障手术时机：视力低于0.5且影响工作生活即可手术，不必等到成熟期。"
    if '超声乳化' in qt or 'phaco' in qt:
        return "超声乳化白内障吸除+IOL植入术（Phaco）特点：切口小、时间短、表麻无痛、恢复快、术后散光小。"
    if '白内障' in qt and '最常见' in qt and ('类型' in qt or '年龄' in qt):
        return "年龄相关性白内障分三型：皮质性（最常见）、核性、后囊下性。"
    if '晶状体' in qt and ('无血管' in qt or '解剖' in qt or '生理' in qt):
        return "晶状体无血管和神经，透明，营养来自房水和玻璃体，由晶体囊+晶体纤维组成。"
    if '晶状体' in qt and '富含血管' in qt:
        return "晶状体本身无血管——'富含血管'是错误描述。"
    if '后发性白内障' in qt or 'PCO' in qt:
        return "后发性白内障是白内障术后最常见的并发症，因残留晶状体上皮细胞增殖迁移所致。"

    # ── GLAUCOMA ──
    if '青光眼' in qt and ('共同特征' in qt or '共同性损害' in qt or '共同' in qt):
        return "青光眼以视神经凹陷性萎缩+视野缺损为共同特征，病理性眼压升高是主要危险因素。"
    if '闭角型青光眼' in qt and '急性' in qt and ('瞳孔' in qt and ('散大' in qt or '大' in qt)):
        return "急性闭角型青光眼：瞳孔括约肌麻痹→瞳孔散大（竖椭圆形），对光反射消失，与虹膜炎的瞳孔缩小鉴别。"
    if '闭角型青光眼' in qt and '急性' in qt and ('禁用' in qt or '避免' in qt or '不能使用' in qt):
        return "急性闭角型青光眼禁用散瞳药（阿托品、复方托吡卡胺），因散瞳可加重房角关闭、升高眼压。"
    if '闭角型青光眼' in qt and '急性' in qt and ('治疗' in qt or '急救' in qt or '处理' in qt):
        return "急救：甘露醇iv快速脱水+局部β阻滞剂/碳酸酐酶抑制剂缩瞳+前房穿刺。眼压控制后行激光虹膜周切术。"
    if '青光眼' in qt and '三联征' in qt:
        return "急性闭角型青光眼发作后三联征：角膜后色素性KP、虹膜节段性萎缩、晶状体前表面青光眼斑。"
    if '开角型青光眼' in qt and '一线用药' in qt:
        return "前列腺素衍生物（拉坦前列素、曲伏前列素）为POAG一线用药，增加葡萄膜巩膜途径房水外流。"
    if '开角型青光眼' in qt and '诊断' in qt:
        return "POAG诊断依据：眼压升高+青光眼性视盘改变（C/D扩大）+特征性视野缺损，房角开放。"
    if '婴幼儿型青光眼' in qt or '先天性青光眼' in qt:
        return "婴幼儿型青光眼三联征：畏光、流泪、眼睑痉挛。体征：角膜增大（>12mm）、角膜水肿混浊、眼压升高。"
    if '前列腺素' in qt and ('副作用' in qt or '不良反应' in qt):
        return "前列腺素衍生物副作用：虹膜色素加深、睫毛变长变粗、眼周皮肤色素沉着。"
    if '噻吗洛尔' in qt and '禁用' in qt:
        return "噻吗洛尔为β受体阻滞剂，禁用于哮喘、COPD、心动过缓、心力衰竭患者——可诱发支气管痉挛和心脏抑制。"
    if '卡替洛尔' in qt and '禁用' in qt:
        return "卡替洛尔为β受体阻滞剂，有哮喘/慢阻肺/心动过缓史者禁用。"
    if '毛果芸香碱' in qt and ('机制' in qt or '降低眼压' in qt):
        return "毛果芸香碱（缩瞳药）收缩瞳孔括约肌→牵拉小梁网→促进房水外流，主要用于闭角型青光眼。"
    if '甘露醇' in qt and '眼压' in qt:
        return "甘露醇（高渗剂）→提高血浆渗透压→玻璃体脱水浓缩→快速降眼压，用于急性高眼压急救。"
    if '碳酸酐酶' in qt or ('布林佐胺' in qt and '机制' in qt):
        return "碳酸酐酶抑制剂（布林佐胺/醋甲唑胺）抑制睫状突碳酸酐酶→减少房水生成。"
    if '正常眼压性青光眼' in qt or '低眼压性青光眼' in qt:
        return "正常眼压性青光眼（NTG）：眼压正常但存在青光眼性视神经损害，可能与血管因素、低颅压等有关。"
    if '高眼压症' in qt:
        return "高眼压症：眼压>21mmHg但视盘和视野完全正常，需定期随访而不必立即用药。"

    # ── RETINA ──
    if '视网膜中央动脉阻塞' in qt or 'CRAO' in qt:
        return "CRAO典型表现：视网膜苍白水肿+黄斑樱桃红斑。属眼科急诊，抢救黄金窗口90-120分钟。"
    if '樱桃红斑' in qt or '樱桃红' in qt:
        return "黄斑樱桃红斑是CRAO的特征性表现——因脉络膜供血保留红色，与周围苍白水肿的视网膜形成对比。"
    if '视网膜中央静脉阻塞' in qt or 'CRVO' in qt:
        return "CRVO典型表现：视网膜静脉迂曲扩张+广泛火焰状出血（暴风雨样）。缺血型易继发新生血管性青光眼。"
    if '视网膜脱离' in qt and '定义' in qt:
        return "视网膜脱离（RD）是视网膜神经上皮与色素上皮之间的分离。孔源性RD治疗原则为封闭裂孔复位视网膜。"
    if '黄斑' in qt and ('仅含' in qt or '主要分布' in qt or '感光细胞' in qt):
        return "黄斑中心凹仅含视锥细胞，是视觉最敏锐部位（明视觉+色觉）。周边视网膜以视杆细胞为主（暗视觉）。"
    if '视盘' in qt and ('生理盲点' in qt or '无感光' in qt or '视乳头' in qt):
        return "视盘（视乳头）无感光细胞，为生理盲点。正常C/D≤0.3，C/D≥0.6为可疑青光眼。"
    if '湿性' in qt and '黄斑变性' in qt:
        return "湿性AMD关键病理改变：脉络膜新生血管（CNV）。一线治疗：玻璃体腔抗VEGF注射。"
    if '干性' in qt and '黄斑变性' in qt:
        return "干性AMD以玻璃膜疣和地图状萎缩为特征，进展缓慢，以抗氧化维生素补充为主。"
    if '黄斑变性' in qt:
        return "AMD是老年人中心视力丧失主要原因。干性以玻璃膜疣/萎缩为主；湿性以CNV为特征需抗VEGF治疗。"
    if '视网膜色素变性' in qt:
        return "视网膜色素变性（RP）为遗传性光感受器变性，典型三联征：夜盲+进行性视野缩小+骨细胞样色素沉着。"
    if '黄斑水肿' in qt:
        return "黄斑水肿OCT表现：外丛状层和内核层出现低反射囊腔（囊样水肿）。FFA呈花瓣样高荧光。"
    if '视网膜静脉周围炎' in qt or 'Eales' in qt:
        return "Eales病（视网膜静脉周围炎）：青年男性、双眼发病、反复视网膜玻璃体出血。与结核相关。"

    # ── UVEITIS ──
    if ('虹膜睫状体炎' in qt or '前葡萄膜炎' in qt) and ('瞳孔' in qt and '缩小' in qt):
        return "急性前葡萄膜炎：虹膜充血水肿+瞳孔括约肌痉挛→瞳孔缩小。可与急性闭角型青光眼（瞳孔散大）鉴别。"
    if ('虹膜睫状体炎' in qt or '前葡萄膜炎' in qt) and '体征' in qt:
        return "急性前葡萄膜炎体征：睫状充血+角膜后KP+前房闪辉（Tyndall+）+瞳孔缩小+虹膜后粘连。"
    if ('虹膜睫状体炎' in qt or '前葡萄膜炎' in qt) and ('散瞳' in qt or '治疗' in qt):
        return "前葡萄膜炎治疗核心：散瞳防后粘连（阿托品/托吡卡胺）+糖皮质激素抗炎+病因治疗。"
    if 'VKH' in qt or 'Vogt' in qt or '小柳' in qt or '原田' in qt:
        return "VKH综合征：双眼渗出性视网膜脱离+晚霞样眼底+头痛耳鸣+皮肤白癜风/毛发变白。自身免疫性全葡萄膜炎。"
    if '交感性眼炎' in qt:
        return "交感性眼炎：一眼穿通伤后对侧眼发生肉芽肿性全葡萄膜炎。潜伏期2周~2年，最危险期伤后4-6周。"
    if 'HLA-B27' in qt or 'HLA' in qt and '葡萄膜炎' in qt:
        return "强直性脊柱炎伴前葡萄膜炎患者HLA-B27阳性率高达约90%。"
    if '睫状充血' in qt and '鉴别' in qt:
        return "睫状充血vs结膜充血：滴肾上腺素后睫状充血不变，结膜充血消失。睫状充血来自睫状前动脉。"
    if '肉芽肿性葡萄膜炎' in qt or '葡萄膜炎' in qt and '肉芽肿' in qt:
        return "肉芽肿性葡萄膜炎包括VKH、交感性眼炎、结核性等。特征：羊脂状KP、Busacca结节。"

    # ── CONJUNCTIVA / OCULAR SURFACE ──
    if '沙眼' in qt and '病原' in qt:
        return "沙眼由沙眼衣原体A、B、C血清型引起。我国汤飞凡、张晓楼1955年世界首次分离成功。"
    if '结膜炎' in qt and '淋球菌' in qt:
        return "淋球菌性结膜炎（新生儿脓漏眼）：大量脓性分泌物、病情凶险，需全身+局部抗生素治疗。"
    if '结膜炎' in qt and '细菌性' in qt and ('最常见' in qt or '病原' in qt or '致病' in qt):
        return "细菌性结膜炎最常见致病菌为表皮葡萄球菌和金黄色葡萄球菌。儿童常见的为流感嗜血杆菌。"
    if '结膜炎' in qt and '春季' in qt:
        return "春季角结膜炎：儿童青少年、双眼奇痒、黏丝状分泌物、上睑结膜铺路石样乳头。变态反应性疾病。"
    if '干眼' in qt and ('检查' in qt or '诊断' in qt):
        return "干眼常用检查：泪膜破裂时间BUT（<10s异常）、Schirmer试验（<10mm/5min异常）、角膜荧光素染色。"
    if '泪膜' in qt and ('组成' in qt or '成分' in qt):
        return "泪膜三层：脂质层（睑板腺）、水样层（泪腺）、粘蛋白层（结膜杯状细胞）。"
    if '干眼' in qt and ('蒸发' in qt or '分型' in qt or '类型' in qt):
        return "干眼分型：水液缺乏型（Sjögren综合征等）和蒸发过强型（睑板腺功能障碍MGD）。"
    if '泪道冲洗' in qt:
        return "泪道冲洗：原路返流→泪小管阻塞；下冲上返→泪总管阻塞；返流+脓→慢性泪囊炎（鼻泪管阻塞）。"
    if '溢泪' in qt and '原因' in qt:
        return "溢泪主要原因：泪道排出受阻（如鼻泪管阻塞），需与流泪（分泌过多）区分。"
    if '麦粒肿' in qt or '睑腺炎' in qt:
        return "睑腺炎（麦粒肿）是眼睑腺体急性化脓性炎症，最常见致病菌为金黄色葡萄球菌。"
    if '霰粒肿' in qt:
        return "霰粒肿（睑板腺囊肿）是睑板腺出口阻塞导致的慢性肉芽肿性炎症，无急性红/热/痛。"
    if '麦粒肿' in qt and '切口' in qt:
        return "外麦粒肿切开排脓时切口应与睑缘平行（减少瘢痕）。内麦粒肿切口与睑缘垂直。"
    if '睑板腺囊肿' in qt and '霰粒肿' not in qt:
        return "睑板腺囊肿（霰粒肿）是慢性非感染性肉芽肿，与急性化脓性睑腺炎不同。"

    # ── EYELID / SCLERA ──
    if '巩膜最薄' in qt:
        return "巩膜最薄处位于眼外肌附着处，最厚处在视神经周围。"
    if '巩膜最厚' in qt:
        return "巩膜最厚处位于视神经周围及角巩膜缘。"
    if '巩膜' in qt and '特征' in qt:
        return "巩膜质地坚韧，厚度各处不一（视神经周围最厚，肌附着处最薄），筛板为巩膜薄弱区。"

    # ── OPTIC NERVE / VISUAL PATHWAY ──
    if '视交叉' in qt and ('压迫' in qt or '偏盲' in qt or '颞侧' in qt):
        return "视交叉中部含双眼鼻侧视网膜交叉纤维，受压（如垂体瘤）→双眼颞侧偏盲。"
    if '视神经炎' in qt and '鉴别' in qt:
        return "视神经炎（中青年、眼球转动痛、中心暗点）vs 缺血性视神经病变（老年、不痛、扇形缺损、视盘出血）。"
    if '视神经炎' in qt and '治疗' in qt:
        return "特发性（脱髓鞘性）视神经炎首选糖皮质激素冲击治疗。"
    if '视神经炎' in qt:
        return "视神经炎典型表现：中青年突发视力下降+眼球转动痛+RAPD+中心暗点。"
    if 'RAPD' in qt or '相对性瞳孔传入障碍' in qt:
        return "RAPD（相对性瞳孔传入障碍）：患眼传入通路受损→交替光照时患侧瞳孔先收缩继而散大。提示视神经或视网膜病变。"
    if '视神经长' in qt or '视神经分' in qt or '视神经全' in qt:
        return "视神经分四段：眼内段1mm→眶内段25mm（最长）→管内段9mm→颅内段16mm。"
    if '视盘水肿' in qt:
        return "视盘水肿常见原因：颅内压增高、视神经炎、前部缺血性视神经病变、高血压视网膜病变IV级等。"
    if '同向性偏盲' in qt or '同侧偏盲' in qt:
        return "视束及以后病变→双眼对侧同向性偏盲。视放射病变可伴黄斑回避（枕叶病变时黄斑区视力保留）。"
    if '黄斑回避' in qt:
        return "黄斑回避见于枕叶皮质病变——黄斑区双重供血（大脑中动脉+大脑后动脉），故枕叶梗死时黄斑视力可保留。"
    if '颞侧偏盲' in qt:
        return "双眼颞侧偏盲最常见于视交叉中部受压（如垂体瘤），因交叉纤维（鼻侧视网膜）受损。"
    if '象限盲' in qt or '象限偏盲' in qt:
        return "象限盲多由视放射部分纤维受损引起，颞叶病变→同侧上象限盲，顶叶病变→同侧下象限盲。"

    # ── REFRACTIVE ──
    if '近视' in qt and ('分类' in qt or '高度' in qt or '轻度' in qt):
        return "近视按程度：轻度<-3.00D，中度-3.00D~-6.00D，高度>-6.00D。按病因分轴性近视和屈光性近视。"
    if '近视' in qt and '屈光' in qt and '特点' in qt:
        return "近视眼：调节静止时平行光线聚焦于视网膜之前，需凹透镜矫正。主要原因为眼轴过长或屈光力过强。"
    if '远视' in qt and ('定义' in qt or '屈光' in qt or '特点' in qt):
        return "远视眼：平行光线聚焦于视网膜之后，需凸透镜矫正。婴幼儿多为生理性远视（眼球未发育完全）。"
    if '远视' in qt and '调节' in qt:
        return "远视眼看远看近均需调节，未矫正的中高度远视可导致调节性内斜视。"
    if '弱视' in qt and ('治疗' in qt or '年龄' in qt or '最佳' in qt):
        return "弱视治疗最佳年龄为3-6岁（视觉发育关键期）。超过12岁治疗效果极差。早发现早治疗是关键。"
    if '弱视' in qt and ('分类' in qt or '定义' in qt or '形觉剥夺' in qt):
        return "弱视分型：斜视性、屈光参差性、屈光不正性、形觉剥夺性。屈光参差性弱视多单眼发病。"
    if '调节' in qt and '机制' in qt:
        return "看近物时：睫状肌收缩→悬韧带松弛→晶状体借自身弹性变凸→屈光力增加。看远时睫状肌松弛。"
    if '近反射' in qt and ('三联' in qt or '联动' in qt):
        return "近反射三联征：调节+集合（双眼会聚）+瞳孔缩小。眼压下降不属于近反射。"
    if '内斜' in qt and '调节性' in qt:
        return "调节性内斜视最常见病因为高度远视——过度调节引起过度集合，导致内斜。"
    if '共同性斜视' in qt:
        return "共同性斜视：眼球运动正常、无复视、第一斜视角=第二斜视角。麻痹性斜视反之。"
    if '麻痹性斜视' in qt:
        return "麻痹性斜视：眼球运动受限、复视、代偿头位、第二斜视角>第一斜视角。"
    if '单视' in qt or '同时视' in qt or '立体视' in qt:
        return "双眼单视功能三级：同时视（最低）→融合→立体视（最高）。同视机可检查各级功能。"
    if '正视' in qt and '眼轴' in qt:
        return "正常成人眼轴长约24mm。眼轴每延长1mm≈近视增加3.00D。"
    if '调节力' in qt or '调节' in qt and '单位' in qt:
        return "调节力的单位为屈光度（D），1D=1/焦距(米)。"
    if '正视' in qt and '40cm' in qt:
        return "注视40cm处目标时调节需求=1/0.4=2.50D。"
    if 'Gullstrand' in qt:
        return "Gullstrand模型眼中，调节静止时眼球总屈光力约58.64D。"

    # ── OCULAR EXAMINATION ──
    if '视力表' in qt and ('检查距离' in qt or '5米' in qt or '5m' in qt):
        return "国际标准视力表检查距离为5米。先查裸眼视力再查矫正视力，先右后左。"
    if '对数视力表' in qt and '5分记录' in qt:
        return "对数远视力表5分记录法：5.0对应小数记录1.0（标准正常视力）。"
    if ('视野' in qt and 'WHO' in qt and '盲' in qt) or ('视野' in qt and '小于' in qt and '盲' in qt):
        return "WHO规定视野半径<10°即为盲标准，无论中心视力如何。"
    if '荧光血管造影' in qt or '臂-视网膜' in qt:
        return "正常人行眼底荧光血管造影（FFA），臂-视网膜循环时间约7~12秒。"
    if 'OCT' in qt and '不正确' in qt:
        return "OCT可用于黄斑/视神经/神经纤维层检查，但不能用于脉络膜肿瘤的鉴别诊断（需B超或ICGA）。"
    if 'OCT' in qt or '相干光断层' in qt:
        return "OCT（光学相干断层扫描）为无创高分辨率视网膜断层成像，广泛用于黄斑疾病、青光眼评估。OCTA无需造影剂即可显示血管。"
    if '裂隙灯' in qt and '照明' in qt:
        return "裂隙灯常用照明法：直接焦点（最常用）、间接（观察KP/内皮）、后部反光（透明体细微病变）、镜面反射（内皮细胞）、弥散（全貌）。"
    if '检眼镜' in qt and '顺序' in qt:
        return "直接检眼镜检查顺序：先查视盘→再沿血管各象限→最后查黄斑。所见为正像，放大15倍。"
    if 'Amsler' in qt or '方格表' in qt:
        return "Amsler方格表是筛查黄斑区视功能（视物变形、暗点）最简便的首选工具。"
    if '视力检查' in qt and ('主观' in qt or '客观' in qt):
        return "视力检查属于主观检查（需被检者配合）。VEP（视觉诱发电位）是客观视功能检查。"
    if '瞳孔' in qt and '正常' in qt and '直径' in qt:
        return "正常人瞳孔在自然光线下直径约2.5~4.0mm，呈正圆形、双侧等大。"
    if '小孔视力' in qt or '针孔视力' in qt:
        return "小孔/针孔视力可减少球面像差和散光，提高屈光不正患者的视力，用于鉴别屈光不正性和器质性视力下降。"

    # ── CORNEAL DISEASE ──
    if '真菌性角膜炎' in qt and ('诱因' in qt or '危险因素' in qt or '最常见' in qt):
        return "真菌性角膜炎最常见诱因：植物性角膜外伤（农作物/树枝划伤）。温暖潮湿气候+角膜上皮缺损+滥用激素。"
    if '真菌性角膜炎' in qt and ('眼内感染' in qt or '穿孔' in qt):
        return "真菌性角膜炎即使未穿孔也可发生病原体性眼内感染（真菌穿透力强），禁用糖皮质激素。"
    if '真菌性角膜炎' in qt:
        return "真菌性角膜炎特点：亚急性起病，植物外伤史，症状较体征轻，溃疡呈牙膏状灰白，禁用激素。"
    if '细菌性角膜炎' in qt and '最常见' in qt:
        return "细菌性角膜炎最常见的致病菌为表皮葡萄球菌。铜绿假单胞菌性角膜炎虽然不最常见但最凶险。"
    if '铜绿假单胞菌' in qt or '绿脓杆菌' in qt:
        return "铜绿假单胞菌性角膜炎特点：潜伏期短、发展迅猛、淡绿色分泌物、易穿孔、前房积脓。需紧急治疗。"
    if '单纯疱疹病毒性角膜炎' in qt or 'HSK' in qt:
        return "HSK（单纯疱疹病毒性角膜炎）特征：反复发作、感冒/劳累诱因、角膜知觉减退、树枝/地图状溃疡。上皮型禁用激素。"
    if '棘阿米巴角膜炎' in qt:
        return "棘阿米巴角膜炎最常见诱因：长期佩戴隐形眼镜（尤其用自来水清洗镜片），特征为环形浸润、剧烈疼痛。"
    if '角膜炎' in qt and '角膜移植' in qt:
        return "感染性角膜溃疡一旦穿孔或即将穿孔，最佳治疗为治疗性角膜移植术。"
    if '圆锥角膜' in qt:
        return "圆锥角膜特征：角膜中央变薄呈锥状前突→高度近视+不规则散光。常染色体隐性遗传。角膜地形图可见下方变陡。"
    if '感染性角膜炎' in qt and '激素' in qt:
        return "病毒性角膜炎（上皮型HSK）和真菌性角膜炎均禁用糖皮质激素，会抑制免疫导致病情恶化穿孔。"

    # ── DIABETIC RETINOPATHY / HYPERTENSION ──
    if ('4-2-1' in qt or '421' in qt) and '糖尿病' in qt:
        return "重度NPDR的4-2-1原则：4个象限严重出血+2个象限静脉串珠+1个象限IRMA。满足一条可诊断。"
    if '增殖期' in qt and '糖尿病' in qt:
        return "PDR标志性改变：新生血管形成（视盘新生血管NVD、视网膜新生血管NVE），可致玻璃体积血和牵拉性RD。"
    if '糖尿病' in qt and '视网膜' in qt and '新生血管' in qt:
        return "新生血管形成是PDR的标志，VEGF升高是关键驱动因素。治疗：全视网膜光凝（PRP）+抗VEGF。"
    if '高血压' in qt and '视网膜' in qt and ('IV' in qt or '4级' in qt or '四级' in qt):
        return "高血压视网膜病变IV级（最严重）：视网膜出血+渗出+棉絮斑+视盘水肿。"
    if '高血压' in qt and '视网膜' in qt and '动静脉交叉' in qt:
        return "高血压视网膜病变可见动脉狭窄、动静脉交叉压迹（Gunn征/Salus征），提示慢性高血压。"
    if '视网膜中央动脉' in qt and '阻塞' in qt and '急诊' in qt:
        return "CRAO急诊处理：降眼压（前房穿刺/眼球按摩/降眼压药）+吸氧/高压氧+血管扩张剂+溶栓。争分夺秒！"

    # ── OCULAR TRAUMA ──
    if ('化学' in qt or '酸碱' in qt) and '烧伤' in qt:
        return "化学性眼烧伤急救首要步骤：立即用大量生理盐水/清水冲洗至少15-30分钟，翻转眼睑转动眼球彻底冲洗。不可等待！"
    if '碱烧伤' in qt and '酸烧伤' in qt:
        return "碱烧伤比酸烧伤更严重：强碱与组织蛋白形成可溶性皂化物→渗透力强→深层组织坏死。酸使蛋白凝固形成屏障穿透力弱。"
    if '碱烧伤' in qt and '严重' in qt:
        return "碱烧伤后果严重：强碱与组织蛋白形成可溶性皂化物，渗透力强，可在数秒内穿透角膜进入眼内。"
    if '眼球穿通伤' in qt:
        return "眼球穿通伤急救：无菌纱布遮盖→禁止冲洗/滴药→避免挤压眼球→禁取脱出的眼内容物→尽快转诊手术。"
    if '前房积血' in qt:
        return "前房积血分级：I级<1/3前房，II级1/3-2/3前房，III级>2/3前房。处理：半卧位+双眼遮盖+监测眼压。"
    if '电光性眼炎' in qt:
        return "电光性眼炎（紫外线角膜结膜炎）潜伏期4-6小时，典型症状：剧烈眼痛、畏光、流泪。常见于电焊工未戴防护镜。"
    if '化学性眼烧伤' in qt or '化学伤' in qt and '冲洗' in qt:
        return "化学伤现场急救：争分夺秒就地用大量清水冲洗（至少15-30min）→翻转眼睑、转动眼球彻底冲洗。"
    if '眼外伤' in qt and '单眼失明' in qt:
        return "眼外伤是单眼失明最主要的原因（青壮年第一位致盲原因）。"
    if '交感性眼炎' in qt:
        return "交感性眼炎：一眼穿通伤后→对侧眼肉芽肿性全葡萄膜炎。潜伏期2周~2年，最危险伤后4-6周。摘除诱发眼不影响交感眼病程。"

    # ── PHARMACOLOGY ──
    if '糖皮质激素' in qt and '禁忌' in qt:
        return "糖皮质激素眼部禁忌证：树枝状角膜炎（HSK上皮型）、真菌性角膜炎——可抑制免疫导致感染扩散、角膜穿孔。"
    if '阿托品' in qt and ('散瞳' in qt or '慢散' in qt or '儿童' in qt):
        return "1%阿托品眼膏为强效长效散瞳睫状肌麻痹剂，用于儿童慢散验光（尤其内斜视者）。点眼后须压迫内眦防全身吸收。"
    if '复方托吡卡胺' in qt or '托吡卡胺' in qt:
        return "托吡卡胺为快速短效散瞳剂，用于成人散瞳验光和眼底检查，作用时间4-6小时。"
    if '毛果芸香碱' in qt:
        return "毛果芸香碱（匹罗卡品）为拟胆碱/缩瞳药，通过缩瞳牵拉小梁网促进房水外流，用于闭角型青光眼。虹膜睫状体炎禁用。"
    if '溴莫尼定' in qt or '阿法根' in qt:
        return "溴莫尼定（α受体激动剂）通过抑制房水生成+增加葡萄膜巩膜外流双重机制降眼压。"
    if '儿童' in qt and '散瞳' in qt and '阿托品' in qt:
        return "伴有内斜视的儿童验光前须用1%阿托品眼膏慢散（强效睫状肌麻痹），避免调节对屈光度的影响。"

    # ── ANATOMY GENERAL ──
    if '眼球壁' in qt and ('分层' in qt or '三层' in qt):
        return "眼球壁由外向内三层：纤维膜（角膜+巩膜）、葡萄膜/血管膜（虹膜+睫状体+脉络膜）、视网膜。"
    if '屈光介质' in qt or '屈光间质' in qt or '屈光系统' in qt:
        return "眼球屈光介质包括：角膜、房水、晶状体、玻璃体。视网膜不是屈光介质（是感光组织）。"
    if '外直肌' in qt and '支配' in qt:
        return "外直肌由展神经（Ⅵ）支配。内直肌、上下直肌、下斜肌、提上睑肌由动眼神经（Ⅲ）支配。上斜肌由滑车神经（Ⅳ）支配。"
    if '上斜肌' in qt and '支配' in qt:
        return "上斜肌由滑车神经（Ⅳ）支配，是唯一由滑车神经支配的眼外肌。"
    if '眼眶' in qt and ('最薄' in qt or '爆裂' in qt):
        return "眶内侧壁最薄，最易发生爆裂性骨折。眶下壁也较薄弱，钝挫伤可致击出性骨折。"
    if '虹膜' in qt and ('描述' in qt or '错误的是' in qt):
        return "瞳孔开大肌受交感神经支配（散瞳），瞳孔括约肌受副交感神经（动眼神经）支配（缩瞳）。"
    if '睫状体' in qt and '错误的是' in qt:
        return "睫状肌为平滑肌，受副交感神经（动眼神经）支配，而非交感神经。睫状肌收缩→悬韧带松弛→晶状体变凸。"
    if '虹膜' in qt and '根部' in qt:
        return "虹膜根部较薄，钝挫伤时易从睫状体上离断（虹膜根部离断）。"
    if '房水' in qt and '不包括' in qt:
        return "房水成分：乳酸、维生素C、钠钾氯、少量蛋白和尿素。葡萄糖含量极低。"
    if '结膜' in qt and '构成' in qt and ('三部分' in qt or '球结膜' in qt):
        return "结膜由三部分构成：球结膜、睑结膜、穹窿部结膜。"
    if '眼表' in qt and '不属于' in qt:
        return "眼表包括角膜、结膜、睑缘、泪膜。虹膜炎属于眼内葡萄膜疾病，不属于严格意义的眼表疾病。"
    if '视网膜' in qt and '视网膜内5层' in qt:
        return "视网膜内5层由视网膜中央动脉供血，外5层由脉络膜毛细血管供血（RPE为分界线）。"
    if '视网膜' in qt and '视盘' in qt and '正确的是' in qt:
        return "视盘（视乳头）是神经节细胞轴突汇合穿出巩膜处，无感光细胞→生理盲点。C/D正常≤0.3。"

    # ── OCULAR ONCOLOGY ──
    if '视网膜母细胞瘤' in qt or 'RB' in qt:
        return "视网膜母细胞瘤（RB）是儿童最常见的眼内恶性肿瘤，典型表现：白瞳症（猫眼反射）。治疗：化疗减容+局部治疗+眼球摘除。"
    if '脉络膜黑色素瘤' in qt:
        return "脉络膜黑色素瘤是成人最常见的眼内原发性恶性肿瘤。B超可见脉络膜挖空征。"

    # ── MISCELLANEOUS ──
    if '色盲' in qt and ('红绿' in qt or '分辨' in qt):
        return "红绿色盲最常见（X连锁隐性遗传），患者无法区分红色和绿色。"
    if '昼盲' in qt:
        return "昼盲常见病因：先天性视网膜锥体细胞功能不良（锥细胞主司明视觉）。夜盲见于视网膜色素变性（杆细胞病变）和维生素A缺乏。"
    if '夜盲' in qt:
        return "夜盲常见病因：视网膜色素变性（最常见）、维生素A缺乏症。"
    if '一过性视力丧失' in qt:
        return "一过性视力丧失（24h内恢复）常见原因：一过性脑缺血发作（TIA）、视网膜动脉痉挛、偏头痛、体位性低血压。视网膜中央动脉阻塞通常持续超过24h。"
    if '主诉' in qt or '病历' in qt and '首先' in qt:
        return "眼科门诊病历核心内容记录顺序：主诉（就诊原因+眼别+症状+持续时间）→现病史→既往史→检查→诊断。"
    if '现病史' in qt and '缺陷' in qt:
        return "现病史应记录：发病时间、诱因、主要症状及演变、伴随症状、诊治经过、既往相关病史。"
    if '左克' in qt:
        return "'左克'为左氧氟沙星的商品名，门诊病历应规范记录通用名而非商品名。"
    if '阿托品' in qt and '8岁' in qt or '阿托品凝胶' in qt and '儿童' in qt:
        return "阿托品凝胶用于儿童慢速散瞳验光，尤其伴有内斜视的儿童（睫状肌调节力强）。"
    if '开角型青光眼' in qt and '慢阻肺' in qt:
        return "有哮喘/慢阻肺/心动过缓病史的开角型青光眼患者，绝对禁用β受体阻滞剂（噻吗洛尔/卡替洛尔）。"
    if 'ICL' in qt or 'ICL晶体' in qt:
        return "ICL晶体植入术前发现泪道冲洗返流+脓性分泌物→先处理感染（抗生素3-5天），待泪道通畅无脓后再择期手术。慢性泪囊炎需先行DCR手术。"
    if '弱视' in qt and ('单眼' in qt or '屈光参差' in qt):
        return "屈光参差性弱视：双眼屈光度数差异>2.50D时，屈光度较高的一眼因成像模糊易发生弱视。屈光不正性弱视多双眼发病。"
    if '低血钙' in qt or '高血磷' in qt:
        return "低钙血症可致绕核性白内障（代谢性白内障），常见于甲状旁腺功能减退。"
    if '开放性眼外伤' in qt:
        return "开放性眼外伤包括：眼球破裂伤、眼球穿通伤、眼内异物。钝挫伤和板层裂伤属于闭合性眼外伤。"
    if '前房角' in qt and '从前到后' in qt:
        return "前房角从前到后：Schwalbe线→小梁网+Schlemm管→巩膜突→睫状体带→虹膜根部。"
    if '视网膜' in qt and '由内到外' in qt:
        return "视网膜组织学层次（由内到外）：内界膜→神经纤维层→神经节细胞层→内丛状层→内核层→外丛状层→外核层→外界膜→视杆视锥层→RPE。"
    if '格子样变性' in qt:
        return "格子样变性是最易发生视网膜裂孔的周边视网膜变性，是孔源性视网膜脱离最常见的前驱病变。"
    if '睑板腺囊肿' in qt or ('霰粒肿' in qt and '描述' in qt):
        return "霰粒肿（睑板腺囊肿）是睑板腺出口阻塞导致的慢性非感染性肉芽肿性炎症，无典型的红肿热痛。"
    if '丝状角膜炎' in qt:
        return "丝状角膜炎常见于干眼症、角膜暴露、长期包扎等，角膜表面可见卷曲的丝状物附着。"
    if '角膜' in qt and '可再生的层次' in qt:
        return "角膜五层中可再生的有：上皮细胞层（快速再生）和后弹力层（可缓慢再生）。前弹力层和内皮细胞层不能再生。"
    if '视神经炎' in qt and '乳头炎' in qt:
        return "视神经乳头炎是视神经炎的一种（炎症累及球内段，即视乳头），表现为视盘充血水肿+视力急剧下降。"
    if '缺血性视神经病变' in qt:
        return "前部缺血性视神经病变（AION）多见于老年人，无眼球转动痛，视野呈扇形或水平半盲缺损，视盘水肿常伴出血。"
    if '巩膜' in qt and '何处' in qt:
        return "巩膜最厚处为视神经周围，最薄处为眼外肌附着处。筛板是巩膜的薄弱区，青光眼时受压凹陷形成青光眼杯。"
    if '标准对数视力表' in qt and '缪天荣' in qt:
        return "我国缪天荣教授设计的《标准对数视力表》规定检查距离为5米，采用5分记录法。"
    if '相对性瞳孔传入障碍' in qt and '检查方法' in qt:
        return "RAPD检查：半暗环境，手电筒快速交替照射双眼。照射患眼时瞳孔先轻微收缩继而散大→提示传入通路受损。"
    if '流行性角膜结膜炎' in qt and '鉴别' in qt:
        return "流行性角结膜炎（腺病毒）的鉴别特征：耳前淋巴结压痛于眼开始受累侧较为明显。其他结膜炎可伴耳前淋巴结肿大但压痛不突出。"
    if '迟发型超敏反应' in qt and '无关' in qt:
        return "单纯疱疹病毒性角膜炎内皮型为免疫介导而非迟发型超敏反应。季节性/春季过敏性结膜炎和特应性角结膜炎为I型或IV型超敏反应。"
    if '关于眼压' in qt and '错误的是' in qt:
        return "眼压升高不一定是青光眼（如高眼压症），正常眼压也不能排除青光眼（如正常眼压性青光眼）。诊断需结合视盘和视野。"
    if '视网膜中央动脉阻塞' in qt and '临床表现' in qt:
        return "CRAO临床表现：突发无痛性单眼视力骤降→瞳孔散大→直接对光反射消失、间接存在→视网膜苍白水肿→黄斑樱桃红斑。"
    if '视网膜中央动脉阻塞' in qt and '治疗' in qt and '不合适' in qt:
        return "CRAO治疗：降眼压（前房穿刺/按摩/药物）+血管扩张剂+吸氧+溶栓。单纯全身抗凝/抗血小板作用有限。"
    if '年龄相关性黄斑变性' in qt and '正确' in qt:
        return "AMD可表现为进行性视力损害和视物变形。多为双眼发病但程度不对称。干性以保守为主，湿性需抗VEGF。玻璃膜疣可见于干性和湿性。"
    if '视网膜变性' in qt and '裂孔' in qt:
        return "格子样变性是最易发生视网膜裂孔的周边视网膜变性类型。"
    if '孔源性视网膜脱离' in qt and '错误的是' in qt:
        return "黄斑脱离超过1周者视力预后已较差，2周后手术视力恢复可能性大大降低。应尽早手术（黄斑在位时急诊手术）。"
    if '屈光介质' in qt and '不属于' in qt:
        return "眼球屈光介质：角膜、房水、晶状体、玻璃体。视网膜是感光组织，不属于屈光介质。"
    if '先天性白内障' in qt and '屈光状态' in qt:
        return "先天性白内障患儿行白内障摘除术后（未植入IOL时），屈光状态为高度远视（因失去了晶状体的屈光力约+19D）。"

    # ── Fallback: use correct answer text ──
    if correct_text and len(correct_text) > 5:
        return f"正确答案：{correct_text}。"

    return ""


# Apply
added = 0
for q in questions:
    if not q.get('explanation') or len(q['explanation'].strip()) < 5:
        expl = generate_explanation(q)
        if expl:
            q['explanation'] = expl
            added += 1

print(f"Added {added} explanations")

with_expl = sum(1 for q in questions if q.get('explanation') and len(q['explanation'].strip()) > 5)
print(f"Total with explanations: {with_expl}/{len(questions)}")

with open(os.path.join(BASE, 'questions.json'), 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)
print("Saved.")
