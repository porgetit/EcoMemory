"""
EcoMemory - Punto de entrada PyWebView
Ejecutar con: python app.py
"""
import os
import webview
from api import EcoMemoryAPI

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    api = EcoMemoryAPI(base_dir)

    window = webview.create_window(
        title='EcoMemory',
        url=os.path.join(base_dir, 'index.html'),
        js_api=api,
        width=1280,
        height=800,
        min_size=(800, 600),
        resizable=True,
    )

    webview.start(debug=False)
