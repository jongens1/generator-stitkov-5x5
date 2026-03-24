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
MARGIN_X = 0.5 * cm    # Bočný okraj (vycentrovanie 20cm na 21cm šírku)
MARGIN_Y = 2.35 * cm   # Horný okraj (vycentrovanie 25cm na 29.7cm výšku)

def generate_pdf(texts, barcode_w):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    page_w, page_h = A4

    def draw_sticker(c, x, y, text):
        # Jemný rámček štítku 5x5cm
        c.setLineWidth(0.1 * mm)
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.rect(x, y, STICKER_SIZE, STICKER_SIZE)

        # Čiarový kód (Podľa obrázka - MASÍVNY A VYSOKÝ)
        try:
            # Výška kódu zväčšená na 3.3 cm (zaberá väčšinu štítku)
            bc_h = 3.3 * cm
            bc = code128.Code128(text, barHeight=bc_h, barWidth=barcode_w)
            
            # Výpočet šírky a vycentrovanie
            bc_w = bc.width
            draw_x = x + (STICKER_SIZE - bc_w) / 2
            
            # Kód začína cca 1.2 cm od spodku, aby ostalo miesto na text
            bc.drawOn(c, draw_x, y + 1.2 * cm)
        except:
            pass

        # Text pod kódom (Väčší a umiestnený nižšie ako na fotke)
        c.setFont("Helvetica-Bold", 14) 
        c.setFillColorRGB(0, 0, 0)
        # Umiestnenie textu 5mm od spodného okraja štítku
        c.drawCentredString(x + STICKER_SIZE/2, y + 0.5 * cm, text)

    idx = 0
    while idx < len(texts):
        for r in range(ROWS):
            for col in range(COLUMNS):
                if idx >= len(texts):
                    break
                
                # Výpočet súradníc (zhora nadol)
                curr_x = MARGIN_X + (col * STICKER_SIZE)
                curr_y = page_h - MARGIN_Y - ((r + 1) * STICKER_SIZE)
                
                draw_sticker(c, curr_x, curr_y, texts[idx])
                idx += 1
            if idx >= len(texts): break
        c.showPage()
    
    c.save()
    buffer.seek(0)
    return buffer

# --- ROZHRANIE APP ---
st.title("🏷️ Generátor štítkov 5x5 cm")

# Počítadlo návštev
st.markdown("![Návštevy](https://hits.dwyl.com/jongens1/stitky-5x5-foto-style.svg)")

st.write("Vložte texty (Každý riadok = jeden štítok). Štýl rozloženia podľa fotografie.")

with st.sidebar:
    st.header("Nastavenia")
    # Upravený rozsah slideru pre lepšiu kontrolu nad širokými kódmi
    barcode_w = st.slider("Hustota čiar (šírka kódu)", 0.3, 1.2, 0.70, 0.01)
    st.info("Na jednu A4 sa zmestí 20 štítkov (4x5).")
    if st.button("Vymazať všetko"):
        st.rerun()

input_text = st.text_area("Zadajte texty (napr. A2--101608-L):", height=300)

if st.button("🚀 Vygenerovať PDF na tlač", type="primary"):
    if input_text.strip():
        texts = [x.strip() for x in re.split(r'[;\n]+', input_text) if x.strip()]
        pdf_buffer = generate_pdf(texts, barcode_w)
        st.success(f"✅ PDF pripravené ({len(texts)} štítkov)")
        st.download_button(
            label="⬇️ STIAHNUŤ PDF (A4)",
            data=pdf_buffer,
            file_name="stitky_5x5_foto.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("Najskôr vložte nejaký text!")
