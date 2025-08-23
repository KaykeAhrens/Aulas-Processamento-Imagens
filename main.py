import FreeSimpleGUI as sg
from PIL import ExifTags, Image
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

layout = [
    [sg.Menu([['Arquivo', ['Abrir', 'Fechar', 'Mostrar Dados de GPS', 'Mostrar Dados da Imagem']], ['Ajuda',['Sobre']]])],
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

window.close()
