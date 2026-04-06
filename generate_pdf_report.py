"""
generate_pdf_report.py — Reporte PDF maestro de análisis histórico

Genera un PDF consolidado con TODOS los resultados del pipeline,
organizado por timeframe y análisis, con una sección final de
PARÁMETROS PARA EL INDICADOR listos para extraer manualmente.

Uso:
    python generate_pdf_report.py
    python generate_pdf_report.py --tf 1D 4H
    python generate_pdf_report.py --out mi_reporte.pdf

Requiere: pip install fpdf2
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
except ImportError:
    print("[ERROR] Falta la libreria fpdf2. Instalala con: pip install fpdf2")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
# RUTAS
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"
OUTPUT_DEFAULT = RESULTS_DIR / f"reporte_maestro_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

# Fuentes DejaVu incluidas con matplotlib (soporte Unicode completo)
_MPL_FONTS = (
    BASE_DIR / ".venv" / "Lib" / "site-packages" /
    "matplotlib" / "mpl-data" / "fonts" / "ttf"
)
FONT_REGULAR = str(_MPL_FONTS / "DejaVuSans.ttf")
FONT_BOLD    = str(_MPL_FONTS / "DejaVuSans-Oblique.ttf")   # no hay Bold; usamos Oblique como bold
FONT_MONO    = str(_MPL_FONTS / "DejaVuSansMono.ttf")
FONT_MONO_B  = str(_MPL_FONTS / "DejaVuSansMono-Bold.ttf")

# ─────────────────────────────────────────────────────────────────────────────
# COLORES (RGB)
# ─────────────────────────────────────────────────────────────────────────────
C_AZUL_OSCURO = (15, 40, 80)
C_AZUL        = (30, 80, 160)
C_AZUL_CLARO  = (200, 220, 255)
C_GRIS_OSCURO = (50, 50, 50)
C_GRIS_CLARO  = (240, 240, 245)
C_BLANCO      = (255, 255, 255)
C_NARANJA     = (200, 100, 0)
C_AMARILLO_BG = (255, 250, 220)

TF_LABEL = {"1D": "Diario (1D)", "4H": "4 Horas (4H)", "1H": "1 Hora (1H)"}


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def leer_txt(ruta):
    """Lee un .txt y devuelve el contenido como string. Vacío si no existe."""
    ruta = Path(ruta)
    if not ruta.exists():
        return ""
    try:
        return ruta.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


# ─────────────────────────────────────────────────────────────────────────────
# CLASE PDF
# ─────────────────────────────────────────────────────────────────────────────
class ReportePDF(FPDF):

    HEADER_H = 12   # altura de la banda del header en mm

    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(left=18, top=self.HEADER_H + 4, right=18)
        # Registrar fuentes Unicode (fpdf2 >= 2.5.1 infiere Unicode de .ttf automáticamente)
        self.add_font("DVS",  "",  FONT_REGULAR)
        self.add_font("DVS",  "B", FONT_BOLD)
        self.add_font("DVSM", "",  FONT_MONO)
        self.add_font("DVSM", "B", FONT_MONO_B)

    # ── Helpers de fuente ────────────────────────────────────────────────────
    def _normal(self, size=9):
        self.set_font("DVS", "", size)

    def _bold(self, size=9):
        self.set_font("DVS", "B", size)

    def _mono(self, size=7.5):
        self.set_font("DVSM", "", size)

    # ── Header / Footer ──────────────────────────────────────────────────────
    def header(self):
        if self.page_no() == 1:
            return
        # Banda azul oscuro de alto HEADER_H
        self.set_fill_color(*C_AZUL_OSCURO)
        self.rect(0, 0, 210, self.HEADER_H, "F")
        self.set_text_color(*C_BLANCO)
        self._bold(7)
        # Título centrado verticalmente en la banda
        y_txt = (self.HEADER_H - 6) / 2
        self.set_xy(18, y_txt)
        self.cell(0, 6, "ANÁLISIS DE MAGNITUDES ARMÓNICAS — REPORTE MAESTRO", align="L")
        self.set_xy(0, y_txt)
        self.cell(192, 6, f"Generado: {datetime.now().strftime('%Y-%m-%d')}", align="R")
        self.set_text_color(*C_GRIS_OSCURO)
        # Dejar el cursor justo debajo de la banda + 2mm de aire
        self.set_xy(self.l_margin, self.HEADER_H + 2)

    def footer(self):
        self.set_y(-14)
        self.set_draw_color(*C_AZUL)
        self.set_line_width(0.3)
        self.line(18, self.get_y(), 192, self.get_y())
        self._normal(7)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8,
                  f"Página {self.page_no()} — Este reporte describe el pasado, no predice el futuro.",
                  align="C")
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.2)

    # ── Portada ──────────────────────────────────────────────────────────────
    def portada(self, timeframes):
        self.add_page()
        self.set_fill_color(*C_AZUL_OSCURO)
        self.rect(0, 0, 210, 80, "F")

        self.set_text_color(*C_BLANCO)
        self._bold(26)
        self.set_xy(18, 20)
        self.cell(0, 12, "ANÁLISIS DE MAGNITUDES", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_x(18)
        self.cell(0, 12, "ARMÓNICAS", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self._normal(12)
        self.set_x(18)
        self.cell(0, 8, "Reporte Maestro de Parámetros para Indicador",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Banda timeframes
        self.set_fill_color(*C_AZUL)
        self.rect(0, 80, 210, 18, "F")
        self._bold(10)
        self.set_xy(18, 83)
        tfs_str = "  |  ".join([TF_LABEL.get(t, t) for t in timeframes])
        self.cell(0, 6, f"Timeframes analizados:  {tfs_str}",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_x(18)
        self._normal(9)
        self.cell(0, 6, f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

        # Descripción
        self.set_text_color(*C_GRIS_OSCURO)
        self.set_xy(18, 108)
        self._bold(11)
        self.cell(0, 7, "Para qué sirve este reporte",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_x(18)
        self._normal(10)
        self.multi_cell(
            174, 5.5,
            "Este reporte consolida todos los resultados del análisis histórico del patrón "
            "de oscilaciones entre el precio y las EMAs (10, 55, 200). "
            "El objetivo es que el trader lea este documento, extraiga los parámetros clave "
            "de la sección final 'PARÁMETROS PARA EL INDICADOR', y los ingrese manualmente "
            "como inputs en el indicador de Pine Script.\n\n"
            "Este documento describe comportamiento histórico. No predice el futuro. "
            "El trader decide — el indicador solo informa."
        )

        # Tabla de contenidos
        self.ln(6)
        self._bold(11)
        self.set_x(18)
        self.cell(0, 7, "Contenido", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        secciones = [
            ("1.", "Análisis Exploratorio (Explore)     — rangos históricos de cada variable"),
            ("2.", "Apoyos en EMAs                      — profundidad y tasa de rebote"),
            ("3.", "Ciclos Dominantes (FFT)             — duración en velas de cada ciclo"),
            ("4.", "Memoria de la Serie (Hurst)         — persistencia de las oscilaciones"),
            ("5.", "Ciclo Dinámico (Hilbert)            — amplitud y período en el tiempo"),
            ("6.", "Correlación entre Distancias        — sincronía y desfase"),
            ("7.", "Escala entre Correcciones           — relación de magnitudes entre EMAs"),
            ("8.", "Fibonacci                           — proporciones en tiempos y amplitudes"),
            ("9.", "PARÁMETROS PARA EL INDICADOR        — tabla lista para usar"),
        ]
        self._normal(9)
        for num, texto in secciones:
            self.set_x(22)
            self.set_text_color(*C_AZUL)
            self.cell(8, 6, num)
            self.set_text_color(*C_GRIS_OSCURO)
            self.cell(0, 6, texto, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.ln(4)
        self._caja_nota(
            "CÓMO USAR ESTE REPORTE\n"
            "1. Lee cada sección por timeframe (1D = visión general, 4H = entradas, 1H = precisión).\n"
            "2. Ve a la sección 9 'PARÁMETROS PARA EL INDICADOR'.\n"
            "3. Copia los valores numéricos en los inputs del indicador Pine Script.\n"
            "4. Repite este proceso mensualmente o cuando el mercado cambie de régimen."
        )

    # ── Separador de sección ─────────────────────────────────────────────────
    def titulo_seccion(self, numero, titulo, subtitulo=""):
        self.add_page()
        # La banda de sección va justo debajo del header
        y_sec = self.HEADER_H + 2
        self.set_fill_color(*C_AZUL_OSCURO)
        self.rect(0, y_sec, 210, 20, "F")
        self.set_text_color(*C_BLANCO)
        self._bold(14)
        self.set_xy(18, y_sec + 2)
        self.cell(0, 8, f"{numero}. {titulo.upper()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        if subtitulo:
            self.set_x(18)
            self._normal(9)
            self.cell(0, 5, subtitulo)
        self.set_text_color(*C_GRIS_OSCURO)
        self.set_xy(self.l_margin, y_sec + 20 + 4)

    # ── Encabezado de timeframe ──────────────────────────────────────────────
    def titulo_tf(self, tf):
        self.ln(3)
        self.set_fill_color(*C_AZUL)
        self.set_text_color(*C_BLANCO)
        self._bold(10)
        self.set_x(18)
        self.cell(174, 7, f"  Timeframe: {TF_LABEL.get(tf, tf)}", fill=True,
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*C_GRIS_OSCURO)
        self.ln(2)

    # ── Bloque de texto preformateado ────────────────────────────────────────
    def bloque_texto(self, texto, titulo_bloque=""):
        if titulo_bloque:
            self._bold(9)
            self.set_x(18)
            self.set_text_color(*C_AZUL)
            self.cell(0, 6, titulo_bloque, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_text_color(*C_GRIS_OSCURO)
        self.set_fill_color(*C_GRIS_CLARO)
        self._mono(7.5)
        for linea in texto.strip().split("\n"):
            if self.get_y() > 265:
                self.add_page()
            self.set_x(20)
            self.cell(172, 4.5, linea, fill=True,
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    # ── Imagen ───────────────────────────────────────────────────────────────
    def insertar_imagen(self, ruta, caption="", w=174):
        ruta = Path(ruta)
        if not ruta.exists():
            self._normal(8)
            self.set_text_color(150, 150, 150)
            self.set_x(18)
            self.cell(0, 6, f"[Imagen no encontrada: {ruta.name}]",
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_text_color(*C_GRIS_OSCURO)
            return
        try:
            self.image(str(ruta), x=18, w=w)
            if caption:
                self._normal(7.5)
                self.set_text_color(100, 100, 100)
                self.set_x(18)
                self.cell(0, 5, caption, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                self.set_text_color(*C_GRIS_OSCURO)
            self.ln(2)
        except Exception as e:
            self._normal(8)
            self.set_x(18)
            self.cell(0, 6, f"[Error cargando imagen: {ruta.name} — {e}]",
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── Tabla de parámetros ──────────────────────────────────────────────────
    def tabla_parametros(self, filas, encabezados, anchos):
        self.set_fill_color(*C_AZUL_OSCURO)
        self.set_text_color(*C_BLANCO)
        self._bold(8)
        self.set_x(18)
        for texto, ancho in zip(encabezados, anchos):
            self.cell(ancho, 6, texto, border=1, fill=True, align="C")
        self.ln()

        self.set_text_color(*C_GRIS_OSCURO)
        self._normal(7.5)
        fill = False
        for fila in filas:
            if self.get_y() > 265:
                self.add_page()
                self.set_fill_color(*C_AZUL_OSCURO)
                self.set_text_color(*C_BLANCO)
                self._bold(8)
                self.set_x(18)
                for texto, ancho in zip(encabezados, anchos):
                    self.cell(ancho, 6, texto, border=1, fill=True, align="C")
                self.ln()
                self.set_text_color(*C_GRIS_OSCURO)
                self._normal(7.5)
            self.set_fill_color(245, 245, 255) if fill else self.set_fill_color(*C_BLANCO)
            self.set_x(18)
            for celda, ancho in zip(fila, anchos):
                self.cell(ancho, 5.5, str(celda), border=1, fill=True)
            self.ln()
            fill = not fill
        self.ln(3)

    # ── Caja de nota ─────────────────────────────────────────────────────────
    def _caja_nota(self, texto, color_bg=C_AMARILLO_BG):
        self.set_fill_color(*color_bg)
        self.set_draw_color(*C_NARANJA)
        self.set_line_width(0.5)
        self._normal(8.5)
        self.set_text_color(*C_GRIS_OSCURO)
        # Dibujar línea por línea para compatibilidad
        lineas = texto.split("\n")
        for i, linea in enumerate(lineas):
            self.set_x(18)
            if len(lineas) == 1:
                borde = 1
            elif i == 0:
                borde = "TLR"
            elif i == len(lineas) - 1:
                borde = "BLR"
            else:
                borde = "LR"
            self.cell(174, 5.2, linea, border=borde, fill=True,
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_line_width(0.2)
        self.set_draw_color(0, 0, 0)
        self.ln(2)


# ─────────────────────────────────────────────────────────────────────────────
# PARSERS DE ARCHIVOS .txt
# ─────────────────────────────────────────────────────────────────────────────

def extraer_explore_params(tf, results_dir):
    txt = leer_txt(results_dir / f"explore_{tf}_stats.txt")
    params = {}
    if not txt:
        return params
    patrones = {
        "dist_p10_p5":   r"dist_p10:.*?p5/p95\s*=\s*([-\d.]+)",
        "dist_p10_p95":  r"dist_p10:.*?p5/p95\s*=\s*[-\d.]+\s*/\s*([\+\-\d.]+)",
        "dist_p10_p25":  r"dist_p10:.*?p25/p75\s*=\s*([-\d.]+)",
        "dist_p10_p75":  r"dist_p10:.*?p25/p75\s*=\s*[-\d.]+\s*/\s*([\+\-\d.]+)",
        "dist_p10_med":  r"dist_p10:.*?mediana\s*=\s*([\+\-\d.]+)",
        "dist_p55_p5":   r"dist_p55:.*?p5/p95\s*=\s*([-\d.]+)",
        "dist_p55_p95":  r"dist_p55:.*?p5/p95\s*=\s*[-\d.]+\s*/\s*([\+\-\d.]+)",
        "dist_p55_p25":  r"dist_p55:.*?p25/p75\s*=\s*([-\d.]+)",
        "dist_p55_p75":  r"dist_p55:.*?p25/p75\s*=\s*[-\d.]+\s*/\s*([\+\-\d.]+)",
        "dist_p55_med":  r"dist_p55:.*?mediana\s*=\s*([\+\-\d.]+)",
        "dist_p200_p5":  r"dist_p200:.*?p5/p95\s*=\s*([-\d.]+)",
        "dist_p200_p95": r"dist_p200:.*?p5/p95\s*=\s*[-\d.]+\s*/\s*([\+\-\d.]+)",
        "dist_p200_p25": r"dist_p200:.*?p25/p75\s*=\s*([-\d.]+)",
        "dist_p200_p75": r"dist_p200:.*?p25/p75\s*=\s*[-\d.]+\s*/\s*([\+\-\d.]+)",
        "dist_p200_med": r"dist_p200:.*?mediana\s*=\s*([\+\-\d.]+)",
        "ratio_mediana":  r"ratio_armonico.*?mediana\s*=\s*([\+\-\d.]+)",
    }
    for clave, patron in patrones.items():
        m = re.search(patron, txt, re.DOTALL)
        params[clave] = m.group(1) if m else "N/D"
    return params


def extraer_apoyo_params(tf, results_dir):
    txt = leer_txt(results_dir / f"apoyo_{tf}_stats.txt")
    params = {}
    if not txt:
        return params
    for ema, clave_base in [("EMA10", "p10"), ("EMA55", "p55"), ("EMA200", "p200")]:
        m = re.search(rf"Apoyo en {ema}.*?mediana\s*=\s*([-+\d.]+)%", txt, re.DOTALL)
        params[f"prof_med_{clave_base}"] = m.group(1) + "%" if m else "N/D"
        m2 = re.search(rf"Apoyo en {ema}.*?tasa.*?=\s*([\d.]+)%", txt, re.DOTALL)
        params[f"tasa_{clave_base}"] = m2.group(1) + "%" if m2 else "N/D"
        m3 = re.search(rf"Apoyo en {ema}.*?mediana rebote\s*=\s*([\+\-\d.]+)%", txt, re.DOTALL)
        params[f"rebote_med_{clave_base}"] = m3.group(1) + "%" if m3 else "N/D"
    return params


def extraer_fft_ciclo_dominante(tf, results_dir):
    txt = leer_txt(results_dir / f"fft_{tf}_ciclos.txt")
    params = {}
    if not txt:
        return params
    for var in ["dist_p10", "dist_p55", "dist_p200", "dist_10_55", "dist_55_200"]:
        m = re.search(rf"{var}:.*?#1\s+(\d+)\s+velas.*?\(([\d.]+)%", txt, re.DOTALL)
        params[f"ciclo1_{var}"] = f"{m.group(1)} v ({m.group(2)}%)" if m else "N/D"
    return params


def extraer_hurst(tf, results_dir):
    txt = leer_txt(results_dir / f"hurst_{tf}_valores.txt")
    params = {}
    if not txt:
        return params
    for var in ["dist_p10", "dist_p55", "dist_p200", "dist_10_55", "dist_55_200"]:
        m = re.search(rf"{var}:\s+H=([\d.]+)", txt)
        params[f"hurst_{var}"] = m.group(1) if m else "N/D"
    return params


def extraer_hilbert(tf, results_dir):
    txt = leer_txt(results_dir / f"hilbert_{tf}_resumen.txt")
    params = {}
    if not txt:
        return params
    for ema, clave in [("EMA10", "p10"), ("EMA55", "p55"), ("EMA200", "p200")]:
        m_amp = re.search(rf"{ema}.*?Amplitud media:\s*([\d.]+)%", txt, re.DOTALL)
        m_per = re.search(rf"{ema}.*?Per.*?odo mediana:\s*([\d.]+)\s*velas", txt, re.DOTALL)
        params[f"hilbert_amp_{clave}"]     = m_amp.group(1) + "%" if m_amp else "N/D"
        params[f"hilbert_periodo_{clave}"] = m_per.group(1) + " v" if m_per else "N/D"
    return params


def extraer_correlacion(tf, results_dir):
    txt = leer_txt(results_dir / f"correlation_{tf}_stats.txt")
    params = {}
    if not txt:
        return params
    m_r   = re.search(r"Pearson r\s*=\s*([\d.]+)", txt)
    m_lag = re.search(r"Lag.*?=\s*(-?\d+)\s*velas", txt)
    m_p   = re.search(r"Pendiente\s*=\s*([\d.]+)", txt)
    params["corr_r"]    = m_r.group(1) if m_r else "N/D"
    params["corr_lag"]  = m_lag.group(1) + " v" if m_lag else "N/D"
    params["corr_pend"] = m_p.group(1) if m_p else "N/D"
    return params


# ─────────────────────────────────────────────────────────────────────────────
# SECCIONES
# ─────────────────────────────────────────────────────────────────────────────

def seccion_explore(pdf, timeframes, results_dir):
    pdf.titulo_seccion("1", "Análisis Exploratorio (Explore)",
                       "Rangos históricos de cada variable — dónde 'vive' el precio respecto a las EMAs")
    pdf._caja_nota(
        "QUÉ BUSCAR AQUÍ:\n"
        "Los percentiles p5/p95 definen los extremos históricos — valores fuera son raros.\n"
        "Los percentiles p25/p75 definen la zona 'normal' de oscilación.\n"
        "La mediana cerca de 0 = la EMA sigue bien al precio. Alejada = tendencia persistente."
    )
    for tf in timeframes:
        pdf.titulo_tf(tf)
        txt = leer_txt(results_dir / f"explore_{tf}_stats.txt")
        pdf.bloque_texto(txt if txt else f"[No se encontró explore_{tf}_stats.txt]")
        for sufijo, caption in [
            ("distancias", "Serie temporal + histograma de distancias precio → EMA"),
            ("ratio",      "Serie temporal de dist_10_55, dist_55_200 y ratio_armónico"),
        ]:
            img = results_dir / f"explore_{tf}_{sufijo}.png"
            if img.exists():
                pdf.insertar_imagen(img, caption=caption, w=165)


def seccion_apoyos(pdf, timeframes, results_dir):
    pdf.titulo_seccion("2", "Apoyos en EMAs",
                       "Profundidad típica del apoyo y tasa de rebote posterior")
    pdf._caja_nota(
        "QUÉ BUSCAR AQUÍ:\n"
        "Profundidad mediana = hasta dónde llega típicamente el precio antes de rebotar.\n"
        "Tasa de éxito = % de veces que el precio subió en las siguientes 10 velas.\n"
        "Mediana de rebote = cuánto subió típicamente después del apoyo."
    )
    for tf in timeframes:
        pdf.titulo_tf(tf)
        txt = leer_txt(results_dir / f"apoyo_{tf}_stats.txt")
        pdf.bloque_texto(txt if txt else f"[No se encontró apoyo_{tf}_stats.txt]")
        for sufijo, caption in [
            ("detalle", "Serie histórica con apoyos marcados + histograma de profundidades"),
            ("rebote",  "Distribución del % de rebote N velas después, por EMA"),
        ]:
            img = results_dir / f"apoyo_{tf}_{sufijo}.png"
            if img.exists():
                pdf.insertar_imagen(img, caption=caption, w=165)


def seccion_fft(pdf, timeframes, results_dir):
    pdf.titulo_seccion("3", "Ciclos Dominantes (FFT)",
                       "Transformada de Fourier — duración de ciclos repetibles en velas")
    pdf._caja_nota(
        "QUÉ BUSCAR AQUÍ:\n"
        "> 10% de energía = ciclo muy dominante (el patrón sigue ese ritmo con fuerza).\n"
        "5-10% = ciclo relevante.  < 5% = posible ruido.\n"
        "Para convertir: 1D x velas = días.  4H x velas / 6 = días.  1H x velas / 24 = días."
    )
    for tf in timeframes:
        pdf.titulo_tf(tf)
        txt = leer_txt(results_dir / f"fft_{tf}_ciclos.txt")
        if txt:
            pdf.bloque_texto(txt)
        img = results_dir / f"fft_{tf}_espectro.png"
        if img.exists():
            pdf.insertar_imagen(img, caption="Espectro de potencia — picos = ciclos dominantes", w=165)


def seccion_hurst(pdf, timeframes, results_dir):
    pdf.titulo_seccion("4", "Memoria de la Serie (Hurst)",
                       "Exponente de Hurst — mide si las oscilaciones tienen persistencia o son aleatorias")
    pdf._caja_nota(
        "ESCALA DE H:\n"
        "H > 0.65  → Persistente fuerte  (la serie continúa su dirección — el patrón tiene inercia)\n"
        "H 0.55-0.65 → Persistente moderada\n"
        "H 0.45-0.55 → Casi aleatoria\n"
        "H < 0.45  → Anti-persistente (revierte rápidamente)\n\n"
        "NOTA: Se aplica a las DISTANCIAS, no al precio crudo."
    )
    for tf in timeframes:
        pdf.titulo_tf(tf)
        txt = leer_txt(results_dir / f"hurst_{tf}_valores.txt")
        if txt:
            pdf.bloque_texto(txt)
        img = results_dir / f"hurst_{tf}_rs.png"
        if img.exists():
            pdf.insertar_imagen(img, caption="Análisis R/S — la pendiente = exponente H", w=165)


def seccion_hilbert(pdf, timeframes, results_dir):
    pdf.titulo_seccion("5", "Ciclo Dinámico (Hilbert)",
                       "Transformada de Hilbert — amplitud y período instantáneo en el tiempo")
    pdf._caja_nota(
        "QUÉ BUSCAR AQUÍ:\n"
        "Amplitud media = magnitud típica de la oscilación en cada nivel de EMA.\n"
        "Período mediana = cuántas velas dura típicamente el ciclo.\n"
        "IQR del período amplio = el ciclo es variable (no constante en el tiempo)."
    )
    for tf in timeframes:
        pdf.titulo_tf(tf)
        txt = leer_txt(results_dir / f"hilbert_{tf}_resumen.txt")
        if txt:
            pdf.bloque_texto(txt)
        for sufijo, caption in [
            ("envolvente", "Amplitud instantánea de la oscilación a lo largo del tiempo"),
            ("frecuencia", "Período instantáneo (velas) — cuánto dura el ciclo en cada momento"),
        ]:
            img = results_dir / f"hilbert_{tf}_{sufijo}.png"
            if img.exists():
                pdf.insertar_imagen(img, caption=caption, w=165)


def seccion_correlacion(pdf, timeframes, results_dir):
    pdf.titulo_seccion("6", "Correlación entre Distancias",
                       "Sincronía y desfase entre dist_10_55 y dist_55_200")
    pdf._caja_nota(
        "QUÉ BUSCAR AQUÍ:\n"
        "r > 0.7 = correlación fuerte (las EMAs se mueven juntas).\n"
        "Lag óptimo negativo = dist_55_200 lidera a dist_10_55 (la EMA lenta va primero).\n"
        "Pendiente < 1 = la EMA rápida amortigua los movimientos de la lenta."
    )
    for tf in timeframes:
        pdf.titulo_tf(tf)
        txt = leer_txt(results_dir / f"correlation_{tf}_stats.txt")
        if txt:
            pdf.bloque_texto(txt)
        for sufijo, caption in [
            ("scatter", "Dispersión dist_10_55 vs dist_55_200 + línea de regresión"),
            ("ccf",     "Correlación cruzada por lag — el pico es el desfase óptimo"),
            ("rolling", "Correlación rodante — cómo cambia la sincronía en el tiempo"),
        ]:
            img = results_dir / f"correlation_{tf}_{sufijo}.png"
            if img.exists():
                pdf.insertar_imagen(img, caption=caption, w=165)


def seccion_escala(pdf, timeframes, results_dir):
    pdf.titulo_seccion("7", "Relaciones de Escala entre Correcciones",
                       "¿Las correcciones hacia EMA55 y EMA200 son múltiplos de las de EMA10?")
    pdf._caja_nota(
        "QUÉ BUSCAR AQUÍ:\n"
        "Se prueba si EMA55 ~ 2x EMA10, EMA200 ~ 3x EMA55, EMA200 ~ 6x EMA10, y proporciones áureas.\n"
        "CONFIRMADA = diferencia < 20%.  DÉBILMENTE = 20-30%.  NO CONFIRMADA = > 30%.\n"
        "Útil para saber si las correcciones escalan de forma predecible."
    )
    for tf in timeframes:
        pdf.titulo_tf(tf)
        txt_v = leer_txt(results_dir / f"scale_{tf}_validation.txt")
        txt_t = leer_txt(results_dir / f"scale_{tf}_table.txt")
        if txt_v:
            pdf.bloque_texto(txt_v, "Validación de hipótesis")
        if txt_t:
            pdf.bloque_texto(txt_t, "Tabla de ratios")
        for sufijo, caption in [
            ("ratios",    "Distribución de ratios entre magnitudes de correcciones"),
            ("evolution", "Evolución del ratio en el tiempo"),
        ]:
            img = results_dir / f"scale_{tf}_{sufijo}.png"
            if img.exists():
                pdf.insertar_imagen(img, caption=caption, w=165)


def seccion_fibonacci(pdf, timeframes, results_dir):
    pdf.titulo_seccion("8", "Análisis de Fibonacci",
                       "¿Los tiempos entre apoyos y amplitudes siguen proporciones áureas?")
    pdf._caja_nota(
        "QUÉ BUSCAR AQUÍ:\n"
        "Distancia < 0.05 a un nivel Fibonacci = el ratio está 'notablemente cerca' del nivel.\n"
        "Niveles a vigilar: 0.236, 0.382, 0.500, 0.618, 0.786, 1.000, 1.618.\n"
        "Pico en histograma en algún nivel Fib = muchos eventos ocurren en esa proporción."
    )
    for tf in timeframes:
        pdf.titulo_tf(tf)
        txt = leer_txt(results_dir / f"fibonacci_{tf}_stats.txt")
        if txt:
            pdf.bloque_texto(txt)
        for sufijo, caption in [
            ("tiempos",    "Distribución de ratios de tiempo entre apoyos vs niveles Fibonacci"),
            ("amplitudes", "Distribución de ratios de amplitud vs niveles Fibonacci"),
        ]:
            img = results_dir / f"fibonacci_{tf}_{sufijo}.png"
            if img.exists():
                pdf.insertar_imagen(img, caption=caption, w=165)


def seccion_parametros_indicador(pdf, timeframes, results_dir):
    pdf.titulo_seccion("9", "PARÁMETROS PARA EL INDICADOR",
                       "Tabla de valores históricos listos para ingresar en Pine Script")
    pdf._caja_nota(
        "CÓMO USAR ESTA SECCIÓN:\n"
        "1. Lee los valores de la columna del timeframe que usas como base (recomendado: 1D).\n"
        "2. Ingresa esos números como 'inputs' en el indicador de Pine Script.\n"
        "3. El indicador usará esos rangos para decirte en qué percentil histórico estás AHORA.\n"
        "4. Actualiza estos valores mensualmente o cuando el mercado cambie de régimen."
    )

    todos = {}
    for tf in timeframes:
        todos[tf] = {}
        todos[tf].update(extraer_explore_params(tf, results_dir))
        todos[tf].update(extraer_apoyo_params(tf, results_dir))
        todos[tf].update(extraer_fft_ciclo_dominante(tf, results_dir))
        todos[tf].update(extraer_hurst(tf, results_dir))
        todos[tf].update(extraer_hilbert(tf, results_dir))
        todos[tf].update(extraer_correlacion(tf, results_dir))

    grupos = [
        ("── RANGOS PRECIO vs EMA10 ──", [
            ("p5  dist_p10  (extremo inf.)",  ["dist_p10_p5"]),
            ("p25 dist_p10  (normal inf.)",   ["dist_p10_p25"]),
            ("Mediana dist_p10",               ["dist_p10_med"]),
            ("p75 dist_p10  (normal sup.)",   ["dist_p10_p75"]),
            ("p95 dist_p10  (extremo sup.)",  ["dist_p10_p95"]),
        ]),
        ("── RANGOS PRECIO vs EMA55 ──", [
            ("p5  dist_p55  (extremo inf.)",  ["dist_p55_p5"]),
            ("p25 dist_p55  (normal inf.)",   ["dist_p55_p25"]),
            ("Mediana dist_p55",               ["dist_p55_med"]),
            ("p75 dist_p55  (normal sup.)",   ["dist_p55_p75"]),
            ("p95 dist_p55  (extremo sup.)",  ["dist_p55_p95"]),
        ]),
        ("── RANGOS PRECIO vs EMA200 ──", [
            ("p5  dist_p200  (extremo inf.)", ["dist_p200_p5"]),
            ("p25 dist_p200  (normal inf.)",  ["dist_p200_p25"]),
            ("Mediana dist_p200",              ["dist_p200_med"]),
            ("p75 dist_p200  (normal sup.)",  ["dist_p200_p75"]),
            ("p95 dist_p200  (extremo sup.)", ["dist_p200_p95"]),
        ]),
        ("── APOYOS ──", [
            ("Profundidad típica EMA10",      ["prof_med_p10"]),
            ("Tasa éxito rebote EMA10",        ["tasa_p10"]),
            ("Rebote mediano EMA10",           ["rebote_med_p10"]),
            ("Profundidad típica EMA55",      ["prof_med_p55"]),
            ("Tasa éxito rebote EMA55",        ["tasa_p55"]),
            ("Rebote mediano EMA55",           ["rebote_med_p55"]),
            ("Profundidad típica EMA200",     ["prof_med_p200"]),
            ("Tasa éxito rebote EMA200",       ["tasa_p200"]),
            ("Rebote mediano EMA200",          ["rebote_med_p200"]),
        ]),
        ("── CICLOS DOMINANTES (FFT) ──", [
            ("Ciclo #1 dist_p10",             ["ciclo1_dist_p10"]),
            ("Ciclo #1 dist_p55",             ["ciclo1_dist_p55"]),
            ("Ciclo #1 dist_p200",            ["ciclo1_dist_p200"]),
            ("Ciclo #1 dist_10_55",           ["ciclo1_dist_10_55"]),
            ("Ciclo #1 dist_55_200",          ["ciclo1_dist_55_200"]),
        ]),
        ("── HURST (memoria) ──", [
            ("H  dist_p10",                   ["hurst_dist_p10"]),
            ("H  dist_p55",                   ["hurst_dist_p55"]),
            ("H  dist_p200",                  ["hurst_dist_p200"]),
        ]),
        ("── HILBERT (amplitud y período) ──", [
            ("Amplitud media  EMA10",         ["hilbert_amp_p10"]),
            ("Período mediana EMA10",         ["hilbert_periodo_p10"]),
            ("Amplitud media  EMA55",         ["hilbert_amp_p55"]),
            ("Período mediana EMA55",         ["hilbert_periodo_p55"]),
            ("Amplitud media  EMA200",        ["hilbert_amp_p200"]),
            ("Período mediana EMA200",        ["hilbert_periodo_p200"]),
        ]),
        ("── CORRELACIÓN dist_10_55 vs dist_55_200 ──", [
            ("Pearson r (sincrónica)",        ["corr_r"]),
            ("Lag óptimo",                    ["corr_lag"]),
            ("Pendiente de regresión",        ["corr_pend"]),
            ("Ratio armónico mediana",        ["ratio_mediana"]),
        ]),
    ]

    ancho_label = 70
    ancho_tf    = int((174 - ancho_label) / max(len(timeframes), 1))
    anchos      = [ancho_label] + [ancho_tf] * len(timeframes)
    encabezados = ["Parámetro"] + [TF_LABEL.get(t, t) for t in timeframes]

    for titulo_grupo, filas_grupo in grupos:
        pdf.set_fill_color(*C_AZUL_CLARO)
        pdf.set_text_color(*C_AZUL_OSCURO)
        pdf._bold(8)
        pdf.set_x(18)
        pdf.cell(174, 6, titulo_grupo, fill=True, border=1,
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(*C_GRIS_OSCURO)

        filas_tabla = []
        for label, claves in filas_grupo:
            fila = [label]
            for tf in timeframes:
                val = "N/D"
                for clave in claves:
                    v = todos.get(tf, {}).get(clave, "N/D")
                    if v and v != "N/D":
                        val = v
                        break
                fila.append(val)
            filas_tabla.append(fila)

        pdf.tabla_parametros(filas_tabla, encabezados, anchos)

    pdf.ln(4)
    pdf._caja_nota(
        "FÓRMULA DEL INDICADOR (referencia):\n\n"
        "  score_actual = (dist_pX_ahora - mediana_historica) / (p95 - p5)\n\n"
        "  score =  0  -> precio en su posición histórica típica respecto a esa EMA\n"
        "  score = +1  -> precio en el extremo superior histórico (muy extendido arriba)\n"
        "  score = -1  -> precio en el extremo inferior histórico (muy extendido abajo)\n\n"
        "Usa los valores de la tabla anterior para reemplazar mediana_historica, p95 y p5.",
        color_bg=(235, 245, 255)
    )


def seccion_comparativa(pdf, results_dir):
    pdf.titulo_seccion("10", "Comparativa Multi-Timeframe",
                       "Resumen consolidado 1D / 4H / 1H")
    txt_tab = leer_txt(results_dir / "comparison_table.txt")
    txt_sum = leer_txt(results_dir / "comparison_summary.md")
    if txt_tab:
        pdf.bloque_texto(txt_tab)
    if txt_sum:
        pdf.bloque_texto(txt_sum)
    for sufijo, caption in [
        ("radar",   "Radar de métricas clave por timeframe"),
        ("scaling", "Comparativa de escalas de corrección entre timeframes"),
    ]:
        img = results_dir / f"comparison_{sufijo}.png"
        if img.exists():
            pdf.insertar_imagen(img, caption=caption, w=165)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Genera el reporte PDF maestro con todos los resultados del análisis."
    )
    parser.add_argument(
        "--tf", nargs="+", default=None, metavar="TIMEFRAME",
        help="Timeframes a incluir. Ej: --tf 1D 4H  (por defecto: los que tengan archivos en results/)"
    )
    parser.add_argument(
        "--out", default=None, metavar="ARCHIVO.pdf",
        help=f"Nombre del PDF de salida (por defecto: {OUTPUT_DEFAULT.name})"
    )
    args = parser.parse_args()

    if args.tf:
        timeframes = args.tf
    else:
        timeframes = [tf for tf in ["1D", "4H", "1H"]
                      if (RESULTS_DIR / f"explore_{tf}_stats.txt").exists()]
        if not timeframes:
            print("[ERROR] No se encontraron archivos de resultados en results/")
            print("        Corre primero: python main.py --pasos explore")
            sys.exit(1)

    ruta_salida = Path(args.out) if args.out else OUTPUT_DEFAULT
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  Generando reporte PDF maestro")
    print("=" * 60)
    print(f"  Timeframes : {', '.join(timeframes)}")
    print(f"  Salida     : {ruta_salida}")
    print()

    pdf = ReportePDF()

    pasos = [
        ("Portada",                         lambda: pdf.portada(timeframes)),
        ("Explore — rangos históricos",      lambda: seccion_explore(pdf, timeframes, RESULTS_DIR)),
        ("Apoyos",                           lambda: seccion_apoyos(pdf, timeframes, RESULTS_DIR)),
        ("FFT — ciclos dominantes",          lambda: seccion_fft(pdf, timeframes, RESULTS_DIR)),
        ("Hurst — memoria",                  lambda: seccion_hurst(pdf, timeframes, RESULTS_DIR)),
        ("Hilbert — ciclo dinámico",         lambda: seccion_hilbert(pdf, timeframes, RESULTS_DIR)),
        ("Correlación",                      lambda: seccion_correlacion(pdf, timeframes, RESULTS_DIR)),
        ("Escala",                           lambda: seccion_escala(pdf, timeframes, RESULTS_DIR)),
        ("Fibonacci",                        lambda: seccion_fibonacci(pdf, timeframes, RESULTS_DIR)),
        ("Parámetros para el indicador",     lambda: seccion_parametros_indicador(pdf, timeframes, RESULTS_DIR)),
        ("Comparativa multi-timeframe",      lambda: seccion_comparativa(pdf, RESULTS_DIR)),
    ]

    for i, (nombre, fn) in enumerate(pasos, 1):
        print(f"  [{i:02d}/{len(pasos)}] {nombre}...")
        fn()

    try:
        pdf.output(str(ruta_salida))
        tam = ruta_salida.stat().st_size / 1024
        print()
        print("=" * 60)
        print("  PDF generado correctamente")
        print(f"  Archivo : {ruta_salida}")
        print(f"  Tamaño  : {tam:.1f} KB")
        print(f"  Páginas : {pdf.page}")
        print("=" * 60)
    except Exception as e:
        print(f"[ERROR] No se pudo guardar el PDF: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
