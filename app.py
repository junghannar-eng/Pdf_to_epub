import streamlit as st
import fitz  # PyMuPDF
from ebooklib import epub
import re

st.title("မြန်မာစာ PDF to EPUB ပြောင်းစက်")
st.write("မြန်မာစာ စာလုံးကွဲထွက်နေမှုကို အထူးပြုပြင်ပေးသော ဗားရှင်း။")

uploaded_file = st.file_uploader("PDF ဖိုင်ကို ရွေးချယ်ပါ", type="pdf")

if uploaded_file is not None:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if st.button("EPUB သို့ ပြောင်းမည်"):
        with st.spinner("မြန်မာစာ စာလုံးများကို ပုံစံမှန်ကန်အောင် ပြင်ဆင်နေပါပြီ... ခေတ္တစောင့်ဆိုင်းပါ"):
            book = epub.EpubBook()
            book.set_identifier('my_epub_003')
            book_title = uploaded_file.name.replace(".pdf", "")
            book.set_title(book_title)
            book.set_language('my')
            
            doc = fitz.open("temp.pdf")
            full_text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                
                # မြန်မာစာလုံးများကြားရှိ မလိုအပ်သော နေရာလွတ်များကို ဖယ်ရှားပြီး ပေါင်းစပ်ခြင်း
                for _ in range(3):
                    text = re.sub(r'([\u1000-\u109F])\s+([\u1000-\u109F])', r'\1\2', text)
                
                cleaned_text = re.sub(r'\s+', ' ', text)
                full_text += f"<p>{cleaned_text}</p><br>"
            
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
