import glob, os

base = 'results'
txt_files = (
    glob.glob(f'{base}/*_explore_stats.txt') +
    glob.glob(f'{base}/*_hurst_valores.txt') +
    glob.glob(f'{base}/*_hilbert_resumen.txt') +
    glob.glob(f'{base}/*_apoyo_stats.txt') +
    glob.glob(f'{base}/*_correlation_stats.txt') +
    glob.glob(f'{base}/*_fft_ciclos.txt') +
    glob.glob(f'{base}/scale_*_table.txt') +
    glob.glob(f'{base}/*_fibonacci_stats.txt')
)

for f in sorted(txt_files):
    name = os.path.basename(f)
    with open(f, encoding='utf-8', errors='replace') as fh:
        content = fh.read()
    print(f'=== {name} ===')
    print(content[:3000])
    print()
