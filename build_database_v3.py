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
        return []

def read_md(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        return lines
    except Exception as e:
        return []

# Precise mapping of illustrations to stories
story_configs = [
    {
        'key': '共工',
        'title': '共工怒触不周山',
        'subtitle': '天柱折，地维绝。那个不肯认输的人，把头撞向了不周山。',
        'category': '卷二 · 反叛与神罚',
        'originalMyth': '《山海经·大荒西经》·《淮南子·天文训》',
        'classicQuote': '天柱折，地维绝。天倾西北，故日月星辰移焉；地不满东南，故水潦尘埃归焉。',
        'coverImg': 'assets/illustrations/illust_01.png',
        'inlineImg': 'assets/illustrations/illust_02.png',
        'imgCaption': '共工撞向不周山，山崩石裂，天倾西北'
    },
    {
        'key': '精卫',
        'title': '精卫填海',
        'subtitle': '扑通。扑通。扑通。东海浩瀚，衔微木以填沧海。',
        'category': '卷二 · 反叛与神罚',
        'originalMyth': '《山海经·北山经》',
        'classicQuote': '炎帝之少女，名曰女娃。女娃游于东海，溺而不返，故为精卫，常衔西山之木石，以堙于东海。',
        'coverImg': 'assets/illustrations/illust_03.png',
        'inlineImg': 'assets/illustrations/illust_04.png',
        'imgCaption': '白鸟衔石投海，水底宫殿隐现'
    },
    {
        'key': '仓颉',
        'title': '仓颉造字',
        'subtitle': '天雨粟，鬼夜哭。当第一道符号落入泥板，天地从此有了记忆。',
        'category': '卷一 · 创世与洪荒',
        'originalMyth': '《淮南子·本经训》·《说文解字序》',
        'classicQuote': '颉首四目，通于神明，仰观奎星圜曲之势，俯察龟文鸟迹之象，博采众美，合而为字。',
        'coverImg': 'assets/illustrations/illust_09.png',
        'inlineImg': 'assets/illustrations/illust_10.png',
        'imgCaption': '仓颉仰观奎星鸟迹，刻符于石板'
    },
    {
        'key': '伯牙',
        'title': '伯牙子期',
        'subtitle': '摔碎瑶琴凤尾寒，子期不在对谁弹。知音之死，高山绝响。',
        'category': '卷三 · 人间与执念',
        'originalMyth': '《列子·汤问》·《吕氏春秋·本味》',
        'classicQuote': '伯牙善鼓琴，钟子期善听。伯牙鼓琴，志在高山，钟子期曰：“善哉，峨峨兮若泰山！”',
        'coverImg': 'assets/illustrations/illust_29.png',
        'inlineImg': 'assets/illustrations/illust_30.png',
        'imgCaption': '汉阳江口抚琴，高山流水遇知音'
    },
    {
        'key': '八仙',
        'title': '八仙过海',
        'subtitle': '都别坐云了。坐云过海算什么本事？今日咱们八个，各显神通。',
        'category': '卷四 · 志怪与幽冥',
        'originalMyth': '《东游记》· 民间八仙传说',
        'classicQuote': '八仙过海，各显神通。沧海横流，不借天风，但凭手中一物，踏破万顷狂澜。',
        'coverImg': 'assets/illustrations/illust_28.png',
        'inlineImg': 'assets/illustrations/illust_35.png',
        'imgCaption': '东海滔天浊浪，八仙抛物泛舟'
    },
    {
        'key': '刑天',
        'title': '刑天舞干戚',
        'subtitle': '以乳为目，以脐为口，操干戚以舞。头颅已断，战意不休。',
        'category': '卷二 · 反叛与神罚',
        'originalMyth': '《山海经·海外西经》· 陶渊明《读山海经》',
        'classicQuote': '刑天与帝至此争神，帝断其首，葬之常羊之山。乃以乳为目，以脐为口，操干戚以舞。',
        'coverImg': 'assets/illustrations/illust_12.png',
        'inlineImg': 'assets/illustrations/illust_14.png',
        'imgCaption': '月下断首战神，操干戚长舞不休'
    },
    {
        'key': '化蝶',
        'title': '梁祝·化蝶',
        'subtitle': '牛车走得慢。这个静得不对，静得像车里坐的不是个大活人。',
        'category': '卷三 · 人间与执念',
        'originalMyth': '民间四大传说 · 梁山伯与祝英台',
        'classicQuote': '生不能同衾，死当同穴。冢忽自开，祝跃入其中，合之，化为双蝶，翩翩而舞。',
        'coverImg': 'assets/illustrations/illust_30.png',
        'inlineImg': 'assets/illustrations/illust_06.png',
        'imgCaption': '冢开蝶舞，草木皆染凄风冷雨'
    },
    {
        'key': '后羿',
        'title': '后羿射日',
        'subtitle': '最后一个太阳。三十步开外，那是天底下最好的一张后背。',
        'category': '卷二 · 反叛与神罚',
        'originalMyth': '《淮南子·本经训》·《楚辞·天问》',
        'classicQuote': '逮至尧之时，十日并出，焦禾稼，杀草木，而民无所食。尧乃使羿上射十日，中其九日。',
        'coverImg': 'assets/illustrations/illust_13.png',
        'inlineImg': 'assets/illustrations/illust_14.png',
        'imgCaption': '焦土裂原之上，羿挽彤弓射日'
    },
    {
        'key': '大禹',
        'title': '大禹涂山',
        'subtitle': '涂山的坛，一夜之间垒了起来。万国诸侯执玉帛，功成还是帝王心。',
        'category': '卷一 · 创世与洪荒',
        'originalMyth': '《史记·夏本纪》·《左传》',
        'classicQuote': '禹会诸侯于涂山，执玉帛者万国。防风氏后至，禹杀而戮之。',
        'coverImg': 'assets/illustrations/illust_15.png',
        'inlineImg': 'assets/illustrations/illust_16.png',
        'imgCaption': '涂山之会，三丈高坛下万国执玉帛'
    },
    {
        'key': '夸父',
        'title': '夸父逐日',
        'subtitle': '夸父死之后呢？那根手杖发芽的时候，他还在不在旁边看着？',
        'category': '卷二 · 反叛与神罚',
        'originalMyth': '《山海经·海外北经》',
        'classicQuote': '夸父与日逐走，入日；渴，欲得饮，饮于河、渭；未至，道渴而死。弃其杖，化为邓林。',
        'coverImg': 'assets/illustrations/illust_07.png',
        'inlineImg': 'assets/illustrations/illust_13.png',
        'imgCaption': '逐日奔赴长途，手杖化作漫野桃林'
    },
    {
        'key': '女娲',
        'title': '女娲造人与补天',
        'subtitle': '神不大数得清年月——捏一个泥人，到他们学会下跪，原来这么短。',
        'category': '卷一 · 创世与洪荒',
        'originalMyth': '《风俗通义》·《淮南子·览冥训》',
        'classicQuote': '女娲炼五色石以补苍天，断鳌足以立四极，杀黑龙以济冀州，积芦灰以止淫水。',
        'coverImg': 'assets/illustrations/illust_08.png',
        'inlineImg': 'assets/illustrations/illust_01.png',
        'imgCaption': '炼石补天，苍茫大地上初生的泥偶'
    },
    {
        'key': '妲己',
        'title': '苏妲己',
        'subtitle': '不是真相。真相我也没有。我只是写下：他们造出的九尾狐妖，究竟是谁。',
        'category': '卷三 · 人间与执念',
        'originalMyth': '《史记·殷本纪》·《列女传》',
        'classicQuote': '纣得妲己，爱幸百计，妲己之言听计从。天下谓之倾国，而史家独归罪于红颜。',
        'coverImg': 'assets/illustrations/illust_21.png',
        'inlineImg': 'assets/illustrations/illust_26.png',
        'imgCaption': '朝歌深宫冷月，青铜鼎外的孤影'
    },
    {
        'key': '孟姜女',
        'title': '孟姜女哭长城',
        'subtitle': '那一刹，她还以为是天塌了。城她哭了三日，原以为墙听不见。',
        'category': '卷三 · 人间与执念',
        'originalMyth': '《左传》杞梁妻 · 民间传说',
        'classicQuote': '杞梁死，其妻迎其柩于路，抚柩而哭，哀声动天，十里长城为之崩塌。',
        'coverImg': 'assets/illustrations/illust_22.png',
        'inlineImg': 'assets/illustrations/illust_23.png',
        'imgCaption': '泥砖坚壁之下，漫天风雪哭断长城'
    },
    {
        'key': '孟婆',
        'title': '孟婆汤',
        'subtitle': '奈何桥头，队排得望不到尾。舀汤舀了一宿——地府没有宿，就是一直舀。',
        'category': '卷四 · 志怪与幽冥',
        'originalMyth': '幽冥神话 · 忘川之畔',
        'classicQuote': '过奈何桥，饮孟婆汤，前世爱恨、冤亲债孽，入腹化水，尽皆忘却，始得轮回报应。',
        'coverImg': 'assets/illustrations/illust_16.png',
        'inlineImg': 'assets/illustrations/illust_27.png',
        'imgCaption': '忘川河边奈何桥，大锅咕嘟粗瓷舀汤'
    },
    {
        'key': '尾生',
        'title': '尾生抱柱',
        'subtitle': '约的是晌午。尾生天没亮就到了。水漫上来的时候，他握紧了桥柱。',
        'category': '卷三 · 人间与执念',
        'originalMyth': '《庄子·盗跖》·《战国策·燕策一》',
        'classicQuote': '尾生与女子期于梁下，女子不来，水至不去，抱梁柱而死。信之至也，亦痴之至也。',
        'coverImg': 'assets/illustrations/illust_23.png',
        'inlineImg': 'assets/illustrations/illust_22.png',
        'imgCaption': '入海河口潮涌，木桥柱下不肯松开的手'
    },
    {
        'key': '愚公',
        'title': '愚公移山',
        'subtitle': '指通豫南，达于汉阴。两座大山黑沉沉地立着，谁是头一个抄起锄头的人。',
        'category': '卷二 · 反叛与神罚',
        'originalMyth': '《列子·汤问》',
        'classicQuote': '虽我之死，有子存焉；子又生孙，孙又生子；子子孙孙无穷匮也，而山不加增，何苦而不平？',
        'coverImg': 'assets/illustrations/illust_18.png',
        'inlineImg': 'assets/illustrations/illust_17.png',
        'imgCaption': '太行王屋万仞壁立，老朽与儿孙一箕一锄'
    },
    {
        'key': '梦蝶',
        'title': '庄周梦蝶',
        'subtitle': '宋城东门代写书信的老庄。不知庄之梦为胡蝶与，蝴蝶之梦为庄周与？',
        'category': '卷五 · 幻化与器物',
        'originalMyth': '《庄子·齐物论》',
        'classicQuote': '昔者庄周梦为胡蝶，栩栩然胡蝶也，自喻适志与！不知周也。俄然觉，则蘧蘧然周也。',
        'coverImg': 'assets/illustrations/illust_06.png',
        'inlineImg': 'assets/illustrations/illust_27.png',
        'imgCaption': '宋城荒草丛中，灰布衫学者与翩然白蝶'
    },
    {
        'key': '混沌',
        'title': '混沌之死',
        'subtitle': '日凿一窍，七日而混沌死。哪儿都是我，我就是哪儿。',
        'category': '卷一 · 创世与洪荒',
        'originalMyth': '《庄子·应帝王》',
        'classicQuote': '南海之帝为儵，北海之帝为忽，中央之帝为浑沌。日凿一窍，七日而浑沌死。',
        'coverImg': 'assets/illustrations/illust_19.png',
        'inlineImg': 'assets/illustrations/illust_20.png',
        'imgCaption': '无极混沦之中，开凿七窍的神明'
    },
    {
        'key': '点睛',
        'title': '画龙点睛',
        'subtitle': '四条龙，它是左数第二条。点上眼睛那一刻，金陵安乐寺风雷大作。',
        'category': '卷五 · 幻化与器物',
        'originalMyth': '《历代名画记》',
        'classicQuote': '张僧繇于金陵安乐寺画四白龙，不点眼睛。点其一，雷电破壁，一龙乘云上天。',
        'coverImg': 'assets/illustrations/illust_05.png',
        'inlineImg': 'assets/illustrations/illust_04.png',
        'imgCaption': '安乐寺粉壁雷破，素白神龙乘电腾空'
    },
    {
        'key': '烂柯',
        'title': '烂柯人',
        'subtitle': '手心一层茧，握紧了斧柄。山中方一日，世上已千年。',
        'category': '卷五 · 幻化与器物',
        'originalMyth': '《述异记》王质烂柯',
        'classicQuote': '王质入山伐木，见二童子弈棋。童子与质一物，如枣核，食之不饥。局罢，斧柯尽烂。',
        'coverImg': 'assets/illustrations/illust_17.png',
        'inlineImg': 'assets/illustrations/illust_18.png',
        'imgCaption': '深山松岩观棋局，青苔落满朽烂斧柄'
    },
    {
        'key': '画皮',
        'title': '聊斋·画皮',
        'subtitle': '天快亮了，得赶紧把脸画上。露出底下的皮，翠绿微凉。',
        'category': '卷四 · 志怪与幽冥',
        'originalMyth': '蒲松龄《聊斋志异·画皮》',
        'classicQuote': '见一狞鬼，面翠色，齿巉巉如锯。铺人皮于榻上，执彩笔而绘之；已而掷笔，举皮如振衣状。',
        'coverImg': 'assets/illustrations/illust_26.png',
        'inlineImg': 'assets/illustrations/illust_31.png',
        'imgCaption': '油灯微烁，榻前执彩笔勾勒翠色人面'
    },
    {
        'key': '白水',
        'title': '白水素女（田螺姑娘）',
        'subtitle': '我替一个不知道我在的人，烧了不知多少顿饭。水汽蒸腾里的人间烟火。',
        'category': '卷五 · 幻化与器物',
        'originalMyth': '《搜神后记》白水素女',
        'classicQuote': '谢端无妻，于田中得一大螺，贮于瓮中。自是日后，日日入炊，甘香满室，端潜归窥之。',
        'coverImg': 'assets/illustrations/illust_10.png',
        'inlineImg': 'assets/illustrations/illust_09.png',
        'imgCaption': '陶瓮窄光渐亮，灶前烟火蒸腾的素衣螺仙'
    },
    {
        'key': '神农',
        'title': '神农尝百草',
        'subtitle': '那味草是苦的，苦里带一丝回甜。水晶肚子里，看得到青黄黑白。',
        'category': '卷一 · 创世与洪荒',
        'originalMyth': '《淮南子·修务训》·《史记》',
        'classicQuote': '神农尝百草之滋味，知水泉之甘苦，令民知所避就。当此之时，一日而遇七十毒。',
        'coverImg': 'assets/illustrations/illust_20.png',
        'inlineImg': 'assets/illustrations/illust_19.png',
        'imgCaption': '水晶腹内验百毒，苍生医药初创时'
    },
    {
        'key': '织女',
        'title': '牛郎织女·七夕',
        'subtitle': '七夕这一夜，天底下的人都在为我和他过节。我站在鹊桥上，听得见下界。',
        'category': '卷三 · 人间与执念',
        'originalMyth': '《诗经·小雅·大东》· 古诗十九首',
        'classicQuote': '迢迢牵牛星，皎皎河汉女。纤纤擢素手，札札弄机杼。终日不成章，泣涕零如雨。',
        'coverImg': 'assets/illustrations/illust_39.png',
        'inlineImg': 'assets/illustrations/illust_32.png',
        'imgCaption': '天河浩瀚迢迢，玉簪划破璀璨星汉'
    },
    {
        'key': '聂小倩',
        'title': '倩女幽魂（聂小倩）',
        'subtitle': '后来他们都说宁采臣救了我。兰若寺夜雨，红尘与白骨之间。',
        'category': '卷四 · 志怪与幽冥',
        'originalMyth': '蒲松龄《聊斋志异·聂小倩》',
        'classicQuote': '小倩，姓聂氏，十八夭卒。兰若夜雨，白骨红粉。宁生仗剑独立，不为妖惑，始脱幽渊。',
        'coverImg': 'assets/illustrations/illust_31.png',
        'inlineImg': 'assets/illustrations/illust_26.png',
        'imgCaption': '兰若荒刹夜雨，冷雾中执伞的素衣女鬼'
    },
    {
        'key': '莫邪新编_v1',
        'title': '干将莫邪（上篇·熔金）',
        'subtitle': '铁化不开。一百天了。楚王要一把剑，天底下最好的剑。',
        'category': '卷五 · 幻化与器物',
        'originalMyth': '《吴越春秋·阖闾内传》',
        'classicQuote': '干将作剑，采五山之铁精，六合之金英。莫邪断发剪爪，投于炉中，金铁乃铄，遂以成剑。',
        'coverImg': 'assets/illustrations/illust_24.png',
        'inlineImg': 'assets/illustrations/illust_25.png',
        'imgCaption': '熔炉炽红如昼，炉膛金铁久灼不化'
    },
    {
        'key': '莫邪新编_v2',
        'title': '干将莫邪（下篇·复仇）',
        'subtitle': '楚王把剑掂了掂，很满意。鼎中三首相咬，断颅不瞑目。',
        'category': '卷五 · 幻化与器物',
        'originalMyth': '《搜神记·三王墓》',
        'classicQuote': '客持剑砍王头，头堕镬中；客亦自脰。三首俱烂，不可识，分葬之，故通名“三王墓”。',
        'coverImg': 'assets/illustrations/illust_25.png',
        'inlineImg': 'assets/illustrations/illust_24.png',
        'imgCaption': '沸镬汤汤，三首相咬同沉沸水'
    },
    {
        'key': '钟馗',
        'title': '钟馗嫁妹',
        'subtitle': '除夕夜，杜家村。那扇柴门从里头闩死了。大鬼小鬼挑着红嫁妆。',
        'category': '卷四 · 志怪与幽冥',
        'originalMyth': '钟馗神话 · 民间年画传说',
        'classicQuote': '终南进士钟馗，殁而为神。感生前好友杜平之义，除夕夜率阴兵群鬼，鼓乐喧天，送妹出阁。',
        'coverImg': 'assets/illustrations/illust_11.png',
        'inlineImg': 'assets/illustrations/illust_28.png',
        'imgCaption': '除夕夜风雪荒村，傩神与百鬼挑嫁妆巡游'
    },
    {
        'key': '雷峰塔',
        'title': '白蛇·雷峰塔',
        'subtitle': '被一个人爱得太满，本身就是一座雷峰塔。细雨断桥，金山水漫。',
        'category': '卷三 · 人间与执念',
        'originalMyth': '《白蛇传》·《警世通言》',
        'classicQuote': '西湖水干，江潮不起，雷峰塔倒，白发才生。痴儿怨女，满纸荒唐，不过是一场金山水漫。',
        'coverImg': 'assets/illustrations/illust_04.png',
        'inlineImg': 'assets/illustrations/illust_03.png',
        'imgCaption': '细雨断桥之下，巍峨雷峰塔镇锁千年执念'
    },
    {
        'key': '黄粱',
        'title': '黄粱一梦',
        'subtitle': '卢生睁开眼的时候，手还是弯着的。掌心里那点温，正在散去。',
        'category': '卷五 · 幻化与器物',
        'originalMyth': '沈既济《枕中记》',
        'classicQuote': '卢生欠伸而寤，见其身方偃于邸舍中，吕翁坐其傍，主人蒸黄粱尚未熟，触类如故。',
        'coverImg': 'assets/illustrations/illust_27.png',
        'inlineImg': 'assets/illustrations/illust_06.png',
        'imgCaption': '客邸残灯初醒，青瓷枕上蒸粟尚温'
    }
]

files = sorted(os.listdir(desktop_path))
articles = []
issue_no = 1

for cfg in story_configs:
    key = cfg['key']
    matched_file = None
    for f in files:
        if '哪吒' in f: continue
        if key in f:
            matched_file = f
            break
            
    if not matched_file:
        continue

    full_path = os.path.join(desktop_path, matched_file)
    if matched_file.endswith('.docx'):
        raw_paras = read_docx(full_path)
    else:
        raw_paras = read_md(full_path)

    # Filter out header lines, titles, and empty lines
    clean_paras = []
    for p in raw_paras:
        p_s = p.strip()
        if not p_s or p_s.startswith(('写作阐述', '---', '===', '# ')):
            continue
        if p_s in [cfg['title'], '不周', '扑通', '开篇', '序章'] or (len(p_s) < 20 and ('新编' in p_s or p_s.startswith(('《', '第', '一、')))):
            continue
        clean_paras.append(p_s)

    total_words = sum(len(p) for p in clean_paras)
    if total_words < 50:
        continue

    # Construct the Full-Bleed Magazine Pages
    pages = []
    
    # 1. PAGE 1: FULL-BLEED COVER PAGE (全画幅沉浸封面)
    pages.append({
        'type': 'cover',
        'pageNumber': 1,
        'title': cfg['title'],
        'subtitle': cfg['subtitle'],
        'category': cfg['category'],
        'issueNumber': f'No. {issue_no:03d}',
        'originalMyth': cfg['originalMyth'],
        'author': 'GX',
        'authorTitle': '神话重构作家 · 独立小说家',
        'wordCount': total_words,
        'readMinutes': max(3, round(total_words / 350)),
        'coverImg': cfg['coverImg']
    })

    # 2. PAGE 2: INSCRIPTION / CLASSIC QUOTE SPREAD (原典题记页)
    pages.append({
        'type': 'inscription',
        'pageNumber': 2,
        'title': cfg['title'],
        'quote': cfg['classicQuote'],
        'originalMyth': cfg['originalMyth'],
        'issueNumber': f'No. {issue_no:03d}',
        'coverImg': cfg['coverImg']
    })

    # 3. CONTENT PAGES (带优雅正文与中插大画幅插图)
    p_idx = 0
    page_counter = 3
    has_injected_img = False

    while p_idx < len(clean_paras):
        # Pack 3 to 4 paragraphs per magazine page
        page_paras = []
        char_c = 0
        while p_idx < len(clean_paras) and (char_c < 320 or len(page_paras) < 2) and len(page_paras) < 4:
            page_paras.append(clean_paras[p_idx])
            char_c += len(clean_paras[p_idx])
            p_idx += 1

        # Check if we should place an inline illustration on this page (on page 3 or 4)
        page_img = None
        page_caption = None
        if not has_injected_img and page_counter >= 3:
            page_img = cfg['inlineImg']
            page_caption = cfg['imgCaption']
            has_injected_img = True

        pages.append({
            'type': 'content',
            'pageNumber': page_counter,
            'title': cfg['title'],
            'issueNumber': f'No. {issue_no:03d}',
            'category': cfg['category'],
            'paragraphs': page_paras,
            'inlineImg': page_img,
            'imgCaption': page_caption
        })
        page_counter += 1

    # 4. COLOPHON PAGE (卷终刊记页)
    next_issue_no = f'No. {issue_no + 1:03d}' if issue_no < 30 else 'No. 001'
    pages.append({
        'type': 'colophon',
        'pageNumber': page_counter,
        'title': cfg['title'],
        'issueNumber': f'No. {issue_no:03d}',
        'category': cfg['category'],
        'wordCount': total_words,
        'nextIssueNumber': next_issue_no,
        'author': 'GX'
    })

    article_obj = {
        'id': f'issue-{issue_no:03d}',
        'issueNumber': f'No. {issue_no:03d}',
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
        'pages': pages,
        'totalPages': len(pages),
        'fullParagraphs': clean_paras
    }
    articles.append(article_obj)
    issue_no += 1

print(f"Built {len(articles)} articles with full-bleed pages and illustrations!")
out_path = os.path.join(output_dir, 'refined_articles.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

js_path = '/Users/gx/.gemini/antigravity/scratch/myth-magazine/js/data.js'
with open(js_path, 'w', encoding='utf-8') as f:
    f.write('window.MYTH_ARTICLES = ' + json.dumps(articles, ensure_ascii=False) + ';\n')

print(f"Exported to {js_path} successfully!")
