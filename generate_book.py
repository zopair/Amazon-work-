#!/usr/bin/env python3
"""Generate an original 24-page bilingual children's book as a KDP-sized vector PDF."""
from pathlib import Path
import argparse
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
import arabic_reshaper
from bidi.algorithm import get_display

# KDP full bleed for 8.5 x 8.5 in trim: add 0.125 in to width and 0.25 in to height.
PW, PH = 8.625*inch, 8.75*inch
BX, BY, SAFE = .0625*inch, .125*inch, .375*inch
COLORS = ["#F36F76","#FFD45F","#65B9E8","#77C98B","#FFA45B","#A98BD8","#F2A5C5"]
# Each record: English title/body, Arabic title/body, Mom's English/Arabic prompt, art theme.
PAGES = [
("The Happy Little Train","A colorful journey full of love, fun, and surprises!","قطار الألوان السعيد","رحلة ملونة مليئة بالحب والمرح والمفاجآت!","Find the train on the cover and make a cheerful train sound: Choo-Choo!","أشيري إلى القطار على الغلاف، وقلّدا معاً صوته المرح: تشو تشو!","cover"),
("Hello, little friends!","I am Choo-Choo, the happy little train. I love colors, and I love you!","مرحباً يا أصدقائي الصغار!","أنا تشو تشو، القطار الصغير السعيد. أحب الألوان، وأحبكم أيضاً!","Ask your child the train's name, then share a big hug.","اسألي طفلك عن اسم القطار، ثم تبادلا عناقاً كبيراً.","train"),
("Look! A red train car!","Red like an apple. Red like a strawberry. Red, red, red!","انظر! عربة قطار حمراء!","أحمر مثل التفاحة. أحمر مثل الفراولة. أحمر، أحمر، أحمر!","Find something red together and point to it.","ابحثي مع طفلك عن شيء أحمر وأشيري إليه معاً.","red"),
("Here comes yellow!","Yellow like the sun. Yellow like a little chick. Hello, sunshine!","ها هو اللون الأصفر!","أصفر مثل الشمس. أصفر مثل الكتكوت الصغير. مرحباً أيتها الشمس!","Stretch your arms like sunshine and find something yellow.","ارفعي ذراعيك مثل أشعة الشمس وابحثا عن شيء أصفر.","yellow"),
("Blue, blue, beautiful blue!","Blue like the sky. Blue like the sea. Splash, splash, splash!","أزرق، أزرق، يا له من أزرق جميل!","أزرق مثل السماء. أزرق مثل البحر. شخ، شخ، شخ!","Make gentle splashing movements and find something blue.","حرّكي يديك كأنكما ترشان الماء، ثم ابحثا عن شيء أزرق.","blue"),
("Green is everywhere!","Green like the trees. Green like the leaves. Grow, little plants, grow!","اللون الأخضر في كل مكان!","أخضر مثل الأشجار. أخضر مثل الأوراق. كبرِي أيتها النباتات الصغيرة!","Pretend to be a tiny seed growing into a tall tree.","تظاهرا بأنكما بذرة صغيرة تكبر حتى تصبح شجرة طويلة.","green"),
("Orange is bright and sweet!","Orange like an orange. Orange like a carrot. Yummy, yummy!","البرتقالي مشرق وجميل!","برتقالي مثل البرتقالة. برتقالي مثل الجزرة. مممم، لذيذ!","Pretend to peel an orange and enjoy its lovely smell.","تظاهرا بتقشير برتقالة واستمتعا برائحتها الجميلة.","orange"),
("Purple is lovely!","Purple like grapes. Purple like little flowers. What a pretty color!","اللون البنفسجي جميل!","بنفسجي مثل العنب. بنفسجي مثل الزهور الصغيرة. يا له من لون رائع!","Make a little bunch of grapes together using your hands.","شكّلا بأيديكما عنقود عنب صغيراً.","purple"),
("Pink is sweet!","Pink like a flower. Pink like a little heart. I send you a hug!","اللون الوردي رقيق وجميل!","وردي مثل الزهرة. وردي مثل القلب الصغير. أرسل إليك حضناً دافئاً!","Draw a heart in the air and give each other a hug.","ارسمي قلباً في الهواء، ثم تبادلا عناقاً.","pink"),
("White, soft, and bright!","White like the clouds. White like fluffy sheep. So soft and sweet!","أبيض وناعم ومشرق!","أبيض مثل الغيوم. أبيض مثل الخراف الصوفية. ما أجمله من لون!","Make a fluffy cloud shape with your arms.","شكّلي بذراعيك سحابة ناعمة وكبيرة.","white"),
("Brown is warm!","Brown like a teddy bear. Brown like a tree. Hello, little bear!","اللون البني دافئ وجميل!","بني مثل الدبدوب. بني مثل جذع الشجرة. مرحباً أيها الدب الصغير!","Hug a teddy bear or toy and name its color.","احتضني دبدوباً أو لعبة محشوة، ثم سمّيا لونها.","brown"),
("One, two, three! Four, five, six!","Let's count the cars. Six colorful cars!","واحد، اثنان، ثلاثة! أربعة، خمسة، ستة!","هيا نعد العربات. ست عربات ملونة!","Count the six train cars together using your fingers.","عدّا عربات القطار الست معاً باستخدام أصابعكما.","count"),
("Who is hiding there?","A little bunny! Peek-a-boo! Hello, little bunny!","من الذي يختبئ هناك؟","إنه أرنب صغير! اختبئ... ها أنا أراك! مرحباً أيها الأرنب!","Play peek-a-boo by hiding your face and popping back with a smile.","العبا الغميضة؛ غطّي وجهك بيديك ثم أظهريه بابتسامة.","bunny"),
("Hello, big elephant!","You are so kind. Wave your trunk. Let's say hello!","مرحباً أيها الفيل الكبير!","أنت لطيف جداً. حرّك خرطومك الجميل. هيا نقول: مرحباً!","Use your arm as an elephant trunk and make a gentle elephant sound.","اجعلي ذراعك مثل خرطوم الفيل وقلّدا صوته بهدوء.","elephant"),
("Choo-Choo, here we go!","Colors everywhere we go. Red and yellow, green and blue. The happy train says: I love you!","تشو تشو، هيا ننطلق!","الألوان حولنا في كل مكان. أحمر وأصفر، أخضر وأزرق. والقطار السعيد يقول: أحبك!","Sing the train rhyme and clap gently with every color.","غني أنشودة القطار وصفّقي برفق مع ذكر كل لون.","song"),
("Look at the shapes!","A circle, round and bright. A square, with four sides. A triangle, with three sides. A star, shining bright!","انظر إلى الأشكال!","دائرة مستديرة وجميلة. مربع له أربعة أضلاع. مثلث له ثلاثة أضلاع. ونجمة تلمع ببريق جميل!","Draw each shape in the air, then find a matching object nearby.","ارسمي كل شكل في الهواء، ثم ابحثا عن شيء يشبهه حولكما.","shapes"),
("Numbers are fun!","One little train. Two little birds. Three pretty flowers. Four happy stars. Five big smiles!","الأرقام ممتعة!","قطار صغير واحد. عصفوران صغيران. ثلاث زهرات جميلة. أربع نجمات سعيدة. خمس ابتسامات كبيرة!","Count your fingers together from one to five.","عدّا أصابعكما معاً من واحد إلى خمسة.","numbers"),
("How do you feel today?","Happy? Sad? Surprised? All feelings are okay. I am here for you!","كيف تشعر اليوم؟","هل أنت سعيد؟ حزين؟ متفاجئ؟ كل مشاعرنا مقبولة. أنا هنا بجانبك!","Make happy, sad, and surprised faces. Let your child name their feelings.","مثّلي وجوهاً سعيدة وحزينة ومتفاجئة، ودعي طفلك يعبّر عن شعوره.","feelings"),
("Oh, little bird! Are you lost?","Let's help you. Friends help friends!","أوه، أيها العصفور الصغير! هل تهت عن عشك؟","هيا نساعدك. الأصدقاء يساعدون بعضهم!","Pretend to help a friend and talk about one kind thing you can do.","تظاهرا بمساعدة صديق، وتحدثا عن عمل لطيف يمكنكما القيام به.","bird"),
("Drip, drop, drip!","The rain is gone. Look! A beautiful rainbow! So many colors in the sky!","طق طق، قطرات المطر!","لقد توقف المطر. انظر! قوس قزح جميل! كم لوناً رائعاً في السماء!","Tap your fingers like raindrops, then draw a rainbow in the air.","انقري بأصابعك مثل قطرات المطر، ثم ارسما قوس قزح في الهواء.","rainbow"),
("Let's have a party!","Clap your hands. Move your feet. Turn around. Let's dance together!","هيا نقيم حفلة!","صفّق بيديك. حرّك قدميك. استدر حول نفسك. هيا نرقص معاً!","Dance together, clap three times, and turn around gently.","ارقصا معاً، وصفّقا ثلاث مرات، ثم استديرا بهدوء.","party"),
("Oh, what a lovely day!","I played and learned so much. Now I feel sleepy. Good night, little friends!","يا له من يوم جميل!","لقد لعبت وتعلمت الكثير. والآن أشعر بالنعاس. تصبحون على خير يا أصدقائي الصغار!","Take a slow breath together and enjoy a quiet moment.","خذا نفساً بطيئاً معاً واستمتعا بلحظة هادئة.","sleep"),
("Colors make the world bright.","Friends make the world happy. Learning is fun. And love is everywhere! See you again!","الألوان تجعل العالم جميلاً ومشرقاً.","والأصدقاء يجعلون العالم سعيداً. التعلم ممتع. والحب موجود في كل مكان! نلتقي مرة أخرى!","Ask about your child's favorite color and favorite moment in the story.","اسألي طفلك عن لونه المفضل وأجمل لحظة في القصة.","friends"),
("The End!","But every day is a new adventure. Keep smiling. Keep learning. And keep loving!","النهاية!","ولكن كل يوم يحمل مغامرة جديدة. ابتسم دائماً. وتعلم دائماً. واجعل الحب يملأ قلبك!","Ask if your child would like to read the story again, then share a hug.","اسألي طفلك إن كان يرغب في قراءة القصة مرة أخرى، ثم تبادلا عناقاً.","end"),
]
PALETTE = {
"cover":("#73C8EF","#FCE28A"),"train":("#79C9EF","#DDF5FF"),"red":("#F36F76","#FFE0DF"),
"yellow":("#FFD45F","#FFF2BF"),"blue":("#65B9E8","#D8F1FF"),"green":("#77C98B","#E0F4D9"),
"orange":("#FFA45B","#FFE5C8"),"purple":("#A98BD8","#EDE3FF"),"pink":("#F2A5C5","#FFE2EE"),
"white":("#DCEAF0","#F6FBFF"),"brown":("#B98562","#F1E0D0"),"count":("#79C9EF","#E9E0FF"),
"bunny":("#A7D98B","#FFF1D2"),"elephant":("#A9B7C8","#E1F0FF"),"song":("#F4A9C9","#FFF0C9"),
"shapes":("#8CCBEA","#FFF0C9"),"numbers":("#F6C66B","#E8E0FF"),"feelings":("#F3B4C9","#E5F4FF"),
"bird":("#A8D9A2","#FFF0CB"),"rainbow":("#85C8EA","#FCE8B8"),"party":("#F3A9C7","#FFF0C9"),
"sleep":("#8299C9","#E8E9FF"),"friends":("#8BCFA2","#FFF0D1"),"end":("#7BC5E9","#FFF0C9")}
def ar(s): return get_display(arabic_reshaper.reshape(s))
def para(c, text, x, top, width, font, size, color, align=1, leading=None):
    st=ParagraphStyle("p",fontName=font,fontSize=size,leading=leading or size*1.4,
        textColor=HexColor(color),alignment=align,spaceAfter=0)
    p=Paragraph(text,st); _,h=p.wrap(width,PH); p.drawOn(c,x,top-h)
