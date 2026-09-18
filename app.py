import streamlit as st
import fitz  # PyMuPDF
from ebooklib import epub
import pytesseract
from PIL import Image
import io
import re

st.title("မြန်မာစာ PDF to EPUB ပြောင်းစက် (OCR Version)")
st.write("PDF ထဲတွင် စာလုံးများ ကွဲနေပါက OCR စနစ်ဖြင့် စာပုံရိပ်ကို တိုက်ရိုက်ဖတ်ယူ၍ EPUB ပြောင်းပေးပါမည်။")

uploaded_file = st.file_uploader("PDF ဖိုင်ကို ရွေးချယ်ပါ", type="pdf")

if uploaded_file is not None:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if st.button("EPUB သို့ ပြောင်းမည်"):
        with st.spinner("OCR စနစ်ဖြင့် မြန်မာစာများကို တစ်မျက်နှာချင်း ဖတ်ယူနေပါသည်... (ခေတ္တစောင့်ဆိုင်းပါ)"):
            book = epub.EpubBook()
            book.set_identifier('my_epub_ocr')
            book_title = uploaded_file.name.replace(".pdf", "")
            book.set_title(book_title)
            book.set_language('my')
            
            doc = fitz.open("temp.pdf")
            full_text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # ၁။ စာမျက်နှာကို ရုပ်ပုံအဖြစ်ပြောင်းခြင်း (300 DPI)
                pix = page.get_pixmap(dpi=300)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                
                # ၂။ Tesseract OCR သုံးပြီး မြန်မာစာ စာသားကို တိုက်ရိုက်ဖတ်ယူခြင်း
                text = pytesseract.image_to_string(img, lang='mya')
                
                # ၃။ ပိုပိုလိုလို စာကြောင်းရှင်းလင်းခြင်း
                lines = text.split('\n')
                page_html = ""
                for line in lines:
                    cleaned = line.strip()
                    if cleaned:
                        page_html += f"{cleaned}<br/>\n"
                
                if page_html:
                    full_text += f"<div style='margin-bottom: 1.5em;'>{page_html}</div>\n"
            
            # EPUB ထုတ်လုပ်ခြင်း
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
            
            st.success("OCR ပြောင်းလဲခြင်း ပြီးဆုံးပါပြီ!")
            with open(output_file, "rb") as f:
                st.download_button(
                    label="EPUB ဖိုင် ဒေါင်းလုဒ်လုပ်ရန်",
                    data=f,
                    file_name=uploaded_file.name.replace(".pdf", ".epub"),
                    mime="application/epub+zip"
                )
