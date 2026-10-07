import os
import json
import re

articles_json_path = '/Users/gx/.gemini/antigravity/scratch/myth-magazine/data/articles.json'
with open(articles_json_path, 'r', encoding='utf-8') as f:
    raw_articles = json.load(f)

# Metadata refinement dictionary
title_overrides = {
    'No. 001': {
        'title': '共工怒触不周山',
        'subtitle': '天柱折，地维绝。那个不肯认输的人，把头撞向了不周山。',
        'originalMyth': '《淮南子·天文训》·《山海经·大荒西经》',
        'tags': ['反叛', '洪荒', '天崩地裂']
    },
    'No. 002': {
        'title': '精卫填海',
        'subtitle': '扑通。扑通。扑通。东海浩瀚，衔微木以填沧海。',
        'originalMyth': '《山海经·北山经》',
        'tags': ['执念', '反叛', '不屈']
    },
    'No. 003': {
        'title': '仓颉造字',
        'subtitle': '天雨粟，鬼夜哭。当第一道符号落入泥板，天地从此有了记忆。',
        'originalMyth': '《淮南子·本经训》·《说文解字序》',
        'tags': ['创世', '文明', '文字']
    },
    'No. 004': {
        'title': '伯牙子期',
        'subtitle': '摔碎瑶琴凤尾寒，子期不在对谁弹。知音之死，高山绝响。',
        'originalMyth': '《列子·汤问》·《吕氏春秋·本味》',
        'tags': ['人间', '知音', '琴道']
    },
    'No. 005': {
        'title': '八仙过海',
        'subtitle': '都别坐云了。坐云过海算什么本事？今日咱们八个，各显神通。',
        'originalMyth': '《东游记》· 民间八仙传说',
        'tags': ['道家', '东游', '沧海']
    },
    'No. 006': {
        'title': '刑天舞干戚',
        'subtitle': '以乳为目，以脐为口，操干戚以舞。头颅已断，战意不休。',
        'originalMyth': '《山海经·海外西经》· 陶渊明《读山海经》',
        'tags': ['反叛', '战神', '不屈']
    },
    'No. 007': {
        'title': '梁祝·化蝶',
        'subtitle': '牛车走得慢。这个静得不对，静得像车里坐的不是个大活人。',
        'originalMyth': '民间四大传说 · 梁山伯与祝英台',
        'tags': ['情执', '人间', '化蝶']
    },
    'No. 008': {
        'title': '后羿射日',
        'subtitle': '最后一个太阳。三十步开外，那是天底下最好的一张后背。',
        'originalMyth': '《淮南子·本经训》·《楚辞·天问》',
        'tags': ['英雄', '弑日', '背叛']
    },
    'No. 009': {
        'title': '哪吒剔骨',
        'subtitle': '割肉还母，剔骨还父。小畜生惹事？不过是神佛规矩太深。',
        'originalMyth': '《封神演义》·《三教搜神大全》',
        'tags': ['反叛', '骨肉', '少年']
    },
    'No. 010': {
        'title': '大禹涂山',
        'subtitle': '涂山的坛，一夜之间垒了起来。万国诸侯执玉帛，功成还是帝王心。',
        'originalMyth': '《史记·夏本纪》·《左传》',
        'tags': ['治水', '王权', '涂山']
    },
    'No. 011': {
        'title': '夸父逐日',
        'subtitle': '夸父死之后呢？那根手杖发芽的时候，他还在不在旁边看着？',
        'originalMyth': '《山海经·海外北经》',
        'tags': ['逐日', '桃林', '余生']
    },
    'No. 012': {
        'title': '女娲造人与补天',
        'subtitle': '神不大数得清年月——捏一个泥人，到他们学会下跪，原来这么短。',
        'originalMyth': '《风俗通义》·《淮南子·览冥训》',
        'tags': ['母神', '创世', '补天']
    },
    'No. 013': {
        'title': '苏妲己',
        'subtitle': '不是真相。真相我也没有。我只是写下：他们造出的九尾狐妖，究竟是谁。',
        'originalMyth': '《史记·殷本纪》·《列女传》',
        'tags': ['红颜', '商周', '史笔']
    },
    'No. 014': {
        'title': '孟姜女哭长城',
        'subtitle': '那一刹，她还以为是天塌了。城她哭了三日，原以为墙听不见。',
        'originalMyth': '《左传》杞梁妻 · 民间传说',
        'tags': ['情执', '人间', '哭城']
    },
    'No. 015': {
        'title': '孟婆汤',
        'subtitle': '奈何桥头，队排得望不到尾。舀汤舀了一宿——地府没有宿，就是一直舀。',
        'originalMyth': '冥界神话 · 幽冥十殿',
        'tags': ['幽冥', '忘川', '前尘']
    },
    'No. 016': {
        'title': '尾生抱柱',
        'subtitle': '约的是晌午。尾生天没亮就到了。水漫上来的时候，他握紧了桥柱。',
        'originalMyth': '《庄子·盗跖》·《战国策·燕策一》',
        'tags': ['信诺', '情执', '潮起']
    },
    'No. 017': {
        'title': '愚公移山',
        'subtitle': '指通豫南，达于汉阴。两座大山黑沉沉地立着，谁是头一个抄起锄头的人。',
        'originalMyth': '《列子·汤问》',
        'tags': ['愚妄', '子孙', '神庭']
    },
    'No. 018': {
        'title': '庄周梦蝶',
        'subtitle': '宋城东门代写书信的老庄。不知庄之梦为胡蝶与，蝴蝶之梦为庄周与？',
        'originalMyth': '《庄子·齐物论》',
        'tags': ['玄理', '梦蝶', '化生']
    },
    'No. 019': {
        'title': '混沌之死',
        'subtitle': '日凿一窍，七日而混沌死。哪儿都是我，我就是哪儿。',
        'originalMyth': '《庄子·应帝王》',
        'tags': ['开窍', '玄化', '无极']
    },
    'No. 020': {
        'title': '张僧繇画龙点睛',
        'subtitle': '四条龙，它是左数第二条。点上眼睛那一刻，金陵安乐寺风雷大作。',
        'originalMyth': '《历代名画记》',
        'tags': ['丹青', '通灵', '雷破']
    },
    'No. 021': {
        'title': '烂柯人',
        'subtitle': '手心一层茧，握紧了斧柄。山中方一日，世上已千年。',
        'originalMyth': '《述异记》王质烂柯',
        'tags': ['时光', '仙弈', '尘世']
    },
    'No. 022': {
        'title': '聊斋·画皮',
        'subtitle': '天快亮了，得赶紧把脸画上。露出底下的皮，翠绿微凉。',
        'originalMyth': '蒲松龄《聊斋志异·画皮》',
        'tags': ['皮相', '画心', '志怪']
    },
    'No. 023': {
        'title': '白水素女（田螺姑娘）',
        'subtitle': '我替一个不知道我在的人，烧了不知多少顿饭。水汽蒸腾里的人间烟火。',
        'originalMyth': '《搜神后记》白水素女',
        'tags': ['螺仙', '人间', '守候']
    },
    'No. 024': {
        'title': '神农尝百草',
        'subtitle': '那味草是苦的，苦里带一丝回甜。水晶肚子里，看得到青黄黑白。',
        'originalMyth': '《淮南子·修务训》·《史记》',
        'tags': ['药祖', '毒发', '苍生']
    },
    'No. 025': {
        'title': '牛郎织女·七夕',
        'subtitle': '七夕这一夜，天底下的人都在为我和他过节。我站在鹊桥上，听得见下界。',
        'originalMyth': '《诗经·小雅·大东》· 古诗十九首',
        'tags': ['星汉', '天河', '织锦']
    },
    'No. 026': {
        'title': '倩女幽魂（聂小倩）',
        'subtitle': '后来他们都说宁采臣救了我。兰若寺夜雨，红尘与白骨之间。',
        'originalMyth': '蒲松龄《聊斋志异·聂小倩》',
        'tags': ['兰若', '妖骨', '真伪']
    },
    'No. 027': {
        'title': '干将莫邪（上篇·熔金）',
        'subtitle': '铁化不开。一百天了。楚王要一把剑，天底下最好的剑。',
        'originalMyth': '《吴越春秋·阖闾内传》',
        'tags': ['铸剑', '血淬', '雌雄']
    },
    'No. 028': {
        'title': '干将莫邪（下篇·复仇）',
        'subtitle': '楚王把剑掂了掂，很满意。鼎中三首相咬，断颅不瞑目。',
        'originalMyth': '《搜神记·三王墓》',
        'tags': ['赤比', '白刃', '决绝']
    },
    'No. 029': {
        'title': '钟馗嫁妹',
        'subtitle': '除夕夜，杜家村。那扇柴门从里头闩死了。大鬼小鬼挑着红嫁妆。',
        'originalMyth': '钟馗捉鬼神话 · 民间年画传说',
        'tags': ['傩神', '夜行', '长兄']
    },
    'No. 030': {
        'title': '白蛇·雷峰塔',
        'subtitle': '被一个人爱得太满，本身就是一座雷峰塔。细雨断桥，金山水漫。',
        'originalMyth': '《白蛇传》·《警世通言·白娘子永镇雷峰塔》',
        'tags': ['情劫', '镇塔', '烟雨']
    },
    'No. 031': {
        'title': '黄粱一梦',
        'subtitle': '卢生睁开眼的时候，手还是弯着的。掌心里那点温，正在散去。',
        'originalMyth': '沈既济《枕中记》',
        'tags': ['青瓷', '枕梦', '虚空']
    }
}

