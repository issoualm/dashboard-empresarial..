import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
from io import BytesIO
from matplotlib.backends.backend_pdf import PdfPages

# Estilo personalizado magenta + branco, detalhes turquesa/preto
custom_css = """
<style>
body {
    background-color: #d0008f;
}
h1, h2, h3, h4, h5, h6 {
    color: #ffffff;
}
.reportview-container {
    background-color: #d0008f;
    color: #ffffff;
}
.stButton>button {
    background-color: #ffffff;
    color: #000000;
    border-radius: 8px;
    padding: 8px 16px;
    border: 2px solid #40e0d0;
}
.stSelectbox, .stTextInput, .stFileUploader {
    background-color: #ffffff;
    color: #000000;
}
hr {
    border: 1px solid #40e0d0;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

st.set_page_config(page_title="Dashboard Empresarial", layout="wide")
st.title("📊 Dashboard Empresarial Inteligente")
st.write("Organize seus dados, visualize resultados e tome decisões com confiança.")

# Upload do Excel ou CSV
uploaded_file = st.file_uploader("📁 Envie sua planilha Excel ou CSV", type=["xlsx", "csv"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.header("📄 Visualização da Tabela")
    st.dataframe(df)

    st.markdown("---")
    colunas = df.columns.tolist()

    # Insights
    st.header("🧠 Insights Rápidos")
    if 'data' in [c.lower() for c in colunas]:
        try:
            df['data'] = pd.to_datetime(df[[c for c in colunas if 'data' in c.lower()][0]])
            df['mes'] = df['data'].dt.to_period("M")
            if 'vendas' in [c.lower() for c in colunas]:
                col_vendas = [c for c in colunas if 'vendas' in c.lower()][0]
                resumo = df.groupby("mes")[col_vendas].sum()
                st.success(f"Último mês ({resumo.index[-1]}): R${resumo.iloc[-1]:,.2f}")
        except:
            st.warning("Não foi possível gerar insights automáticos.")

    st.markdown("---")

    # Gráfico
    st.header("📊 Gráfico Personalizado")
    x = st.selectbox("Eixo X", colunas)
    y = st.selectbox("Eixo Y", colunas)
    tipo = st.selectbox("Tipo de gráfico", ["Barra", "Linha", "Pizza"])

    if st.button("Gerar Gráfico"):
        fig, ax = plt.subplots()
        if tipo == "Barra":
            sns.barplot(data=df, x=x, y=y, ax=ax, palette="rocket")
        elif tipo == "Linha":
            sns.lineplot(data=df, x=x, y=y, ax=ax, color="#40e0d0")
        elif tipo == "Pizza":
            dados = df.groupby(x)[y].sum()
            ax.pie(dados, labels=dados.index, autopct="%1.1f%%", colors=["#e75480", "#40e0d0", "#000000"])
            ax.axis("equal")
        st.pyplot(fig)

    st.markdown("---")

    # PDF
    def gerar_pdf(fig):
        pdf_buffer = BytesIO()
        with PdfPages(pdf_buffer) as pdf:
            pdf.savefig(fig)
        pdf_buffer.seek(0)
        return pdf_buffer

    if st.button("📥 Baixar PDF do gráfico"):
        fig, ax = plt.subplots()
        if tipo == "Barra":
            sns.barplot(data=df, x=x, y=y, ax=ax, palette="rocket")
        elif tipo == "Linha":
            sns.lineplot(data=df, x=x, y=y, ax=ax, color="#40e0d0")
        elif tipo == "Pizza":
            dados = df.groupby(x)[y].sum()
            ax.pie(dados, labels=dados.index, autopct="%1.1f%%", colors=["#e75480", "#40e0d0", "#000000"])
            ax.axis("equal")
        pdf_file = gerar_pdf(fig)
        st.download_button("📎 Baixar PDF", data=pdf_file, file_name="grafico.pdf", mime="application/pdf")
