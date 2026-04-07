from setuptools import setup, find_packages

setup(
    name="analisis-math",
    version="1.0.0",
    description="Herramienta de análisis matemático de magnitudes armónicas",
    author="Gemini CLI",
    packages=find_packages(),
    py_modules=["main", "parse_csv", "explore", "fft_analysis", "hurst", "hilbert_analysis", 
                "fibonacci_analysis", "apoyo_stats", "correlation_analysis", 
                "scale_analysis", "contact_dynamics_analysis", "timeframe_comparison",
                "generate_master_reports", "generate_report", "generate_pdf_report", "plot_style"],
    install_requires=[
        "pandas",
        "matplotlib",
        "scipy",
        "numpy",
        "fpdf2",
    ],
    entry_points={
        "console_scripts": [
            "math-analisis=main:main",
        ],
    },
    python_requires=">=3.8",
)