def train(c,cx,cy,s):
    # Original vector train character, reused consistently on all pages.
    for i,col in enumerate(COLORS[:4]):
        x=cx+(i-2.2)*.83*s
        c.setFillColor(HexColor(col)); c.setStrokeColor(colors.white)
        c.roundRect(x,cy-.05*s,.72*s,.42*s,.12*s,fill=1,stroke=1)
        c.setFillColor(colors.white); c.circle(x+.19*s,cy-.10*s,.09*s,fill=1,stroke=0); c.circle(x+.53*s,cy-.10*s,.09*s,fill=1,stroke=0)
    c.setFillColor(HexColor("#62B8E8")); c.roundRect(cx-.15*s,cy-.02*s,1.05*s,.55*s,.16*s,fill=1,stroke=0)
    c.setFillColor(HexColor("#BFEAFF")); c.roundRect(cx+.48*s,cy+.22*s,.28*s,.25*s,.06*s,fill=1,stroke=0)
    c.setFillColor(colors.white); c.circle(cx+.24*s,cy+.27*s,.075*s,fill=1,stroke=0); c.circle(cx+.52*s,cy+.27*s,.075*s,fill=1,stroke=0)
    c.setFillColor(HexColor("#31536B")); c.circle(cx+.24*s,cy+.27*s,.018*s,fill=1,stroke=0); c.circle(cx+.52*s,cy+.27*s,.018*s,fill=1,stroke=0)
    c.setStrokeColor(HexColor("#31536B")); c.arc(cx+.28*s,cy+.10*s,cx+.52*s,cy+.28*s,205,130)
    for x in (cx+.12*s,cx+.72*s):
        c.setFillColor(HexColor("#526477")); c.circle(x,cy-.07*s,.12*s,fill=1,stroke=0)
        c.setFillColor(colors.white); c.circle(x,cy-.07*s,.045*s,fill=1,stroke=0)
