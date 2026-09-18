import streamlit as st
import fitz  # PyMuPDF
from ebooklib import epub
import re

st.title("မြန်မာစာ PDF to EPUB ပြောင်းစက်")
st.write("စာကြောင်းတိုများ မကွဲဘဲ မှန်ကန်သော အပိုင်းအခြားများနှင့် စာလုံးအမှန် ဖြစ်စေရန် ပြင်ဆင်ထားသော ဗားရှင်း။")

uploaded_file = st.file_uploader("PDF ဖိုင်ကို ရွေးချယ်ပါ", type="pdf")

if uploaded_file is not None:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if st.button("EPUB သို့ ပြောင်းမည်"):
        with st.spinner("စာအုပ်ကို စနစ်တကျ ပြင်ဆင်နေပါပြီ... ခေတ္တစောင့်ဆိုင်းပါ"):
            book = epub.EpubBook()
            book.set_identifier('my_epub_009')
            book_title = uploaded_file.name.replace(".pdf", "")
            book.set_title(book_title)
            book.set_language('my')
            
            doc = fitz.open("temp.pdf")
            full_text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                
                # ၁။ ဗျည်းနှင့် အသတ်အညှပ် (လုံးကြီးတင်၊ ရေးချ၊ ဝစ္စပေါက် စသည်) ကြားတွင် Space ပါနေပါက ပေါင်းစပ်ခြင်း
                text = re.sub(r'([\u1000-\u1021])\s+([\u102c-\u103a])', r'\1\2', text)
                
                # ၂။ ထပ်နေသော သဝေထိုး၊ လုံးကြီးတင်၊ ရေးချ၊ ဝစ္စပေါက်များကို တစ်ခုတည်းဖြစ်အောင် ဖယ်ရှားခြင်း
                duplicate_signs = ['\u102c', '\u102d', '\u102e', '\u102f', '\u1030', '\u1031', '\u1032', '\u1036', '\u1037', '\u1038', '\u103a']
                for sign in duplicate_signs:
                    text = text.replace(sign + sign, sign)
                    text = text.replace(sign + ' ' + sign, sign)
                    text = text.replace(sign + '  ' + sign, sign)
                
                # ၃။ မူရင်း PDF ပါ ဖွဲ့စည်းပုံအတိုင်း အပိုင်းလေးများ (Phrases/Lines) အဖြစ် ထိန်းသိမ်းခြင်း
                lines = text.split('\n')
                for line in lines:
                    line_cleaned = re.sub(r'[ \t]+', ' ', line).strip()
                    if line_cleaned:
                        # ထပ်မံ၍ လုံးကြီးတင်/ရေးချ ထပ်နေသည်များကို လိုင်းလိုက် ရှင်းလင်းခြင်း
                        for sign in duplicate_signs:
                            line_cleaned = line_cleaned.replace(sign + sign, sign)
                            line_cleaned = line_cleaned.replace(sign + ' ' + sign, sign)
                        
                        full_text += f"<p>{line_cleaned}</p>\n"
            
            chapter = epub.EpubHtml(title=book_title, file_name='content.xhtml', lang='my')
            chapter.content = f'<html><head><meta charset="utf-8"/></head><body>{full_text}</body></html>'
            book.add_item(chapter)
            
            book.toc = (chapter,)
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())
            book.spine = ['nav', chapter]
            
            output_file = "output.epub"
            epub.write_epub(output_file, book, {})
            
            st.success("ပြီးဆုံးပါပြီ! အောက်ပါခလုတ်ဖြင့် ဒေါင်းလုဒ်လုပ်ပါ။")
            with open(output_file, "rb") as f:
                st.download_button(
                    label="EPUB ဖိုင် ဒေါင်းလုဒ်လုပ်ရန်",
                    data=f,
                    file_name=uploaded_file.name.replace(".pdf", ".epub"),
                    mime="application/epub+zip"
                )
