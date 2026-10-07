import os
import zipfile
import xml.etree.ElementTree as ET
import json
import re

desktop_path = '/Users/gx/Desktop/神话改编系列'
output_dir = '/Users/gx/.gemini/antigravity/scratch/myth-magazine/data'
os.makedirs(output_dir, exist_ok=True)

def read_docx(path):
    try:
        with zipfile.ZipFile(path) as z:
            xml_content = z.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            paragraphs = []
            for p in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                texts = [node.text for node in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if node.text]
                if texts:
                    t = ''.join(texts).strip()
                    if t:
                        paragraphs.append(t)
            return paragraphs
    except Exception as e:
        print(f"Error reading docx {path}: {e}")
        return []

def read_md(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        return lines
    except Exception as e:
        print(f"Error reading md {path}: {e}")
        return []

title_metadata = {
    '共工': {
        'title': '共工怒触不周山',
        'subtitle': '天柱折，地维绝。那个不肯认输的人，把头撞向了不周山。',
        'category': '卷二 · 反叛与神罚',
        'originalMyth': '《山海经·大荒西经》·《淮南子·天文训》',
        'classicQuote': '天柱折，地维绝。天倾西北，故日月星辰移焉；地不满东南，故水潦尘埃归焉。',
        'classicSource': '《淮南子·天文训》'
    },
    '精卫': {
        'title': '精卫填海',
        'subtitle': '扑通。扑通。扑通。东海浩瀚，衔微木以填沧海。',
        'category': '卷二 · 反叛与神罚',
        'originalMyth': '《山海经·北山经》',
        'classicQuote': '炎帝之少女，名曰女娃。女娃游于东海，溺而不返，故为精卫，常衔西山之木石，以堙于东海。',
        'classicSource': '《山海经·北山经》'
    },
    '仓颉': {
        'title': '仓颉造字',
        'subtitle': '天雨粟，鬼夜哭。当第一道符号落入泥板，天地从此有了记忆。',
        'category': '卷一 · 创世与洪荒',
        'originalMyth': '《淮南子·本经训》·《说文解字序》',
        'classicQuote': '颉首四目，通于神明，仰观奎星圜曲之势，俯察龟文鸟迹之象，博采众美，合而为字。',
        'classicSource': '《说文解字序》'
    },
    '伯牙': {
        'title': '伯牙子期',
        'subtitle': '摔碎瑶琴凤尾寒，子期不在对谁弹。知音之死，高山绝响。',
        'category': '卷三 · 人间与执念',
        'originalMyth': '《列子·汤问》·《吕氏春秋·本味》',
        'classicQuote': '伯牙善鼓琴，钟子期善听。伯牙鼓琴，志在高山，钟子期曰：“善哉，峨峨兮若泰山！”',
        'classicSource': '《列子·汤问》'
    },
    '八仙': {
        'title': '八仙过海',
        'subtitle': '都别坐云了。坐云过海算什么本事？今日咱们八个，各显神通。',
        'category': '卷四 · 志怪与幽冥',
        'originalMyth': '《东游记》· 民间八仙传说',
        'classicQuote': '八仙过海，各显神通。沧海横流，不借天风，但凭手中一物，踏破万顷狂澜。',
        'classicSource': '《东游记》'
    },
    '刑天': {
        'title': '刑天舞干戚',
        'subtitle': '以乳为目，以脐为口，操干戚以舞。头颅已断，战意不休。',
        'category': '卷二 · 反叛与神罚',
        'originalMyth': '《山海经·海外西经》· 陶渊明《读山海经》',
        'classicQuote': '刑天与帝至此争神，帝断其首，葬之常羊之山。乃以乳为目，以脐为口，操干戚以舞。',
        'classicSource': '《山海经·海外西经》'
    },
    '化蝶': {
        'title': '梁祝·化蝶',
        'subtitle': '牛车走得慢。这个静得不对，静得像车里坐的不是个大活人。',
        'category': '卷三 · 人间与执念',
        'originalMyth': '民间传说 · 梁山伯与祝英台',
        'classicQuote': '生不能同衾，死当同穴。冢忽自开，祝跃入其中，合之，化为双蝶，翩翩而舞。',
        'classicSource': '《宁波府志》'
    },
    '后羿': {
        'title': '后羿射日',
        'subtitle': '最后一个太阳。三十步开外，那是天底下最好的一张后背。',
        'category': '卷二 · 反叛与神罚',
        'originalMyth': '《淮南子·本经训》·《楚辞·天问》',
        'classicQuote': '逮至尧之时，十日并出，焦禾稼，杀草木，而民无所食。尧乃使羿上射十日，中其九日。',
        'classicSource': '《淮南子·本经训》'
    },
    '大禹': {
        'title': '大禹涂山',
        'subtitle': '涂山的坛，一夜之间垒了起来。万国诸侯执玉帛，功成还是帝王心。',
        'category': '卷一 · 创世与洪荒',
        'originalMyth': '《史记·夏本纪》·《左传》',
        'classicQuote': '禹会诸侯于涂山，执玉帛者万国。防风氏后至，禹杀而戮之。',
        'classicSource': '《左传·哀公七年》'
    },
    '夸父': {
        'title': '夸父逐日',
        'subtitle': '夸父死之后呢？那根手杖发芽的时候，他还在不在旁边看着？',
        'category': '卷二 · 反叛与神罚',
        'originalMyth': '《山海经·海外北经》',
        'classicQuote': '夸父与日逐走，入日；渴，欲得饮，饮于河、渭；河、渭不足，北饮大泽。未至，道渴而死。弃其杖，化为邓林。',
        'classicSource': '《山海经·海外北经》'
    },
    '女娲': {
        'title': '女娲造人与补天',
        'subtitle': '神不大数得清年月——捏一个泥人，到他们学会下跪，原来这么短。',
        'category': '卷一 · 创世与洪荒',
        'originalMyth': '《风俗通义》·《淮南子·览冥训》',
        'classicQuote': '女娲炼五色石以补苍天，断鳌足以立四极，杀黑龙以济冀州，积芦灰以止淫水。',
        'classicSource': '《淮南子·览冥训》'
    },
    '妲己': {
        'title': '苏妲己',
        'subtitle': '不是真相。真相我也没有。我只是写下：他们造出的九尾狐妖，究竟是谁。',
        'category': '卷三 · 人间与执念',
        'originalMyth': '《史记·殷本纪》·《列女传》',
        'classicQuote': '纣得妲己，爱幸百计，妲己之言听计从。天下谓之倾国，而史家独归罪于红颜。',
        'classicSource': '《列女传》'
    },
    '孟姜女': {
        'title': '孟姜女哭长城',
        'subtitle': '那一刹，她还以为是天塌了。城她哭了三日，原以为墙听不见。',
        'category': '卷三 · 人间与执念',
        'originalMyth': '《左传》杞梁妻 · 民间传说',
        'classicQuote': '杞梁死，其妻迎其柩于路，抚柩而哭，哀声动天，十里长城为之崩塌。',
        'classicSource': '《左传》杞梁妻传说'
    },
    '孟婆': {
        'title': '孟婆汤',
        'subtitle': '奈何桥头，队排得望不到尾。舀汤舀了一宿——地府没有宿，就是一直舀。',
        'category': '卷四 · 志怪与幽冥',
        'originalMyth': '幽冥神话 · 忘川之畔',
        'classicQuote': '过奈何桥，饮孟婆汤，前世爱恨、冤亲债孽，入腹化水，尽皆忘却，始得轮回报应。',
        'classicSource': '《幽冥录》'
    },
    '尾生': {
        'title': '尾生抱柱',
        'subtitle': '约的是晌午。尾生天没亮就到了。水漫上来的时候，他握紧了桥柱。',
        'category': '卷三 · 人间与执念',
        'originalMyth': '《庄子·盗跖》·《战国策·燕策一》',
        'classicQuote': '尾生与女子期于梁下，女子不来，水至不去，抱梁柱而死。信之至也，亦痴之至也。',
        'classicSource': '《庄子·盗跖》'
    },
    '愚公': {
        'title': '愚公移山',
        'subtitle': '指通豫南，达于汉阴。两座大山黑沉沉地立着，谁是头一个抄起锄头的人。',
        'category': '卷二 · 反叛与神罚',
        'originalMyth': '《列子·汤问》',
        'classicQuote': '虽我之死，有子存焉；子又生孙，孙又生子；子子孙孙无穷匮也，而山不加增，何苦而不平？',
        'classicSource': '《列子·汤问》'
    },
    '梦蝶': {
        'title': '庄周梦蝶',
        'subtitle': '宋城东门代写书信的老庄。不知庄之梦为胡蝶与，蝴蝶之梦为庄周与？',
        'category': '卷五 · 幻化与器物',
        'originalMyth': '《庄子·齐物论》',
        'classicQuote': '昔者庄周梦为胡蝶，栩栩然胡蝶也，自喻适志与！不知周也。俄然觉，则蘧蘧然周也。',
        'classicSource': '《庄子·齐物论》'
    },
    '混沌': {
        'title': '混沌之死',
        'subtitle': '日凿一窍，七日而混沌死。哪儿都是我，我就是哪儿。',
        'category': '卷一 · 创世与洪荒',
        'originalMyth': '《庄子·应帝王》',
        'classicQuote': '南海之帝为儵，北海之帝为忽，中央之帝为浑沌。日凿一窍，七日而浑沌死。',
        'classicSource': '《庄子·应帝王》'
    },
    '点睛': {
        'title': '画龙点睛',
        'subtitle': '四条龙，它是左数第二条。点上眼睛那一刻，金陵安乐寺风雷大作。',
        'category': '卷五 · 幻化与器物',
        'originalMyth': '《历代名画记》',
        'classicQuote': '张僧繇于金陵安乐寺画四白龙，不点眼睛。点其一，雷电破壁，一龙乘云上天。',
        'classicSource': '《历代名画记》'
    },
    '烂柯': {
        'title': '烂柯人',
        'subtitle': '手心一层茧，握紧了斧柄。山中方一日，世上已千年。',
        'category': '卷五 · 幻化与器物',
        'originalMyth': '《述异记》王质烂柯',
        'classicQuote': '王质入山伐木，见二童子弈棋。童子与质一物，如枣核，食之不饥。局罢，斧柯尽烂。',
        'classicSource': '《述异记》'
    },
    '画皮': {
        'title': '聊斋·画皮',
        'subtitle': '天快亮了，得赶紧把脸画上。露出底下的皮，翠绿微凉。',
        'category': '卷四 · 志怪与幽冥',
        'originalMyth': '蒲松龄《聊斋志异·画皮》',
        'classicQuote': '见一狞鬼，面翠色，齿巉巉如锯。铺人皮于榻上，执彩笔而绘之；已而掷笔，举皮如振衣状。',
        'classicSource': '《聊斋志异》'
    },
    '白水': {
        'title': '白水素女（田螺姑娘）',
        'subtitle': '我替一个不知道我在的人，烧了不知多少顿饭。水汽蒸腾里的人间烟火。',
        'category': '卷五 · 幻化与器物',
        'originalMyth': '《搜神后记》白水素女',
        'classicQuote': '谢端无妻，于田中得一大螺，贮于瓮中。自是日后，日日入炊，甘香满室，端潜归窥之。',
        'classicSource': '《搜神后记》'
    },
    '神农': {
        'title': '神农尝百草',
        'subtitle': '那味草是苦的，苦里带一丝回甜。水晶肚子里，看得到青黄黑白。',
        'category': '卷一 · 创世与洪荒',
        'originalMyth': '《淮南子·修务训》·《史记》',
        'classicQuote': '神农尝百草之滋味，知水泉之甘苦，令民知所避就。当此之时，一日而遇七十毒。',
        'classicSource': '《淮南子·修务训》'
    },
    '织女': {
        'title': '牛郎织女·七夕',
        'subtitle': '七夕这一夜，天底下的人都在为我和他过节。我站在鹊桥上，听得见下界。',
        'category': '卷三 · 人间与执念',
        'originalMyth': '《诗经·小雅·大东》· 古诗十九首',
        'classicQuote': '迢迢牵牛星，皎皎河汉女。纤纤擢素手，札札弄机杼。终日不成章，泣涕零如雨。',
        'classicSource': '《古诗十九首》'
    },
    '聂小倩': {
        'title': '倩女幽魂（聂小倩）',
        'subtitle': '后来他们都说宁采臣救了我。兰若寺夜雨，红尘与白骨之间。',
        'category': '卷四 · 志怪与幽冥',
        'originalMyth': '蒲松龄《聊斋志异·聂小倩》',
        'classicQuote': '小倩，姓聂氏，十八夭卒。兰若夜雨，白骨红粉。宁生仗剑独立，不为妖惑，始脱幽渊。',
        'classicSource': '《聊斋志异》'
    },
    '莫邪新编_v1': {
        'title': '干将莫邪（上篇·熔金）',
        'subtitle': '铁化不开。一百天了。楚王要一把剑，天底下最好的剑。',
        'category': '卷五 · 幻化与器物',
        'originalMyth': '《吴越春秋·阖闾内传》',
        'classicQuote': '干将作剑，采五山之铁精，六合之金英。莫邪断发剪爪，投于炉中，金铁乃铄，遂以成剑。',
        'classicSource': '《吴越春秋》'
    },
    '莫邪新编_v2': {
        'title': '干将莫邪（下篇·复仇）',
        'subtitle': '楚王把剑掂了掂，很满意。鼎中三首相咬，断颅不瞑目。',
        'category': '卷五 · 幻化与器物',
        'originalMyth': '《搜神记·三王墓》',
        'classicQuote': '客持剑砍王头，头堕镬中；客亦自脰。三首俱烂，不可识，分葬之，故通名“三王墓”。',
        'classicSource': '《搜神记》'
    },
    '钟馗': {
        'title': '钟馗嫁妹',
        'subtitle': '除夕夜，杜家村。那扇柴门从里头闩死了。大鬼小鬼挑着红嫁妆。',
        'category': '卷四 · 志怪与幽冥',
        'originalMyth': '钟馗神话 · 民间年画传说',
        'classicQuote': '终南进士钟馗，殁而为神。感生前好友杜平之义，除夕夜率阴兵群鬼，鼓乐喧天，送妹出阁。',
        'classicSource': '《钟馗传奇》'
    },
    '雷峰塔': {
        'title': '白蛇·雷峰塔',
        'subtitle': '被一个人爱得太满，本身就是一座雷峰塔。细雨断桥，金山水漫。',
        'category': '卷三 · 人间与执念',
        'originalMyth': '《白蛇传》·《警世通言》',
        'classicQuote': '西湖水干，江潮不起，雷峰塔倒，白发才生。痴儿怨女，满纸荒唐，不过是一场金山水漫。',
        'classicSource': '《白蛇传》'
    },
    '黄粱': {
        'title': '黄粱一梦',
        'subtitle': '卢生睁开眼的时候，手还是弯着的。掌心里那点温，正在散去。',
        'category': '卷五 · 幻化与器物',
        'originalMyth': '沈既济《枕中记》',
        'classicQuote': '卢生欠伸而寤，见其身方偃于邸舍中，吕翁坐其傍，主人蒸黄粱尚未熟，触类如故。',
        'classicSource': '《枕中记》'
    }
}

files = sorted(os.listdir(desktop_path))
articles = []
issue_no = 1

for f in files:
    # 彻底跳过哪吒！
    if '哪吒' in f:
        print(f"Skipping excluded story: {f}")
        continue
    if f.startswith('.') or f.endswith(('.png', '.xlsx', '.log')):
        continue
    if f in ['文风范例.md', '项目交接_handoff.md']:
        continue
    if not (f.endswith('.docx') or f.endswith('.md')):
        continue

    full_path = os.path.join(desktop_path, f)
    if f.endswith('.docx'):
        paras = read_docx(full_path)
    else:
        paras = read_md(full_path)

    if not paras:
        continue

    # Match metadata
    matched_meta = None
    for k, meta in title_metadata.items():
        if k in f:
            matched_meta = meta
            break
            
    if not matched_meta:
        clean_name = f.replace('.docx', '').replace('.md', '').replace('_v1', '').replace('_v2', '')
        matched_meta = {
            'title': clean_name,
            'subtitle': '大白话打底，短句断得狠；叙述者冷、克制、却有体温。',
            'category': '神话新编',
            'originalMyth': '中华上古传说',
            'classicQuote': '神话新编 · 经典重述',
            'classicSource': '中华神话'
        }

    # Filter out redundant title lines and empty paragraphs
    clean_body_paras = []
    for p in paras:
        p_s = p.strip()
        if not p_s or p_s.startswith(('写作阐述', '---', '===', '# ')):
            continue
        # Skip lines that are just titles or fragments
        if p_s in [matched_meta['title'], '不周', '扑通', '开篇', '序章'] or (len(p_s) < 20 and ('新编' in p_s or p_s.startswith(('《', '第', '一、')))):
            continue
        clean_body_paras.append(p_s)

    body_paras = clean_body_paras
    total_words = sum(len(p) for p in body_paras)
    if total_words < 100:
        continue

    # Build Spreads (each Spread has a Left Page and a Right Page, like a real magazine!)
    spreads = []
    
    # SPREAD 1: Cover / Opening Spread (as in the screenshot!)
    # Left page: Masthead line, golden category badge, giant display title, subtitle, opening paragraphs
    # Right page: Header line with title, Golden Roman numeral, Classic Quote Callout Card, following paragraphs
    left_p_count = 2 if len(body_paras) >= 2 else 1
    left_opening_paras = body_paras[:left_p_count]
    right_opening_paras = body_paras[left_p_count:left_p_count + 3]
    curr_idx = left_p_count + len(right_opening_paras)

    spread1 = {
        'spreadNumber': 1,
        'type': 'opening',
        'leftPage': {
            'pageNumber': 2,
            'headerTag': matched_meta['category'],
            'badge': '特稿专栏',
            'title': matched_meta['title'],
            'subtitle': matched_meta['subtitle'],
            'paragraphs': left_opening_paras,
            'footerCategory': matched_meta['category'].split('·')[-1].strip(),
            'footerPage': '02'
        },
        'rightPage': {
            'pageNumber': 3,
            'headerTitle': matched_meta['title'],
            'calloutCard': {
                'title': matched_meta['classicSource'],
                'subtitle': '原典考据 · 存照',
                'goldNumber': '1',
                'goldLabel': '典，千古流传',
                'quote': matched_meta['classicQuote'],
                'buttonText': '铭记此句 · 留在心间'
            },
            'paragraphs': right_opening_paras,
            'footerCategory': matched_meta['category'].split('·')[-1].strip(),
            'footerPage': '03'
        }
    }
    spreads.append(spread1)

    # Subsequent Spreads
    page_counter = 4
    spread_counter = 2
    
    while curr_idx < len(body_paras):
        # Pack left page (approx 3-4 paragraphs or 300 words)
        left_ps = []
        char_c = 0
        while curr_idx < len(body_paras) and (char_c < 280 or len(left_ps) < 2) and len(left_ps) < 4:
            left_ps.append(body_paras[curr_idx])
            char_c += len(body_paras[curr_idx])
            curr_idx += 1

        # Pack right page
        right_ps = []
        char_c = 0
        while curr_idx < len(body_paras) and (char_c < 280 or len(right_ps) < 2) and len(right_ps) < 4:
            right_ps.append(body_paras[curr_idx])
            char_c += len(body_paras[curr_idx])
            curr_idx += 1

        # Optional decorative callout on subsequent spreads
        right_callout = None
        if spread_counter == 2 and len(matched_meta['subtitle']) > 15:
            right_callout = {
                'title': '神话回响',
                'subtitle': '文风辑要',
                'goldNumber': f'{spread_counter}',
                'goldLabel': '语，字字砸地',
                'quote': matched_meta['subtitle'],
                'buttonText': '细细品读'
            }

        spread = {
            'spreadNumber': spread_counter,
            'type': 'content',
            'leftPage': {
                'pageNumber': page_counter,
                'headerTag': matched_meta['category'],
                'paragraphs': left_ps,
                'footerCategory': matched_meta['category'].split('·')[-1].strip(),
                'footerPage': f'{page_counter:02d}'
            },
            'rightPage': {
                'pageNumber': page_counter + 1,
                'headerTitle': matched_meta['title'],
                'calloutCard': right_callout,
                'paragraphs': right_ps,
                'footerCategory': matched_meta['category'].split('·')[-1].strip(),
                'footerPage': f'{(page_counter + 1):02d}'
            }
        }
        spreads.append(spread)
        page_counter += 2
        spread_counter += 1

    # End Colophon Spread
    colophon_spread = {
        'spreadNumber': spread_counter,
        'type': 'colophon',
        'leftPage': {
            'pageNumber': page_counter,
            'headerTag': matched_meta['category'],
            'isColophon': True,
            'title': '《' + matched_meta['title'] + '》· 卷终',
            'paragraphs': [
                '“大白话打底，短句断得狠；叙述者冷、克制、却有体温、敢下判断；情绪全化进身体和器物，绝不抒情空转。”',
                f'全篇计 {total_words:,} 字。叙述戛然而止，余音不绝。'
            ],
            'footerCategory': matched_meta['category'].split('·')[-1].strip(),
            'footerPage': f'{page_counter:02d}'
        },
        'rightPage': {
            'pageNumber': page_counter + 1,
            'headerTitle': '中华神话重构系列 · 刊记',
            'isColophonNext': True,
            'nextIssueNumber': f'No. {(issue_no + 1):03d}',
            'footerCategory': matched_meta['category'].split('·')[-1].strip(),
            'footerPage': f'{(page_counter + 1):02d}'
        }
    }
    spreads.append(colophon_spread)

    article_obj = {
        'id': f'issue-{issue_no:03d}',
        'issueNumber': f'No. {issue_no:03d}',
        'cleanTitle': matched_meta['title'],
        'subtitle': matched_meta['subtitle'],
        'category': matched_meta['category'],
        'originalMyth': matched_meta['originalMyth'],
        'classicQuote': matched_meta['classicQuote'],
        'author': 'GX',
        'authorTitle': '神话重构作家 · 独立小说家',
        'wordCount': total_words,
        'readMinutes': max(3, round(total_words / 350)),
        'spreads': spreads,
        'totalSpreads': len(spreads),
        'totalPages': page_counter + 1,
        'fullParagraphs': body_paras
    }
    articles.append(article_obj)
    issue_no += 1

print(f"Processed {len(articles)} myth stories without Nezha!")
with open(os.path.join(output_dir, 'refined_articles.json'), 'w', encoding='utf-8') as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

# Export to js/data.js
js_path = '/Users/gx/.gemini/antigravity/scratch/myth-magazine/js/data.js'
with open(js_path, 'w', encoding='utf-8') as f:
    f.write('window.MYTH_ARTICLES = ' + json.dumps(articles, ensure_ascii=False) + ';\n')

print(f"Exported to {js_path} successfully!")
