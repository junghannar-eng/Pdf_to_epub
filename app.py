import streamlit as st
import fitz  
from ebooklib import epub

st.title("မြန်မာစာ PDF to EPUB ပြောင်းစက်")
st.write("ဖုန်းမှ PDF တင်၍ EPUB ထုတ်ယူနိုင်ပါပြီ။")

uploaded_file = st.file_uploader("PDF ဖိုင်ကို ရွေးချယ်ပါ", type="pdf")

if uploaded_file is not None:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.button("EPUB သို့ ပြောင်းမည်"):
        with st.spinner("ပြောင်းလဲနေပါပြီ... ခေတ္တစောင့်ဆိုင်းပါ"):
            book = epub.EpubBook()
            book.set_identifier('id123456')
            book.set_title(uploaded_file.name.replace(".pdf", ""))
            book.set_language('my')

            doc = fitz.open("temp.pdf")
            chapters = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")

                chapter = epub.EpubHtml(title=f'စာမျက်နှာ {page_num + 1}', file_name=f'chap_{page_num + 1}.xhtml', lang='my')
                chapter.content = f'<html><body><p>{text.replace(chr(10), "<br>")}</p></body></html>'
                book.add_item(chapter)
                chapters.append(chapter)

            book.toc = tuple(chapters)
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())
            book.spine = ['nav'] + chapters

            output_file = "output.epub"
            epub.write_epub(output_file, book, {})

            st.success("ပြီးဆုံးပါပြီ!")
            with open(output_file, "rb") as f:
                st.download_button(
                    label="EPUB ဖိုင် ဒေါင်းလုဒ်လုပ်ရန်",
                    data=f,
                    file_name=uploaded_file.name.replace(".pdf", ".epub"),
                    mime="application/epub+zip"
                )
