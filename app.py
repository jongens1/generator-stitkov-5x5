import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm, mm
from reportlab.graphics.barcode import code128
import io
import re

# --- KONFIGURÁCIA STRÁNKY ---
st.set_page_config(page_title="Generátor štítkov 5x5", layout="centered")

# --- PARAMETRE ŠTÍTKOV ---
STICKER_SIZE = 5 * cm  # 50mm
COLUMNS = 4            # 4 stĺpce = 20cm
ROWS = 5               # 5 riadkov = 25cm
MARGIN_X = 0.5 * cm    
MARGIN_Y = 2.35 * cm   

def generate_pdf(texts, barcode_w):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    page_h = A4[1]

    def draw_sticker(c, x, y, text):
        c.setLineWidth(0.1 * mm)
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.rect(x, y, STICKER_SIZE, STICKER_SIZE)
        try:
            bc_h = 1.5 * cm
            bc = code128.Code128(text, barHeight=bc_h, barWidth=barcode_w)
            bc_w = bc.width
            draw_x = x + (STICKER_SIZE - bc_w) / 2
            bc.drawOn(c, draw_x, y + 1.8 * cm)
        except:
            pass
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(x + STICKER_SIZE/2, y + 1 * cm, text)

    idx = 0
    while idx < len(texts):
        for r in range(ROWS):
            for col in range(COLUMNS):
                if idx >= len(texts): break
                curr_x = MARGIN_X + (col * STICKER_SIZE)
                curr_y = page_h - MARGIN_Y - ((r + 1) * STICKER_SIZE)
                draw_sticker(c, curr_x, curr_y, texts[idx])
                idx += 1
        c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

st.title("🏷️ Generátor štítkov 5x5 cm")
st.markdown("![Návštevy](https://hits.dwyl.com/jongens1/stitky-5x5-as-gen.svg)")
st.write("Vložte texty. Každý riadok = jeden štítok (A4, 20 štítkov na stranu).")

with st.sidebar:
    st.header("Nastavenia")
    barcode_w = st.slider("Hustota čiar (šírka kódu)", 0.3, 1.2, 0.7, 0.05)
    if st.button("Vymazať všetko"): st.rerun()

input_text = st.text_area("Zadajte texty pre štítky:", height=300)

if st.button("Pripraviť PDF na tlač", type="primary"):
    if input_text.strip():
        texts = [x.strip() for x in re.split(r'[;\n]+', input_text) if x.strip()]
        pdf_buffer = generate_pdf(texts, barcode_w)
        st.success(f"✅ PDF pripravené ({len(texts)} štítkov)")
        st.download_button(label="⬇️ STIAHNUŤ PDF (A4)", data=pdf_buffer, file_name="stitky_5x5.pdf", mime="application/pdf")
