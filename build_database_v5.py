import os
import json
import re

# Load raw articles
with open('/Users/gx/.gemini/antigravity/scratch/myth-magazine/data/articles.json', 'r', encoding='utf-8') as f:
    raw_all = json.load(f)

# Filter out Nezha completely
raw = [x for x in raw_all if '哪吒' not in x['title'] and not x['title'].startswith('一、')]

print(f"Total raw myth articles (Nezha excluded): {len(raw)}")

# 100% Precise metadata and artwork mapping for all 30 articles
story_configs = [
    {
        'title': '共工怒触不周山',
        'subtitle': '天柱折，地维绝。那个不肯认输的人，把头撞向了不周山。',
        'category': '卷二 · 反叛与神罚',
        'originalMyth': '《山海经·大荒西经》·《淮南子·天文训》',
        'classicQuote': '天柱折，地维绝。天倾西北，故日月星辰移焉；地不满东南，故水潦尘埃归焉。',
        'coverImg': 'assets/illustrations/illust_01.png',
        'inlineImg': 'assets/illustrations/illust_02.png',
        'imgCaption': '共工撞向不周山，山崩石裂，天倾西北',
        'extraImgs': {}
    },
    {
        'title': '精卫填海',
        'subtitle': '扑通。扑通。扑通。东海浩瀚，衔微木以填沧海。',
        'category': '卷二 · 反叛与神罚',
        'originalMyth': '《山海经·北山经》',
        'classicQuote': '炎帝之少女，名曰女娃。女娃游于东海，溺而不返，故为精卫，常衔西山之木石，以堙于东海。',
        'coverImg': 'assets/illustrations/illust_05.png',
        'inlineImg': 'assets/illustrations/illust_03.png',
        'imgCaption': '白鸟衔石投海，飞掠沧海浊浪',
        'extraImgs': {
            2: ('assets/illustrations/illust_04.png', '龙宫海底专班案前，水族计簿算盘核算')
        }
    },
    {
        'title': '仓颉造字',
        'subtitle': '天雨粟，鬼夜哭。当第一道符号落入泥板，天地从此有了记忆。',
        'category': '卷一 · 创世与洪荒',
        'originalMyth': '《淮南子·本经训》·《说文解字序》',
        'classicQuote': '颉首四目，通于神明，仰观奎星圜曲之势，俯察龟文鸟迹之象，博采众美，合而为字。',
        'coverImg': 'assets/illustrations/illust_09.png',
        'inlineImg': 'assets/illustrations/illust_10.png',
        'imgCaption': '仓颉仰观奎星鸟迹，刻符于石板',
        'extraImgs': {
            3: ('assets/illustrations/illust_24.png', '兽骨甲片微芒初现，青光灼灼如神迹'),
            5: ('assets/illustrations/illust_26.png', '灵鸟啄石为印，神迹留爪为书')
        }
    },
    {
        'title': '伯牙子期',
        'subtitle': '摔碎瑶琴凤尾寒，子期不在对谁弹。知音之死，高山绝响。',
        'category': '卷三 · 人间与执念',
        'originalMyth': '《列子·汤问》·《吕氏春秋·本味》',
        'classicQuote': '伯牙善鼓琴，钟子期善听。伯牙鼓琴，志在高山，钟子期曰：“善哉，峨峨兮若泰山！”',
        'coverImg': 'assets/illustrations/illust_07.png',
        'inlineImg': 'assets/illustrations/illust_38.png',
        'imgCaption': '汉阳江口抚琴相携，高山流水遇知音',
        'extraImgs': {}
    },
    {
        'title': '八仙过海',
        'subtitle': '都别坐云了。坐云过海算什么本事？今日咱们八个，各显神通。',
        'category': '卷四 · 志怪与幽冥',
        'originalMyth': '《东游记》· 民间八仙传说',
        'classicQuote': '八仙过海，各显神通。沧海横流，不借天风，但凭手中一物，踏破万顷狂澜。',
        'coverImg': 'assets/illustrations/illust_35.png',
        'inlineImg': 'assets/illustrations/illust_28.png',
        'imgCaption': '海滨客肆道友会聚，煮茶论道意在东海',
        'extraImgs': {
            3: ('assets/illustrations/illust_37.png', '白衣仙者席地而坐，汉钟离点悟凡世'),
            4: ('assets/illustrations/illust_36.png', '铁拐李执杖云端，俯视下界沧海桑田')
        }
    },
    {
        'title': '刑天舞干戚',
        'subtitle': '以乳为目，以脐为口，操干戚以舞。头颅已断，战意不休。',
        'category': '卷二 · 反叛与神罚',
        'originalMyth': '《山海经·海外西经》· 陶渊明《读山海经》',
        'classicQuote': '刑天与帝至此争神，帝断其首，葬之常羊之山。乃以乳为目，以脐为口，操干戚以舞。',
        'coverImg': 'assets/illustrations/illust_12.png',
        'inlineImg': 'assets/illustrations/illust_12.png',
        'imgCaption': '断首战神以乳为目，操干戚而舞不休',
        'extraImgs': {}
    },
    {
        'title': '梁祝·化蝶',
        'subtitle': '牛车走得慢。这个静得不对，静得像车里坐的不是个大活人。',
        'category': '卷三 · 人间与执念',
        'originalMyth': '民间四大传说 · 梁山伯与祝英台',
        'classicQuote': '生不能同衾，死当同穴。冢忽自开，祝跃入其中，合之，化为双蝶，翩翩而舞。',
        'coverImg': 'assets/illustrations/illust_08.png',
        'inlineImg': 'assets/illustrations/illust_11.png',
        'imgCaption': '宫墙暮色冷蝶双飞，宿命执念终化彩翼',
        'extraImgs': {}
    },
    {
        'title': '后羿射日',
        'subtitle': '最后一个太阳。三十步开外，那是天底下最好的一张后背。',
        'category': '卷二 · 反叛与神罚',
        'originalMyth': '《淮南子·本经训》·《楚辞·天问》',
        'classicQuote': '逮至尧之时，十日并出，焦禾稼，杀草木，而民无所食。尧乃使羿上射十日，中其九日。',
        'coverImg': 'assets/illustrations/illust_13.png',
        'inlineImg': 'assets/illustrations/illust_14.png',
        'imgCaption': '彤弓如满月，金乌尽坠落',
        'extraImgs': {
            3: ('assets/illustrations/illust_15.png', '残阳暮色庭院孤立，射日英雄余生寂寞')
        }
    },
    {
        'title': '大禹涂山',
        'subtitle': '涂山的坛，一夜之间垒了起来。万国诸侯执玉帛，功成还是帝王心。',
        'category': '卷一 · 创世与洪荒',
        'originalMyth': '《史记·夏本纪》·《左传》',
        'classicQuote': '禹会诸侯于涂山，执玉帛者万国。防风氏后至，禹杀而戮之。',
        'coverImg': 'assets/illustrations/illust_16.png',
        'inlineImg': 'assets/illustrations/illust_16.png',
        'imgCaption': '涂山之会三丈高坛，黑鸦群聚诸侯执玉帛',
        'extraImgs': {}
    },
    {
        'title': '夸父逐日',
        'subtitle': '夸父死之后呢？那根手杖发芽的时候，他还在不在旁边看着？',
        'category': '卷二 · 反叛与神罚',
        'originalMyth': '《山海经·海外北经》',
        'classicQuote': '夸父与日逐走，入日；渴，欲得饮，饮于河、渭；未至，道渴而死。弃其杖，化为邓林。',
        'coverImg': 'assets/illustrations/illust_31.png',
        'inlineImg': 'assets/illustrations/illust_32.png',
        'imgCaption': '黄土大道车辙深印，逐日狂奔向无尽金阳',
        'extraImgs': {}
    },
    {
        'title': '女娲造人与补天',
        'subtitle': '神不大数得清年月——捏一个泥人，到他们学会下跪，原来这么短。',
        'category': '卷一 · 创世与洪荒',
        'originalMyth': '《风俗通义》·《淮南子·览冥训》',
        'classicQuote': '女娲炼五色石以补苍天，断鳌足以立四极，杀黑龙以济冀州，积芦灰以止淫水。',
        'coverImg': 'assets/illustrations/illust_17.png',
        'inlineImg': 'assets/illustrations/illust_18.png',
        'imgCaption': '苍茫荒野甩绳成泥，母神初造世间凡躯',
        'extraImgs': {
            3: ('assets/illustrations/illust_19.png', '熔岩天火苍生浩劫，神手俯伸救赎众生'),
            4: ('assets/illustrations/illust_20.png', '神庙香火供奉母神，天下万民初学叩拜')
        }
    },
    {
        'title': '苏妲己',
        'subtitle': '不是真相。真相我也没有。我只是写下：他们造出的九尾狐妖，究竟是谁。',
        'category': '卷三 · 人间与执念',
        'originalMyth': '《史记·殷本纪》·《列女传》',
        'classicQuote': '纣得妲己，爱幸百计，妲己之言听计从。天下谓之倾国，而史家独归罪于红颜。',
        'coverImg': 'assets/illustrations/art_daji.jpg',
        'inlineImg': 'assets/illustrations/art_daji.jpg',
        'imgCaption': '商宫青铜鼎前九尾暗影，深宫冷月锁尽千秋悲凉',
        'extraImgs': {}
    },
    {
        'title': '孟姜女哭长城',
        'subtitle': '那一刹，她还以为是天塌了。城她哭了三日，原以为墙听不见。',
        'category': '卷三 · 人间与执念',
        'originalMyth': '《左传》杞梁妻 · 民间传说',
        'classicQuote': '杞梁死，其妻迎其柩于路，抚柩而哭，哀声动天，十里长城为之崩塌。',
        'coverImg': 'assets/illustrations/art_mengjiang.jpg',
        'inlineImg': 'assets/illustrations/art_mengjiang.jpg',
        'imgCaption': '暴雪肆虐塞北荒脊，素衣孤女哭断坚石长城',
        'extraImgs': {}
    },
    {
        'title': '孟婆汤',
        'subtitle': '奈何桥头，队排得望不到尾。舀汤舀了一宿——地府没有宿，就是一直舀。',
        'category': '卷四 · 志怪与幽冥',
        'originalMyth': '幽冥神话 · 忘川之畔',
        'classicQuote': '过奈何桥，饮孟婆汤，前世爱恨、冤亲债孽，入腹化水，尽皆忘却，始得轮回报应。',
        'coverImg': 'assets/illustrations/art_mengpo.jpg',
        'inlineImg': 'assets/illustrations/art_mengpo.jpg',
        'imgCaption': '忘川河畔孟婆大鼎，金汤入腹前尘俱散',
        'extraImgs': {}
    },
    {
        'title': '尾生抱柱',
        'subtitle': '约的是晌午。尾生天没亮就到了。水漫上来的时候，他握紧了桥柱。',
        'category': '卷三 · 人间与执念',
        'originalMyth': '《庄子·盗跖》·《战国策·燕策一》',
        'classicQuote': '尾生与女子期于梁下，女子不来，水至不去，抱梁柱而死。信之至也，亦痴之至也。',
        'coverImg': 'assets/illustrations/art_weisheng.jpg',
        'inlineImg': 'assets/illustrations/art_weisheng.jpg',
        'imgCaption': '狂潮浊浪漫过桥底，死守死契双臂不松',
        'extraImgs': {}
    },
    {
        'title': '愚公移山',
        'subtitle': '指通豫南，达于汉阴。两座大山黑沉沉地立着，谁是头一个抄起锄头的人。',
        'category': '卷二 · 反叛与神罚',
        'originalMyth': '《列子·汤问》',
        'classicQuote': '虽我之死，有子存焉；子又生孙，孙又生子；子子孙孙无穷匮也，而山不加增，何苦而不平？',
        'coverImg': 'assets/illustrations/illust_29.png',
        'inlineImg': 'assets/illustrations/illust_30.png',
        'imgCaption': '太行王屋万仞壁立，老朽与儿孙一箕一锄',
        'extraImgs': {}
    },
    {
        'title': '庄周梦蝶',
        'subtitle': '宋城东门代写书信的老庄。不知庄之梦为胡蝶与，蝴蝶之梦为庄周与？',
        'category': '卷五 · 幻化与器物',
        'originalMyth': '《庄子·齐物论》',
        'classicQuote': '昔者庄周梦为胡蝶，栩栩然胡蝶也，自喻适志与！不知周也。俄然觉，则蘧蘧然周也。',
        'coverImg': 'assets/illustrations/illust_06.png',
        'inlineImg': 'assets/illustrations/illust_06.png',
        'imgCaption': '宋城荒草丛中高眠，白蝶翩翩落于鼻尖',
        'extraImgs': {}
    },
    {
        'title': '混沌之死',
        'subtitle': '日凿一窍，七日而混沌死。哪儿都是我，我就是哪儿。',
        'category': '卷一 · 创世与洪荒',
        'originalMyth': '《庄子·应帝王》',
        'classicQuote': '南海之帝为儵，北海之帝为忽，中央之帝为浑沌。日凿一窍，七日而浑沌死。',
        'coverImg': 'assets/illustrations/art_hundun.jpg',
        'inlineImg': 'assets/illustrations/art_hundun.jpg',
        'imgCaption': '混沦元初七窍开凿，金色神光破开虚无',
        'extraImgs': {}
    },
    {
        'title': '画龙点睛',
        'subtitle': '四条龙，它是左数第二条。点上眼睛那一刻，金陵安乐寺风雷大作。',
        'category': '卷五 · 幻化与器物',
        'originalMyth': '《历代名画记》',
        'classicQuote': '张僧繇于金陵安乐寺画四白龙，不点眼睛。点其一，雷电破壁，一龙乘云上天。',
        'coverImg': 'assets/illustrations/art_dianjing.jpg',
        'inlineImg': 'assets/illustrations/art_dianjing.jpg',
        'imgCaption': '神僧落笔点亮龙睛，白龙破壁乘雷腾天',
        'extraImgs': {}
    },
    {
        'title': '烂柯人',
        'subtitle': '手心一层茧，握紧了斧柄。山中方一日，世上已千年。',
        'category': '卷五 · 幻化与器物',
        'originalMyth': '《述异记》',
        'classicQuote': '信安郡石室山，晋时王质伐木至，见童子数人棋而歌，质因听之。童子与一物如枣核，食之不饥。',
        'coverImg': 'assets/illustrations/art_lanke.jpg',
        'inlineImg': 'assets/illustrations/art_lanke.jpg',
        'imgCaption': '石室岩洞仙童落子，木柯已朽尘世百年',
        'extraImgs': {}
    },
    {
        'title': '聊斋·画皮',
        'subtitle': '皮相之下，究竟是恶鬼还是凡胎？裂腹掏心，犹言世人看不穿。',
        'category': '卷四 · 志怪与幽冥',
        'originalMyth': '《聊斋志异·画皮》',
        'classicQuote': '世人愚惑，明是妖魔，而以为美。迷而不悟，乃至碎裂胸膛，何其哀哉！',
        'coverImg': 'assets/illustrations/art_huapi.jpg',
        'inlineImg': 'assets/illustrations/art_huapi.jpg',
        'imgCaption': '书斋残烛青面恶鬼，素手微执巧描人皮',
        'extraImgs': {}
    },
    {
        'title': '白水素女（田螺姑娘）',
        'subtitle': '谢端每日归家，灶上有热饭。水瓮里的田螺壳，藏着不可说的来处。',
        'category': '卷五 · 幻化与器物',
        'originalMyth': '《搜神后记》',
        'classicQuote': '侯官谢端，少孤，无妇。得大螺，养于瓮中。每日归，见有饭饮汤火，乃白水素女所为也。',
        'coverImg': 'assets/illustrations/art_baishui.jpg',
        'inlineImg': 'assets/illustrations/art_baishui.jpg',
        'imgCaption': '水瓮素螺微光烁烁，灶台炊烟暖意人间',
        'extraImgs': {}
    },
    {
        'title': '神农尝百草',
        'subtitle': '日遇七十二毒，得荼而解之。以一身血肉，试尽人间草木枯荣。',
        'category': '卷一 · 创世与洪荒',
        'originalMyth': '《淮南子·修务训》',
        'classicQuote': '神农尝百草之滋味，水泉之甘苦，令民知所避就。当此之时，一日而遇七十毒。',
        'coverImg': 'assets/illustrations/art_shennong.jpg',
        'inlineImg': 'assets/illustrations/art_shennong.jpg',
        'imgCaption': '绝壁悬崖细辨毒草，以身试毒为济万民',
        'extraImgs': {}
    },
    {
        'title': '牛郎织女·七夕',
        'subtitle': '天河两岸，机杼声歇。每年七月七，不过是一次痛彻心扉的对视。',
        'category': '卷三 · 人间与执念',
        'originalMyth': '《古诗十九首》· 汉魏乐府',
        'classicQuote': '迢迢牵牛星，皎皎河汉女。纤纤擢素手，札札弄机杼。盈盈一水间，脉脉不得语。',
        'coverImg': 'assets/illustrations/illust_39.png',
        'inlineImg': 'assets/illustrations/illust_39.png',
        'imgCaption': '芦苇溪水惊回顾盼，羽衣已拾仙凡相隔',
        'extraImgs': {}
    },
    {
        'title': '倩女幽魂（聂小倩）',
        'subtitle': '兰若寺里夜雨急。金银可弃，美色可拒，宁生书生自有浩然气。',
        'category': '卷四 · 志怪与幽冥',
        'originalMyth': '《聊斋志异·聂小倩》',
        'classicQuote': '宁生笑曰：“我生平无妄想，此物非我所有，何敢受之？”小倩叹曰：“君真丈夫也！”',
        'coverImg': 'assets/illustrations/art_xiaoqian.jpg',
        'inlineImg': 'assets/illustrations/art_xiaoqian.jpg',
        'imgCaption': '兰若荒刹古灯幽照，幽魂素影窗外伫立',
        'extraImgs': {}
    },
    {
        'title': '干将莫邪（上篇·熔金）',
        'subtitle': '采五山之铁精，六合之金英。炉火不发，夫妻断发投身以殉剑。',
        'category': '卷五 · 幻化与器物',
        'originalMyth': '《吴越春秋》·《搜神记》',
        'classicQuote': '干将作剑，采五山之铁精，六合之金英。候天伺地，金铁不销，铁汁不下。',
        'coverImg': 'assets/illustrations/art_ganjiang.jpg',
        'inlineImg': 'assets/illustrations/art_ganjiang.jpg',
        'imgCaption': '炉膛烈焰金铁不销，青丝入火神剑铸成',
        'extraImgs': {}
    },
    {
        'title': '干将莫邪（下篇·复仇）',
        'subtitle': '青锋出匣，白虹贯日。赤比借客头颅，三王之墓终雪万古冤。',
        'category': '卷五 · 幻化与器物',
        'originalMyth': '《搜神记·三王墓》',
        'classicQuote': '客持头往见楚王，王大喜。客曰：“此勇士头也，当于汤镬煮之。”王从之，煮三日三夜不烂。',
        'coverImg': 'assets/illustrations/art_ganjiang.jpg',
        'inlineImg': 'assets/illustrations/illust_25.png',
        'imgCaption': '三王之墓沸汤白刃，孤客仗义雪恨仇深',
        'extraImgs': {}
    },
    {
        'title': '钟馗嫁妹',
        'subtitle': '生前屈死，死后封神。红袍破帽夜行，送舍妹嫁予人间良人。',
        'category': '卷四 · 志怪与幽冥',
        'originalMyth': '民间钟馗信仰 ·《唐逸史》',
        'classicQuote': '终南钟馗，虽为鬼王，心怀赤诚。挑灯夜引，百鬼肃穆，嫁妹于杜生，骨肉至情。',
        'coverImg': 'assets/illustrations/illust_22.png',
        'inlineImg': 'assets/illustrations/illust_23.png',
        'imgCaption': '漫天风雪夜送红妆，朱判执灯情深骨肉',
        'extraImgs': {
            2: ('assets/illustrations/illust_21.png', '重门森严青面门神，阴阳两界规矩森然')
        }
    },
    {
        'title': '白蛇·雷峰塔',
        'subtitle': '被一个人爱得太满，本身就是一座雷峰塔。西湖水干，江潮不起。',
        'category': '卷三 · 人间与执念',
        'originalMyth': '《白娘子永镇雷峰塔》',
        'classicQuote': '西湖水干，江潮不起，雷峰塔倒，白蛇出世。情之所钟，生死不悔。',
        'coverImg': 'assets/illustrations/art_baishe.jpg',
        'inlineImg': 'assets/illustrations/art_baishe.jpg',
        'imgCaption': '西湖烟雨雷峰古塔，素贞执伞巨蟒盘霄',
        'extraImgs': {}
    },
    {
        'title': '黄粱一梦',
        'subtitle': '邯郸驿中枕，一梦五十年。荣华富贵散尽，锅中黍米犹自未熟。',
        'category': '卷五 · 幻化与器物',
        'originalMyth': '《枕中记》',
        'classicQuote': '卢生欠伸而寤，见方卧于邸中，吕翁坐其旁，主人蒸黍尚未熟。生抚案惊曰：“岂其梦寐耶？”',
        'coverImg': 'assets/illustrations/illust_33.png',
        'inlineImg': 'assets/illustrations/illust_27.png',
        'imgCaption': '邯郸客馆灯火微明，一枕梦回五十年欢悲',
        'extraImgs': {}
    }
]