refined_articles = []
for item in raw_articles:
    issue = item['issueNumber']
    override = title_overrides.get(issue, {})
    
    title = override.get('title', item['title'])
    subtitle = override.get('subtitle', item.get('pullQuote', ''))
    myth = override.get('originalMyth', '中华上古神话')
    tags = override.get('tags', [item['category']])
    
    item['cleanTitle'] = title
    item['subtitle'] = subtitle
    item['originalMyth'] = myth
    item['tags'] = tags
    
    # Calculate pages for the reader (roughly 450 words per magazine page)
    pages = []
    # Page 1: Magazine Cover Page (Metadata, Cover Art, Large Display Title)
    pages.append({
        'type': 'cover',
        'pageNumber': 1,
        'title': title,
        'subtitle': subtitle,
        'issueNumber': item['issueNumber'],
        'category': item['category'],
        'author': item['author'],
        'authorTitle': item['authorTitle'],
        'wordCount': item['wordCount'],
        'readMinutes': item['readMinutes'],
        'originalMyth': myth
    })
    
    # Page 2: Editorial Note / Inscription Page
    pages.append({
        'type': 'inscription',
        'pageNumber': 2,
        'title': title,
        'subtitle': subtitle,
        'quote': item['pullQuote'],
        'originalMyth': myth,
        'author': item['author']
    })
    
    # Subsequent pages: Content spread pages
    current_page_paras = []
    current_char_count = 0
    page_idx = 3
    
    for ch in item['chapters']:
        ch_title = ch['title']
        for p_idx, p in enumerate(ch['paragraphs']):
            p_len = len(p)
            if current_char_count + p_len > 480 and current_page_paras:
                pages.append({
                    'type': 'content',
                    'pageNumber': page_idx,
                    'paragraphs': current_page_paras,
                    'issueNumber': item['issueNumber'],
                    'title': title
                })
                page_idx += 1
                current_page_paras = []
                current_char_count = 0
                
            current_page_paras.append({
                'text': p,
                'isChapterHead': (p_idx == 0 and ch_title not in ['序章', '开篇']),
                'chapterTitle': ch_title if (p_idx == 0 and ch_title not in ['序章', '开篇']) else None
            })
            current_char_count += p_len
            
    if current_page_paras:
        pages.append({
            'type': 'content',
            'pageNumber': page_idx,
            'paragraphs': current_page_paras,
            'issueNumber': item['issueNumber'],
            'title': title
        })
        page_idx += 1
        
    # Final Page: Colophon / End Note / Next Issue Recommendation
    pages.append({
        'type': 'colophon',
        'pageNumber': page_idx,
        'title': title,
        'issueNumber': item['issueNumber'],
        'date': item['date'],
        'author': item['author'],
        'authorTitle': item['authorTitle'],
        'wordCount': item['wordCount']
    })
    
    item['pages'] = pages
    item['totalPages'] = len(pages)
    refined_articles.append(item)

print(f"Refined {len(refined_articles)} articles with pagination!")
out_refined_path = '/Users/gx/.gemini/antigravity/scratch/myth-magazine/data/refined_articles.json'
with open(out_refined_path, 'w', encoding='utf-8') as f:
    json.dump(refined_articles, f, ensure_ascii=False, indent=2)

print(f"Saved to {out_refined_path}")
