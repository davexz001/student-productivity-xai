# styles.py — Shared CSS

SLIDER_CSS = """
<style>
    /* ===== SLIDERS — RED THEME ===== */
    .stSlider {
        padding-top: 6px !important;
        padding-bottom: 6px !important;
    }
    
    .stSlider .st-emotion-cache-igqoeg {
        background: #E2E8F0 !important;
        height: 6px !important;
        border-radius: 4px !important;
    }
    
    .stSlider .st-emotion-cache-igqoeg > div {
        background: #EF4444 !important;
        height: 6px !important;
        border-radius: 4px !important;
    }
    
    .stSlider .st-emotion-cache-igqoeg > div > div {
        background: #EF4444 !important;
        width: 18px !important;
        height: 18px !important;
        border-radius: 50% !important;
        border: 2px solid white !important;
        box-shadow: 0 2px 8px rgba(239, 68, 68, 0.5) !important;
        margin-top: -6px !important;
    }
    
    .stSlider .st-emotion-cache-igqoeg > div > div:hover {
        transform: scale(1.15) !important;
        box-shadow: 0 2px 12px rgba(239, 68, 68, 0.7) !important;
    }
    
    .stSlider .stMarkdown {
        font-size: 14px !important;
        color: #1E293B !important;
        font-weight: 500 !important;
        min-width: 28px !important;
        text-align: center !important;
    }
    
    .stSlider:focus-within {
        outline: none !important;
        box-shadow: none !important;
    }
</style>
"""