articles = []

for idx in range(30):
    cfg = story_configs[idx]
    rw = raw[idx]
    issue_no = idx + 1
    issue_str = f"No. {issue_no:03d}"
    raw_chs = rw.get('chapters', [])
    raw_paras = rw.get('fullParagraphs', [])
    
    # Process Chapters specifically per story
    processed_chs = []
    author_note = None

    # SPECIAL CASE 1: 梁祝·化蝶 (Split into 3 dramatic acts, filter 2026.9.25)
    if cfg['title'] == '梁祝·化蝶':
        clean_p = [p.strip() for p in raw_paras if p.strip() and not re.match(r'^(202\d|\d{4}年)', p.strip())]
        processed_chs = [
            {'title': '第一幕 · 青绸车', 'paragraphs': clean_p[0:12]},
            {'title': '第二幕 · 黄土坟', 'paragraphs': clean_p[12:22]},
            {'title': '第三幕 · 彩蝶说', 'paragraphs': clean_p[22:33]}
        ]

    # SPECIAL CASE 2: 夸父逐日 (Extract author manifesto to author_note)
    elif cfg['title'] == '夸父逐日':
        # P0: 写作阐述, P1-P3: manifesto
        manifesto_lines = []
        story_paras = []
        is_manifesto = False
        
        for p in raw_paras:
            p_s = p.strip()
            if not p_s: continue
            if p_s in ['写作阐述', '夸父逐日之后·新编']:
                is_manifesto = True
                continue
            if is_manifesto and p_s.startswith(('一、', '一.')):
                is_manifesto = False
                story_paras.append(p_s)
                continue
            if is_manifesto:
                manifesto_lines.append(p_s)
            else:
                story_paras.append(p_s)
                
        if manifesto_lines:
            author_note = "\n\n".join(manifesto_lines)
            
        # Re-chunk story paras into chapters
        curr_c = {'title': '第一幕', 'paragraphs': []}
        ch_counter = 1
        for p in story_paras:
            m = re.match(r'^[一二三四五六七八九十百]+[、\.]?\s*(.*)', p)
            if m:
                if curr_c['paragraphs']:
                    processed_chs.append(curr_c)
                ch_counter += 1
                num_clean = re.sub(r'[、\.\s]', '', p)
                curr_c = {'title': f'第 {num_clean} 幕' if '幕' not in num_clean else num_clean, 'paragraphs': []}
            else:
                curr_c['paragraphs'].append(p)
        if curr_c['paragraphs']:
            processed_chs.append(curr_c)

    # SPECIAL CASE 3: 白水素女 (Split embedded 四 and 五)
    elif cfg['title'] == '白水素女（田螺姑娘）':
        for ch in raw_chs:
            ch_t = ch.get('title', '')
            c_paras = ch.get('paragraphs', [])
            sub_curr = {'title': ch_t, 'paragraphs': []}
            for p in c_paras:
                p_s = p.strip()
                if p_s in ['四', '四、']:
                    if sub_curr['paragraphs']:
                        processed_chs.append(sub_curr)
                    sub_curr = {'title': '四、', 'paragraphs': []}
                elif p_s in ['五', '五、']:
                    if sub_curr['paragraphs']:
                        processed_chs.append(sub_curr)
                    sub_curr = {'title': '五、', 'paragraphs': []}
                else:
                    sub_curr['paragraphs'].append(p_s)
            if sub_curr['paragraphs']:
                processed_chs.append(sub_curr)

    # SPECIAL CASE 4: 精卫填海 (Split embedded 十三)
    elif cfg['title'] == '精卫填海':
        for ch in raw_chs:
            ch_t = ch.get('title', '')
            c_paras = ch.get('paragraphs', [])
            sub_curr = {'title': ch_t, 'paragraphs': []}
            for p in c_paras:
                p_s = p.strip()
                if p_s.startswith(('十三、', '十三.')):
                    if sub_curr['paragraphs']:
                        processed_chs.append(sub_curr)
                    sub_curr = {'title': '十三、', 'paragraphs': []}
                else:
                    sub_curr['paragraphs'].append(p_s)
            if sub_curr['paragraphs']:
                processed_chs.append(sub_curr)

    # DEFAULT CASES
    else:
        # Merge tiny prologue (< 3 paragraphs) into the following chapter
        if len(raw_chs) > 1 and raw_chs[0].get('title', '').strip() in ['开篇', '序章'] and len(raw_chs[0].get('paragraphs', [])) < 3:
            prologue_paras = raw_chs[0].get('paragraphs', [])
            first_act = dict(raw_chs[1])
            first_act['paragraphs'] = prologue_paras + first_act.get('paragraphs', [])
            processed_chs.append(first_act)
            for c in raw_chs[2:]:
                processed_chs.append(c)
        else:
            processed_chs = list(raw_chs)

    def format_act_title(raw_title, idx):
        t = raw_title.strip()
        if t in ['开篇', '序章']:
            return '序 幕'
        m = re.match(r'^([一二三四五六七八九十百]+)[、\.]?\s*(.*)', t)
        if m:
            num, rest = m.group(1), m.group(2).strip()
            if rest:
                return f'第 {num} 幕 · {rest}'
            return f'第 {num} 幕'
        if not t.startswith('第') and not t.endswith('幕'):
            return f'第 {idx+1} 幕 · {t}'
        return t

    # Helper to pick a punchy pull quote from paragraphs
    def find_pull_quote(paras):
        for p in paras:
            p_clean = p.strip('“"”\'')
            if 14 <= len(p_clean) <= 60 and not p_clean.startswith(('“', '”')):
                return p_clean
        if paras:
            mid = paras[len(paras)//2]
            sentences = re.split(r'[。！？；]', mid)
            for s in sentences:
                s = s.strip()
                if 14 <= len(s) <= 50:
                    return s
        return None

    # Clean all paragraphs thoroughly
    clean_chapters = []
    total_words = 0
    full_paragraphs = []

    for ch_idx, ch in enumerate(processed_chs):
        ch_raw_t = ch.get('title', f'第 {ch_idx+1} 幕')
        ch_fmt_t = format_act_title(ch_raw_t, ch_idx)
        raw_p = ch.get('paragraphs', [])
        
        cleaned_paras = []
        for p in raw_p:
            p_clean = p.strip()
            if not p_clean:
                continue
            # Remove title echo, stray author tags, date stamps
            if p_clean in ['不周', '扑通', '写作阐述', '白蛇 · 新编', '白蛇·新编', '故事梗概', '角色设定', 
                           cfg['title'], rw.get('title', ''), ch_raw_t, ch_fmt_t] or \
               p_clean.startswith(('《' + cfg['title'], '【')) or \
               re.match(r'^(202\d[\.\-\/]\d+[\.\-\/]\d+|\d{4}年\d+月|完$)', p_clean):
                continue
            cleaned_paras.append(p_clean)
            total_words += len(p_clean)
            full_paragraphs.append(p_clean)
            
        if cleaned_paras:
            clean_chapters.append({
                'title': ch_fmt_t,
                'paragraphs': cleaned_paras
            })

    # Build Pages
    pages = []

    # 1. COVER PAGE (全画幅大封面)
    pages.append({
        'type': 'cover',
        'pageNumber': 1,
        'title': cfg['title'],
        'subtitle': cfg['subtitle'],
        'category': cfg['category'],
        'issueNumber': issue_str,
        'originalMyth': cfg['originalMyth'],
        'author': 'GX',
        'authorTitle': '神话重构作家 · 独立小说家',
        'wordCount': total_words,
        'readMinutes': max(3, round(total_words / 350)),
        'coverImg': cfg['coverImg']
    })

    # 2. INSCRIPTION PAGE (原典题记页)
    inscr_obj = {
        'type': 'inscription',
        'pageNumber': 2,
        'title': cfg['title'],
        'quote': cfg['classicQuote'],
        'originalMyth': cfg['originalMyth'],
        'issueNumber': issue_str,
        'coverImg': cfg['coverImg']
    }
    if author_note:
        inscr_obj['authorNote'] = author_note
    pages.append(inscr_obj)

    # 3. CHAPTER PAGES (章节杂志页 · 纯粹严谨顶格中文文学排版)
    page_counter = 3
    total_acts = len(clean_chapters)

    for ch_idx, ch in enumerate(clean_chapters):
        ch_title = ch['title']
        ch_paras = ch['paragraphs']
        
        # Determine illustration for this chapter
        ch_img = None
        ch_caption = None
        
        if ch_idx == 0:
            ch_img = cfg['inlineImg']
            ch_caption = cfg['imgCaption']
        elif (ch_idx + 1) in cfg.get('extraImgs', {}):
            ch_img, ch_caption = cfg['extraImgs'][ch_idx + 1]
            
        pull_q = find_pull_quote(ch_paras) if not ch_img else None
        
        # Next chapter info for in-page progression
        next_ch_title = clean_chapters[ch_idx + 1]['title'] if (ch_idx + 1 < total_acts) else None
        prev_ch_title = clean_chapters[ch_idx - 1]['title'] if (ch_idx > 0) else None
        
        pages.append({
            'type': 'chapter',
            'pageNumber': page_counter,
            'title': cfg['title'],
            'chapterTitle': ch_title,
            'chapterIndex': ch_idx + 1,
            'totalChapters': total_acts,
            'issueNumber': issue_str,
            'category': cfg['category'],
            'paragraphs': ch_paras,
            'inlineImg': ch_img,
            'imgCaption': ch_caption,
            'pullQuote': pull_q,
            'nextChapterTitle': next_ch_title,
            'prevChapterTitle': prev_ch_title
        })
        page_counter += 1

    # 4. COLOPHON PAGE (卷终刊记页)
    next_issue_no = f"No. {issue_no + 1:03d}" if issue_no < 30 else "No. 001"
    pages.append({
        'type': 'colophon',
        'pageNumber': page_counter,
        'title': cfg['title'],
        'issueNumber': issue_str,
        'category': cfg['category'],
        'wordCount': total_words,
        'nextIssueNumber': next_issue_no,
        'author': 'GX'
    })

    article_obj = {
        'id': f'issue-{issue_no:03d}',
        'issueNumber': issue_str,
        'cleanTitle': cfg['title'],
        'subtitle': cfg['subtitle'],
        'category': cfg['category'],
        'originalMyth': cfg['originalMyth'],
        'classicQuote': cfg['classicQuote'],
        'author': 'GX',
        'authorTitle': '神话重构作家 · 独立小说家',
        'wordCount': total_words,
        'readMinutes': max(3, round(total_words / 350)),
        'coverImg': cfg['coverImg'],
        'inlineImg': cfg['inlineImg'],
        'imgCaption': cfg['imgCaption'],
        'authorNote': author_note,
        'pages': pages,
        'totalPages': len(pages),
        'chapters': [{'title': ch['title'], 'count': len(ch['paragraphs'])} for ch in clean_chapters],
        'fullParagraphs': full_paragraphs
    }
    articles.append(article_obj)

print(f"Successfully constructed {len(articles)} refined articles with accurate illustrations & pristine chapter data!")

# Save to refined_articles.json
out_json = '/Users/gx/.gemini/antigravity/scratch/myth-magazine/data/refined_articles.json'
with open(out_json, 'w', encoding='utf-8') as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)
print(f"Written: {out_json}")

# Save to js/data.js
out_js = '/Users/gx/.gemini/antigravity/scratch/myth-magazine/js/data.js'
with open(out_js, 'w', encoding='utf-8') as f:
    f.write('/* Auto-generated full-bleed chapter-based myth magazine database with verified illustrations */\n')
    f.write('window.MYTH_ARTICLES = ')
    json.dump(articles, f, ensure_ascii=False, indent=2)
print(f"Written: {out_js}")
