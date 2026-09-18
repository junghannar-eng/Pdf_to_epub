import streamlit as st
import fitz  # PyMuPDF
from ebooklib import epub
import re

st.title("မြန်မာစာ PDF to EPUB ပြောင်းစက် (စာမျက်နှာအများကြီးအတွက်)")
st.write("OCR မလိုအပ်ဘဲ စာမျက်နှာ ရာပေါင်းများစွာကို စက္ကန့်ပိုင်းအတွင်း မြန်ဆန်စွာ ပြောင်းပေးမည့် စနစ်။")

def join_myanmar_broken_text(text):
    # ဗျည်းနှင့် အသတ်/သရ/ယပင့်/ရရစ် ကြားထဲမှ ခြားနေသော Spaces များကို အလိုအလျောက် ပေါင်းစပ်ခြင်း
    # အကြိမ်ကြိမ် စစ်ဆေး၍ စာလုံးများကို အမှန်အတိုင်း ပြန်ဆက်ပေးသည်
    for _ in range(5):
        text = re.sub(r'([\u1000-\u102a\u102b-\u103e\u103a])\s+([\u102b-\u103e\u103a\u103f])', r'\1\2', text)
        text = re.sub(r'(\u1039)\s+([\u1000-\u1021])', r'\1\2', text)
    
    # ပိုနေသော Space များနှင့် အသတ်အညှပ် အပိုများကို ရှင်းထုတ်ခြင်း
    text = re.sub(r'[ \t]+', ' ', text)
    signs = ['\u102b', '\u102c', '\u102d', '\u102e', '\u102f', '\u1030', '\u1031', '\u1032', '\u1036', '\u1037', '\u1038', '\u103a']
    for s in signs:
        text = text.replace(s + s, s)
    return text

uploaded_file = st.file_uploader("PDF ဖိုင်ကို ရွေးချယ်ပါ", type="pdf")

if uploaded_file is not None:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if st.button("EPUB သို့ ပြောင်းမည်"):
        with st.spinner("စာအုပ်တစ်အုပ်လုံးကို မြန်ဆန်စွာ ပြောင်းလဲနေပါသည်..."):
            book = epub.EpubBook()
            book.set_identifier('my_epub_fast')
            book_title = uploaded_file.name.replace(".pdf", "")
            book.set_title(book_title)
            book.set_language('my')
            
            doc = fitz.open("temp.pdf")
            full_text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                
                # စာလုံး ကွဲနေသည်များကို ပြန်ဆက်ခြင်း
                fixed_text = join_myanmar_broken_text(text)
                
                lines = fixed_text.split('\n')
                page_html = ""
                for line in lines:
                    cleaned = line.strip()
                    if cleaned:
                        page_html += f"{cleaned}<br/>\n"
                
                if page_html:
                    full_text += f"<div style='margin-bottom: 1.2em;'>{page_html}</div>\n"
            
            chapter = epub.EpubHtml(title=book_title, file_name='content.xhtml', lang='my')
            chapter.content = f"""
            <html>
            <head>
                <meta charset="utf-8"/>
                <style>
                    body {{ font-family: sans-serif; padding: 10px; line-height: 1.8; }}
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
            
            st.success("ပြောင်းလဲခြင်း အောင်မြင်စွာ ပြီးဆုံးပါပြီ!")
            with open(output_file, "rb") as f:
                st.download_button(
                    label="EPUB ဖိုင် ဒေါင်းလုဒ်လုပ်ရန်",
                    data=f,
                    file_name=uploaded_file.name.replace(".pdf", ".epub"),
                    mime="application/epub+zip"
                )
