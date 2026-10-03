from PIL import Image
import sys

try:
    img = Image.open('logo.jpg')
    # Generar tamaños estándar para que Windows lo visualice con nitidez en barra de tareas, explorador y ventana
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save('logo.ico', sizes=sizes)
    print("Icono creado exitosamente con múltiples resoluciones.")
except Exception as e:
    print(f"Error: {e}")

