"""
plot_style.py — Paleta y funciones de estilo compartidas por todos los scripts
"""
BG_FIG = 'white'
BG_AX  = '#f7f9fc'
C_ZERO = '#888888'
C_POS  = '#1565c0'   # azul — relleno positivo
C_NEG  = '#e53935'   # rojo — relleno negativo

COLORS = {
    'dist_p10':   '#1565c0',
    'dist_p55':   '#e65100',
    'dist_p200':  '#2e7d32',
    'dist_10_55': '#6a1b9a',
    'dist_55_200':'#c62828',
    'ratio':      '#f57f17',
    'precio':     '#37474f',
    'hurst':      '#00695c',
    'envolvente': '#212121',
    'fibonacci':  '#f9a825',
}

def estilo_ax(ax, xlabel='', ylabel='', title=''):
    """Aplica estilo uniforme legible (fondo claro, texto oscuro)."""
    ax.set_facecolor(BG_AX)
    ax.tick_params(labelsize=8, colors='#222222')
    ax.xaxis.label.set_color('#333333')
    ax.yaxis.label.set_color('#333333')
    ax.title.set_color('#111111')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for spine in ax.spines.values():
        spine.set_color('#cccccc')
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=9)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=9)
    if title:
        ax.set_title(title, fontsize=10, fontweight='bold', pad=6)
