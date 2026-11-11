"""Source ink regions for publication type, measured at the legacy 2480px layout."""
# Text rows are bounded independently, excluding logos and card outlines.
TARGETS=[]
def add(t,r,kind='dark'):TARGETS.append((t,r,kind))
add('Google認定資格を持つ講師から、',[120,1380,2410,1572],'white')
add('AIを実践的に学ぶ。',[120,1573,2180,1785],'white')
for t,y0,y1 in [('AIビジネス専門学校では、Google認定資格を持つ講師が、',1828,1892),('最新のAIツールとGoogleのサービスを使い、実践的に指導します。',1920,1988),('学校で学んだことを、将来の仕事にそのまま活かせる力を育てます。',2013,2080)]:add(t,[140,y0,2390,y1],'white')
add('Google認定資格を持つ講師が指導',[105,2180,1210,2270])
add('教育の専門知識と最新のAI活用スキルを持つ講師が、',[1280,2160,2380,2224]);add('基礎から実践まで丁寧に教えます。',[1280,2224,2380,2290])
for x,title,level in [(395,'Google','レベル1'),(1210,'Google','レベル2'),(2025,'Gemini',None)]:
 add(title,[x,2348,x+400,2415]);add('認定教育者',[x,2418,x+400,2485]);
 if level:add(level,[x,2495,x+400,2560])
for x,level in [(160,'Level 1'),(960,'Level 2')]:
 add('Google for Education',[x,2595,x+600,2650]);add('Certified Educator',[x,2648,x+600,2690]);add(level,[x,2695,x+600,2741])
add('Google for Education',[1760,2598,2395,2657]);add('Gemini Educator',[1760,2658,2395,2710])
for x,items in [(80,['授業でGoogleツールを','活用するための基礎知識と','実践力を持つ教員の資格です。']),(900,['より高度なテクノロジー活用と','学習環境設計のスキルを持つ','教員の資格です。']),(1730,['教育における生成AI(Gemini)の','効果的な活用能力を持つ','教員の資格です。'])]:
 for t,y0,y1 in zip(items,([2770,2832,2895] if x==80 else [2774,2839,2904]),([2831,2890,2958] if x==80 else [2831,2897,2962])):add(t,[x,y0,x+720,y1])
add('主な使用ツール',[90,3040,540,3120],'white');add('授業・課題・発表・学校生活の中で、さまざまなツールを使い学びます。',[585,3050,2405,3130])
for t,r in [('Gemini',[100,3290,410,3343]),('Google Workspace',[485,3285,1050,3350]),('NotebookLM',[1100,3284,1500,3340]),('ChatGPT',[2040,3300,2385,3355])]:add(t,r)
for x,x1,items,ys in [(60,420,['生成AI','文章・画像・分析'],[3357,3420]),(480,1050,['文書作成・資料作成','共同作業・データ管理'],[3357,3420]),(1090,1500,['調査・情報整理','レポート作成'],[3357,3420]),(1560,1970,['デザイン・画像作成','SNS・ポスター制作'],[3355,3419]),(2010,2420,['情報収集・アイデア出し','文章作成・要約'],[3365,3428])]:
 for t,y in zip(items,ys):add(t,[x,y,x1,y+57])