def scene(c,kind):
    main,bg=map(HexColor,PALETTE[kind]); c.setFillColor(bg); c.rect(0,0,PW,PH,fill=1,stroke=0)
    c.setFillColor(main); c.circle(PW*.13,PH*.91,42,fill=1,stroke=0)
    c.setFillColor(colors.white); c.circle(PW*.77,PH*.88,25,fill=1,stroke=0); c.circle(PW*.83,PH*.89,31,fill=1,stroke=0)
    c.setFillColor(HexColor("#C9E9B7")); c.ellipse(-20,PH*.30,PW+20,PH*.53,fill=1,stroke=0)
    for i,col in enumerate(COLORS):
        c.setFillColor(HexColor(col)); c.circle((.10+i*.125)*PW,PH*(.67+(i%2)*.045),5+(i%3)*2,fill=1,stroke=0)
    if kind in ("rainbow","cover","end"):
        for i,col in enumerate(COLORS[:6]):
            c.setStrokeColor(HexColor(col)); c.setLineWidth(11); c.arc(PW*.24+i*2,PH*.48+i*2,PW*.76-i*2,PH*.96-i*2,0,180)
    elif kind in ("shapes","numbers","count"):
        for i,col in enumerate(COLORS[:5]):
            x=PW*(.18+i*.16); y=PH*.65; c.setFillColor(HexColor(col))
            if i%3==0: c.circle(x,y,18,fill=1,stroke=0)
            elif i%3==1: c.rect(x-16,y-16,32,32,fill=1,stroke=0)
            else:
                p=c.beginPath(); p.moveTo(x,y+20); p.lineTo(x-20,y-16); p.lineTo(x+20,y-16); p.close(); c.drawPath(p,fill=1,stroke=0)
    else:
        c.setFillColor(main)
        for i in range(5): c.circle(PW*(.18+i*.15),PH*(.65+(i%2)*.05),13+(i%3)*5,fill=1,stroke=0)
    train(c,PW*.52,PH*.39,.88)
    for x in (PW*.13,PW*.87):
        c.setFillColor(HexColor("#F5A8C8")); c.circle(x,PH*.34,8,fill=1,stroke=0)
        c.setFillColor(HexColor("#F8D66D")); c.circle(x,PH*.34,3.5,fill=1,stroke=0)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",default="dist/the-happy-little-train-print.pdf"); args=ap.parse_args()
    if len(PAGES)!=24: raise RuntimeError(f"Expected 24 pages; got {len(PAGES)}")
    f=Path("assets/fonts/NotoNaskhArabic.ttf")
    en=Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    if not f.exists() or not en.exists(): raise FileNotFoundError("Required fonts missing. Run the GitHub Actions workflow or install fonts as documented.")
    pdfmetrics.registerFont(TTFont("Arabic",str(f))); pdfmetrics.registerFont(TTFont("English",str(en)))
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    c=canvas.Canvas(str(out),pagesize=(PW,PH),pageCompression=1)
    c.setTitle("The Happy Little Train | قطار الألوان السعيد"); c.setAuthor("Original bilingual children's book project")
    c.setSubject("24-page Arabic-English interactive picture book")
    for n,(et,eb,at,ab,me,ma,kind) in enumerate(PAGES,1):
        scene(c,kind); left=BX+SAFE; width=PW-2*(BX+SAFE)
        if n==1:
            para(c,escape(et),left,PH*.91,width,"English",25,"#31536B")
            para(c,ar(escape(at)),left,PH*.84,width,"Arabic",26,"#31536B")
            para(c,escape(eb),left+.15*inch,PH*.24,width-.3*inch,"English",11,"#31536B")
            para(c,ar(escape(ab)),left+.15*inch,PH*.17,width-.3*inch,"Arabic",13,"#31536B")
        else:
            para(c,escape(et),left,PH*.91,width,"English",17,"#31536B")
            para(c,ar(escape(at)),left,PH*.84,width,"Arabic",19,"#31536B")
            para(c,escape(eb),left+.10*inch,PH*.265,width-.2*inch,"English",10.5,"#29485D",leading=14)
            para(c,ar(escape(ab)),left+.10*inch,PH*.205,width-.2*inch,"Arabic",12.5,"#29485D",leading=18)
            py=BY+SAFE*.48
            c.setFillColor(colors.Color(1,1,1,alpha=.90)); c.roundRect(left,py,width,.57*inch,10,fill=1,stroke=0)
            para(c,"Mom's Turn: "+escape(me),left+.12*inch,py+.48*inch,width-.24*inch,"English",7.1,"#526477",align=0,leading=9)
            para(c,ar("دور الأم: "+escape(ma)),left+.12*inch,py+.27*inch,width-.24*inch,"Arabic",8.2,"#526477",align=2,leading=11)
        c.setFillColor(HexColor("#526477")); c.setFont("English",7); c.drawCentredString(PW/2,BY+SAFE*.20,str(n)); c.showPage()
    c.save(); print(f"Created {out}: {len(PAGES)} pages; {PW/inch:.3f} x {PH/inch:.3f} inches")
if __name__=="__main__": main()
