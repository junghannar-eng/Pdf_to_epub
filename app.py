import streamlit as st
import fitz  # PyMuPDF
from ebooklib import epub
import re

st.title("မြန်မာစာ PDF to EPUB ပြောင်းစက်")
st.write("အသတ်အညှပ် အပိုများ မပါဝင်ဘဲ၊ မူရင်းအဖြတ်အတောက်အတိုင်း သပ်ရပ်စွာ ပြောင်းလဲပေးသော ဗားရှင်း။")

uploaded_file = st.file_uploader("PDF ဖိုင်ကို ရွေးချယ်ပါ", type="pdf")

if uploaded_file is not None:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if st.button("EPUB သို့ ပြောင်းမည်"):
        with st.spinner("စာအုပ်ကို စနစ်တကျ ပြင်ဆင်နေပါပြီ... ခေတ္တစောင့်ဆိုင်းပါ"):
            book = epub.EpubBook()
            book.set_identifier('my_epub_final')
            book_title = uploaded_file.name.replace(".pdf", "")
            book.set_title(book_title)
            book.set_language('my')
            
            doc = fitz.open("temp.pdf")
            full_text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                # မူရင်း PDF ထဲက စာသားများကို ရယူခြင်း
                text = page.get_text("text")
                
                # ၁။ ဗျည်းနှင့် အသတ်အညှပ်များကြား နေရာလွတ် (Space) ဝင်နေပါက အလိုအလျောက် ပေါင်းစပ်ခြင်း
                text = re.sub(r'([\u1000-\u1021])\s+([\u102b-\u103e])', r'\1\2', text)
                
                # ၂။ နေရာလွတ် အပိုများကို ရှင်းလင်းခြင်း
                text = re.sub(r'[ \t]+', ' ', text)
                
                # ၃။ ထပ်နေသော ရေးချ၊ လုံးကြီးတင်၊ တစ်ချောင်းငင်၊ ဝစ္စပေါက် စသည်တို့ကို အတိအကျ ရှင်းလင်းခြင်း
                duplicate_signs = ['\u102b', '\u102c', '\u102d', '\u102e', '\u102f', '\u1030', '\u1031', '\u1032', '\u1036', '\u1037', '\u1038', '\u103a']
                for sign in duplicate_signs:
                    # ကပ်လျက် ထပ်နေသော အရာများ
                    text = text.replace(sign + sign, sign)
                    # ကြားတွင် နေရာလွတ်ခံပြီး ထပ်နေသော အရာများ
                    text = text.replace(sign + ' ' + sign, sign)
                    text = text.replace(sign + '  ' + sign, sign)
                
                # ၄။ မူရင်း PDF အတိုင်း အဖြတ်အတောက် (Lines/Phrases) များကို ထိန်းသိမ်းခြင်း
                # <p> ជំនួសឲ្យ <br> ကို အသုံးပြုခြင်းဖြင့် စာကြောင်းများကြား အလွန်အမင်း ကွာဟမှုကို တားဆီးသည်
                lines = text.split('\n')
                page_html = ""
                for line in lines:
                    line_cleaned = line.strip()
                    if line_cleaned:
                        # လိုင်းတစ်ကြောင်းချင်းစီတွင် ကျန်နေသေးသော အသတ်အညှပ် အပိုများကို ထပ်မံရှင်းလင်းခြင်း
                        for sign in duplicate_signs:
                            line_cleaned = line_cleaned.replace(sign + sign, sign)
                            line_cleaned = line_cleaned.replace(sign + ' ' + sign, sign)
                        
                        # လိုင်းဆင်းရန် <br/> ကို သုံးသည် (စာကြောင်းများ အကွာအဝေး အလွန်မကျယ်စေရန်)
                        page_html += f"{line_cleaned}<br/>\n"
                
                # စာမျက်နှာ တစ်ခုနှင့် တစ်ခုကြားတွင်သာ သပ်ရပ်စေရန် စာပိုဒ် (Paragraph) အဖြစ် ခွဲခြားပေးသည်
                if page_html:
                    full_text += f"<p style='margin-bottom: 1em; line-height: 1.6;'>{page_html}</p>\n"
            
            # EPUB အခန်းဖန်တီးခြင်း (CSS ဖြင့် စာကြောင်းအကွာအဝေးကို သဘာဝကျအောင် ထိန်းထားသည်)
            chapter = epub.EpubHtml(title=book_title, file_name='content.xhtml', lang='my')
            chapter.content = f"""
            <html>
            <head>
                <meta charset="utf-8"/>
                <style>
                    body {{ font-family: sans-serif; padding: 10px; }}
                    p {{ text-indent: 0; text-align: left; }}
                </style>
            </head>
            <body>{full_text}</body>
            </html>
            """
            book.add_item(chapter)
            
            book.toc = (chapter,)
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())
            book.spine = ['nav', chapter]
            
            output_file = "output.epub"
            epub.write_epub(output_file, book, {})
            
            st.success("ပြောင်းလဲခြင်း ပြီးဆုံးပါပြီ! အောက်ပါခလုတ်ဖြင့် ဒေါင်းလုဒ်လုပ်ပါ။")
            with open(output_file, "rb") as f:
                st.download_button(
                    label="EPUB ဖိုင် ဒေါင်းလုဒ်လုပ်ရန်",
                    data=f,
                    file_name=uploaded_file.name.replace(".pdf", ".epub"),
                    mime="application/epub+zip"
                )
