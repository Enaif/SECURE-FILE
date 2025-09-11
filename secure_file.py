import streamlit as st
from pypdf import PdfReader, PdfWriter, constants
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from streamlit_lottie import st_lottie
import json
import io

st.set_page_config(page_title="🔐 PDF Crypto Shield", layout="wide")

# CSS Web3 / Crypto
st.markdown("""
<style>
body {
    background-color: #0a0a1f;
    color: #00fff0;
    font-family: 'Orbitron', 'Segoe UI', sans-serif;
}

h1 {
    color: #00fff0;
    text-align: center;
    font-family: 'Orbitron', sans-serif;
    font-size: 3rem;
    margin-bottom: 1rem;
    text-shadow: 0 0 10px #00fff0, 0 0 20px #00ffea;
}

.card {
    background: linear-gradient(145deg, #111126, #1a1a2e);
    padding: 1rem;
    border-radius: 20px;
    margin-bottom: 1rem;
    box-shadow: 0 0 30px rgba(0,255,240,0.3);
    border: 1px solid #00fff0;
}

.stButton>button {
    background: linear-gradient(90deg, #00fff0 0%, #00c6a0 100%);
    color: #000000;
    font-weight: bold;
    border-radius: 15px;
    padding: 0.7rem 1.5rem;
    font-family: 'Orbitron', sans-serif;
    transition: all 0.3s ease-in-out;
}
.stButton>button:hover {
    transform: scale(1.08);
    box-shadow: 0 0 20px #00fff0, 0 0 40px #00c6a0;
}

.stTextInput>div>input, .stColorPicker>div>input {
    background-color: #111126;
    color: #00fff0;
    border-radius: 12px;
    border: 1px solid #00fff0;
    padding: 0.5rem;
}

.css-1w2j7hf.edgvbvh3 {
    background: linear-gradient(90deg, #00fff0 0%, #00c6a0 100%);
}
</style>
""", unsafe_allow_html=True)

st.title("🔐 PDF Crypto Shield")

def load_lottie_file(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

# === Container avec 2 colonnes ===
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file = st.file_uploader("Choisir un fichier PDF", type="pdf")
    
    with col2:
        lottie_secure = load_lottie_file("animation.json")
        st_lottie(
            lottie_secure,
            speed=1,
            width=300,
            height=300,
            key="secure_animation"
        )

# === Partie principale de l'app en dessous du container ===
if uploaded_file:
    st.subheader("Comment voulez-vous sécuriser votre PDF ?")
    option_watermark = st.checkbox("Ajouter un Watermark")
    option_password = st.checkbox("Ajouter un mot de passe")
    option_restrict_copy = st.checkbox("Interdire le copier-coller / modification")

    if option_watermark:
        st.markdown("### Options Watermark")
        watermark_text = st.text_input("Texte du Watermark", value="CONFIDENTIEL")
        watermark_color = st.color_picker("Couleur du Watermark", "#00fff0")
        watermark_size = st.slider("Taille du texte", min_value=20, max_value=100, value=40)
        watermark_angle = st.slider("Angle de rotation", min_value=0, max_value=360, value=45)
        watermark_alpha = st.slider("Transparence", min_value=0.1, max_value=1.0, value=0.3)
        apply_pages = st.text_input("Pages à appliquer (ex: 1-3 ou laisser vide pour toutes)", value="")

    password = ""
    if option_password:
        st.markdown("### Mot de passe PDF")
        password = st.text_input("Entrer un mot de passe pour protéger le PDF", type="password")

    if st.button("🔒 Sécuriser le PDF"):
        reader = PdfReader(uploaded_file)
        writer = PdfWriter()

        def create_watermark(text, color, size, angle, alpha):
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            can.setFont("Helvetica-Bold", size)
            can.setFillColor(HexColor(color))
            can.setFillAlpha(alpha)
            can.saveState()
            can.translate(300, 400)
            can.rotate(angle)
            can.drawCentredString(0, 0, text)
            can.restoreState()
            can.save()
            packet.seek(0)
            return PdfReader(packet)

        if option_watermark:
            watermark = create_watermark(watermark_text, watermark_color, watermark_size, watermark_angle, watermark_alpha)
            total_pages = len(reader.pages)
            if apply_pages.strip():
                pages_to_apply = []
                for part in apply_pages.split(","):
                    if "-" in part:
                        start, end = map(int, part.split("-"))
                        pages_to_apply.extend(range(start-1, end))
                    else:
                        pages_to_apply.append(int(part)-1)
            else:
                pages_to_apply = list(range(total_pages))

        for i, page in enumerate(reader.pages):
            if option_watermark and i in pages_to_apply:
                page.merge_page(watermark.pages[0])
            writer.add_page(page)

        if option_password or option_restrict_copy:
            permissions = 0
            if not option_restrict_copy:
                permissions |= constants.UserAccessPermissions.PRINT
                permissions |= constants.UserAccessPermissions.MODIFY
                permissions |= constants.UserAccessPermissions.EXTRACT_TEXT_AND_GRAPHICS
            writer.encrypt(
                user_password=password if password else "",
                owner_password=password if password else None,
                use_128bit=True,
                permissions_flag=permissions
            )

        output_buffer = io.BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)

        st.success("✅ PDF sécurisé avec succès !")
        st.download_button(
            "📥 Télécharger le PDF sécurisé",
            data=output_buffer,
            file_name="document_securise.pdf",
            mime="application/pdf"
        )
