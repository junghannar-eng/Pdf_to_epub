import streamlit as st
import fitz  # PyMuPDF
from ebooklib import epub
import re

st.title("မြန်မာစာ PDF to EPUB ပြောင်းစက်")
st.write("စာကြောင်းတိုများ ကွဲထွက်နေမှုကို ပြင်ဆင်ပြီး စာပိုဒ်များအဖြစ် စနစ်တကျ ပေါင်းစပ်ပေးသော ဗားရှင်း။")

uploaded_file = st.file_uploader("PDF ဖိုင်ကို ရွေးချယ်ပါ", type="pdf")

if uploaded_file is not None:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if st.button("EPUB သို့ ပြောင်းမည်"):
        with st.spinner("စာအုပ်ကို စာပိုဒ်များအဖြစ် ပုံစံမှန်ကန်အောင် ပြင်ဆင်နေပါပြီ... ခေတ္တစောင့်ဆိုင်းပါ"):
            book = epub.EpubBook()
            book.set_identifier('my_epub_007')
            book_title = uploaded_file.name.replace(".pdf", "")
            book.set_title(book_title)
            book.set_language('my')
            
            doc = fitz.open("temp.pdf")
            full_text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                
                # ၁။ မလိုအပ်သော လိုင်းပြတ်များကို ဖယ်ရှားပြီး စာပိုဒ်ငယ်များအဖြစ် စုစည်းခြင်း
                # (စာကြောင်းတစ်ကြောင်းချင်း ပြတ်နေသည်များကို တစ်ဆက်တည်းဖြစ်စေရန် နေရာလွတ်ဖြင့် အစားထိုးခြင်း)
                paragraphs = text.split('\n\n')
                
                for p in paragraphs:
                    p_cleaned = p.replace('\n', ' ')
                    p_cleaned = re.sub(r'[ \t]+', ' ', p_cleaned).strip()
                    
                    if p_cleaned:
                        # ၂။ ထပ်နေသော သဝေထိုး၊ လုံးကြီးတင်၊ ရေးချ၊ ဝစ္စပေါက်များကို တစ်ခုတည်းဖြစ်အောင် ညှိခြင်း
                        duplicate_signs = ['\u102c', '\u102d', '\u102e', '\u102f', '\u1030', '\u1031', '\u1032', '\u1036', '\u1037', '\u1038', '\u103a']
                        for sign in duplicate_signs:
                            p_cleaned = p_cleaned.replace(sign + sign, sign)
                            p_cleaned = p_cleaned.replace(sign + ' ' + sign, sign)
                        
                        full_text += f"<p>{p_cleaned}</p>\n"
            
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
