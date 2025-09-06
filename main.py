import FreeSimpleGUI as sg
from PIL import *
import io
import requests

def decimal_coords(coords, ref):
    decimal_degrees = float(coords[0]) + float(coords[1]) / 60 + float(coords[2]) / 3600
    if ref == "S" or ref =='W' :
        decimal_degrees = -1 * decimal_degrees
    return decimal_degrees

GPSINFO_TAG = next(
    tag for tag, name in ExifTags.TAGS.items() if name == "GPSInfo"
)

def resize_image(image_path):
    img = Image.open(image_path)
    img = img.resize((800, 600), Image.Resampling.LANCZOS)
    return img

def filtro_neg(image):
    width, height = image.size
    img = image.copy()

    for i in range(width):
        for j in range(height):
            (r, g, b) = img.getpixel((i, j))  
            r = 255 - r
            g = 255 - g
            b = 255 - b
            img.putpixel((i, j), (r, g, b))  

    return img

def filtro_quatro_bits(image):
    img = image.copy()
    img = img.convert("P", palette=Image.ADAPTIVE, colors=4)

    return img

def filtro_blur(image):
    img = image.copy()
    radius = sg.popup_get_text("Digite a quantidade de blur que você quer aplicar (0 a 20):", default_text="2")
    radius = int(radius)
    radius = max(0, min(20, radius))
    img = img.filter(ImageFilter.GaussianBlur(radius))

    return img

def filtro_sepia(image):
    width, height = image.size
    img = image.copy()

    for i in range(width):
        for j in range(height):
            (r, g, b) = img.getpixel((i, j))  
            r = r + 120 if r + 120 < 255 else 255 
            g = g + 75 if g + 75 < 255 else 255
            b = b + 5 if b + 5 < 255 else 255

            img.putpixel((i, j), (r, g, b))  

    return img

def filtro_pb(image):
    width, height = image.size
    img = image.copy()

    for i in range(width):
        for j in range(height):
            rgb = img.getpixel((i, j))  
            r = int(0.3 * rgb[0])
            g = int(0.59 * rgb[1]) 
            b = int(0.11 * rgb[2])
            pb = r + g + b
            r = pb
            g = pb
            b = pb
            img.putpixel((i, j), (r, g, b))  

    return img
            
layout = [
    [sg.Menu([
        ['Arquivo', ['Abrir', 'Fechar', 'Mostrar Dados de GPS', 'Mostrar Dados da Imagem'], ['Ajuda',['Sobre']]],
        ['Editar', ['Desfazer']],
        ['Imagem', [
            'Girar', ['Girar 90° à Direita', 'Girar 90° à Esquerda'],
            'Filtro', ['Preto e Branco', 'Sépia', 'Negativo', '4 Bits', 'Blur', 'Contorno', 'Detalhe'
            'Realce de Bordas', 'Relevo', 'Detectar Bordas', 'Nitidez', 'Suavizar','Filtro Mínimo', 'Filtro Máximo'],
            'Histograma RGB']],
            ])],
    [sg.Image(key='-IMAGE-', size=(800, 600))],
]

window = sg.Window('Foto Shopping', layout, resizable=True, background_color='purple')

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == 'Fechar':
        break
    elif event == 'Abrir':
       file_path = sg.popup_get_file('Selecione uma imagem', file_types=(("Imagens", "*.jpg *.png"),))
       if file_path:
           resized_img = resize_image(file_path)
           img_bytes = io.BytesIO()
           resized_img.save(img_bytes, format='PNG')
           window['-IMAGE-'].update(data=img_bytes.getvalue())
    elif event == 'Mostrar Dados de GPS':
        path = r"IMG_0667 (SALVA).png"
        image = Image.open(path)
        info = image.getexif()

        gpsinfo = info.get_ifd(GPSINFO_TAG)

        lat = decimal_coords(gpsinfo[2], gpsinfo[1])
        lon = decimal_coords(gpsinfo[4], gpsinfo[3])

        print('Lat : {0}'.format(lat))
        print('Lon : {0}'.format(lon))

        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10&addressdetails=1"
        headers = {'User-Agent': 'FotoShoppingApp/1.0 (kaykebiscegli2005@gmail.com)'} 
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        address = data.get('address', {})
        estado = address.get('state', 'Não encontrado')
        pais = address.get('country', 'Não encontrado')

        sg.popup(f"Localização:\nEstado: {estado}\nPaís: {pais}", title="Dados de Localização")

    elif event == 'Mostrar Dados da Imagem':
        img = Image.open("IMG_0667 (SALVA).png")
        img.show("imagem")
        print(img.size)
        width, height = img.size
        print(width)
        print(height)
        print(img.filename)
        print(img.format)
        print(img.format_description)
    elif event == 'Sobre':
        sg.popup('Desenvolvido pelo BCC - 6° Semestre.\n\n Thyago Quintas')

    elif event == "Negativo":
        file_path = sg.popup_get_file('Selecione uma imagem', file_types=(("Imagens", "*.jpg *.png"),))
        if file_path:
            image = Image.open(file_path)
            img = filtro_neg(image)
            img.show()

    elif event == "Sépia":
        file_path = sg.popup_get_file('Selecione uma imagem', file_types=(("Imagens", "*.jpg *.png"),))
        if file_path:
            image = Image.open(file_path)
            img = filtro_sepia(image)
            img.show()

    elif event == "Preto e Branco":
        file_path = sg.popup_get_file('Selecione uma imagem', file_types=(("Imagens", "*.jpg *.png"),))
        if file_path:
            image = Image.open(file_path)
            img = filtro_pb(image)
            img.show()

    elif event == "4 Bits":
        file_path = sg.popup_get_file('Selecione uma imagem', file_types=(("Imagens", "*.jpg *.png"),))
        if file_path:
            image = Image.open(file_path)
            img = filtro_quatro_bits(image)
            img.show()

    elif event == "Blur":
        file_path = sg.popup_get_file('Selecione uma imagem', file_types=(("Imagens", "*.jpg *.png"),))
        if file_path:
            image = Image.open(file_path)
            img = filtro_blur(image)
            img.show()

window.close()