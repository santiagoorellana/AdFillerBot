'''Esta clase permite obtener anuncios de revolico.com mediante el scraping de
las páginas de anuncios. El scraping no se hace navegando por los enlaces del sitio,
sino que se accede directamente a los anuncios por medio de su URL, la cual se crea
con el identificador del anuncio, por lo que para acceder al anuncio hay que conocer
su identificador. Para obtener los identificadores, se puede buscar manualmente en la
página o se puede buscar automáticamente a patir de un identificador base y luego irlo
incrementando para obtener los anuncios en orden de aparición. Esta implementación de
scraping no ejecuta ningún código script que exista en la página.
'''
__version__ = '1.0'
__author__ = 'Santiago A. Orellana Perez'
__created__ = '8/mayo/2022'
__tested__ = 'Python 3.10'

import requests
from bs4 import BeautifulSoup
import random
import time
import datetime
import json

URL_REVOLICO_BASE = 'https://www.revolico.com'

REVOLICO_CATEGORIES = ["compra-venta", "autos", "vivienda", "empleos", "servicios", "computadoras"]

REVOLICO_CATEGORIES_ID = {
    "0": "Todas las etiquetas de todas las categorías",
    "31": "Celulares/L\u00edneas/Accesorios",
    "32": "Reproductor MP3/MP4/IPOD",
    "33": "Reproductor DVD/VCD/DVR",
    "214": "Televisor",
    "34": "C\u00e1mara Foto/Video",
    "213": "Aire Acondicionado",
    "39": "Consola Videojuego/Juegos",
    "43": "Sat\u00e9lite",
    "35": "Electrodom\u00e9sticos",
    "36": "Muebles/Decoraci\u00f3n",
    "37": "Ropa/Zapato/Accesorios",
    "40": "Intercambio/Regalo",
    "41": "Mascotas/Animales",
    "42": "Divisas",
    "38": "Libros/Revistas",
    "211": "Joyas/Relojes",
    "217": "Antiguedades/Colecci\u00f3n",
    "219": "Implementos Deportivos",
    "221": "Arte",
    "44": "Otros",
    "30": "Compra / Venta",
    "121": "Carros",
    "122": "Motos",
    "215": "Bicicletas",
    "125": "Piezas/Accesorios",
    "124": "Alquiler",
    "123": "Mec\u00e1nico",
    "204": "Otros",
    "120": "Autos",
    "101": "Compra/Venta",
    "102": "Permuta",
    "103": "Alquiler a cubanos",
    "104": "Alquiler a extranjeros",
    "105": "Casa en la playa",
    "100": "Vivienda",
    "161": "Ofertas de empleo",
    "162": "Busco empleo",
    "160": "Empleos",
    "83": "Clases/Cursos",
    "71": "Inform\u00e1tica/Programaci\u00f3n",
    "72": "Pel\u00edculas/Series/Videos",
    "73": "Limpieza/Dom\u00e9stico",
    "74": "Foto/Video",
    "75": "Construcci\u00f3n/Mantenimiento",
    "76": "Reparaci\u00f3n Electr\u00f3nica",
    "77": "Peluquer\u00eda/Barber\u00eda/Belleza",
    "78": "Restaurantes/Gastronom\u00eda",
    "79": "Dise\u00f1o/Decoraci\u00f3n",
    "80": "M\u00fasica/Animaci\u00f3n/Shows",
    "81": "Relojero/Joyero",
    "220": "Gimnasio/Masaje/Entrenador",
    "82": "Otros",
    "70": "Servicios",
    "2": "PC de Escritorio",
    "3": "Laptop",
    "5": "Microprocesador",
    "4": "Monitor",
    "6": "Motherboard",
    "7": "Memoria RAM/FLASH",
    "8": "Disco Duro Interno/Externo",
    "9": "Chasis/Fuente",
    "11": "Tarjeta de Video",
    "12": "Tarjeta de Sonido/Bocinas",
    "13": "Quemador/Lector DVD/CD",
    "14": "Backup/UPS",
    "15": "Impresora/Cartuchos",
    "16": "Modem/Wifi/Red",
    "18": "Webcam/Microf/Aud\u00edfono",
    "19": "Teclado/Mouse",
    "216": "Internet/Email",
    "218": "CD/DVD Virgen",
    "20": "Otros",
    "1": "Computadoras"
    }

REVOLICO_CATEGORIES_URL = {
    "compra-venta":[
        "/compra-venta/celulares-lineas-accesorios",
        "/compra-venta/reproductor-mp3-mp4-ipod",
        "/compra-venta/reproductor-dvd-vcd-dvr",
        "/compra-venta/televisor",
        "/compra-venta/camara-foto-video",
        "/compra-venta/aire-acondicionado",
        "/compra-venta/consola-videojuego-juegos",
        "/compra-venta/satelite",
        "/compra-venta/electrodomesticos",
        "/compra-venta/muebles-decoracion",
        "/compra-venta/ropa-zapato-accesorios",
        "/compra-venta/intercambio-regalo",
        "/compra-venta/mascotas-animales",
        "/compra-venta/divisas",
        "/compra-venta/libros-revistas",
        "/compra-venta/joyas-relojes",
        "/compra-venta/antiguedades-coleccion",
        "/compra-venta/implementos-deportivos",
        "/compra-venta/arte",
        "/compra-venta/otros"
        ],
    "autos":[
        "/autos/carros",
        "/autos/motos",
        "/autos/bicicletas",
        "/autos/piezas-accesorios",
        "/autos/alquiler",
        "/autos/mecanico",
        "/autos/otros"
        ],
    "vivienda":[
        "/vivienda/compra-venta",
        "/vivienda/permuta",
        "/vivienda/alquiler-a-cubanos",
        "/vivienda/alquiler-a-extranjeros",
        "/vivienda/casa-en-la-playa"
        ],
    "empleos":[
        "/empleos/ofertas-de-empleo",
        "/empleos/busco-empleo"
        ],
    "servicios":[
        "/servicios/clases-cursos",
        "/servicios/informatica-programacion",
        "/servicios/peliculas-series-videos",
        "/servicios/limpieza-domestico",
        "/servicios/foto-video",
        "/servicios/construccion-mantenimiento",
        "/servicios/reparacion-electronica",
        "/servicios/peluqueria-barberia-belleza",
        "/servicios/restaurantes-gastronomia",
        "/servicios/diseno-decoracion",
        "/servicios/musica-animacion-shows",
        "/servicios/relojero-joyero",
        "/servicios/gimnasio-masaje-entrenador",
        "/servicios/otros"
        ],
    "computadoras":[
        "/computadoras/pc-de-escritorio",
        "/computadoras/laptop",
        "/computadoras/microprocesador",
        "/computadoras/monitor",
        "/computadoras/motherboard",
        "/computadoras/memoria-ram-flash",
        "/computadoras/disco-duro-interno-externo",
        "/computadoras/chasis-fuente",
        "/computadoras/tarjeta-de-video",
        "/computadoras/tarjeta-de-sonido-bocinas",
        "/computadoras/quemador-lector-dvd-cd",
        "/computadoras/backup-ups",
        "/computadoras/impresora-cartuchos",
        "/computadoras/modem-wifi-red",
        "/computadoras/webcam-microf-audifono",
        "/computadoras/teclado-mouse",
        "/computadoras/internet-email",
        "/computadoras/cd-dvd-virgen",
        "/computadoras/otros"
        ]
    }

# User Agent for headers
UA_IE = 'Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)'
UA_MOZILLA_MSIE = 'Mozilla/5.0 (compatible; MSIE 10.0; Macintosh; Intel Mac OS X 10_7_3; Trident/6.0)'
UA_INTERNET_EXPLORER = 'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; GTB7.4; InfoPath.2; SV1; .NET CLR 3.3.69573; WOW64; en-US)'
UA_OPERA = 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.8.131 Version/11.11'
UA_CHROME = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2'
UA_GOOGLE = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13'
UA_GOOGLE_CHROME = 'Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11'
UA_MOZILLA = 'Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1'
UA_MOZILLA_FF = 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0.1'
UA_SAFARI = 'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25'

# Los que me acepta revolico.com
UA_LIST = [UA_IE, UA_MOZILLA_MSIE, UA_INTERNET_EXPLORER, UA_OPERA, UA_SAFARI]

FILE_NAME_FOR_ID = './lastid.txt'

# Este ID de anuncio corresponde a la fecha base 8/11/2022 y puede ser actualizado
# manualmente para ayudar al algoritmo a encontrar anuncios mas recientes.
REVOLICO_BASE_ID = 41925759

SLEEP_TIMES = [1, 2, 3, 4, 5]

CHANGE_INCREMENT = 100

HOURS_FOR_OLD = 24

class ScraperRevolico():
    def __init__(self, maxHours=1, debugMode=True, fileName=None, revolicoAdID=None):
        self.debugMode = debugMode
        if fileName is None:
            self.fileName = FILE_NAME_FOR_ID
        else:
            self.fileName = fileName
        if revolicoAdID is None:
            self.revolicoAdID = self.id_from_file()
        else:
            self.revolicoAdID = revolicoAdID
        self.maxHours = maxHours
        self._increment = 1
        self._lastSuccessID = self.revolicoAdID
        self._maxNones = 10
        self._countNones = 0

    
    def show_message(self, msg):
        if self.debugMode:
            print(msg)


    def id_to_file(self, value):
        '''Este metodo escribe el valor pasado como parametro en un fichero local.
        Devuelve True si logra escribir el valor.
        '''
        try:
            fileOut = open(self.fileName, 'w')
            fileOut.write(str(value))
            fileOut.close()
            return True
        except Exception as e:
            self.show_message('ERROR writing ID file {}. {}'.format(self.fileName, str(e)))
            return False


    def id_from_file(self):
        '''Este metodo lee el un valor de la primera linea de un fichero local.
        Si no encuentra el ficehro, esta vacio o logra leerlo, devuelve REVOLICO_BASE_ID.
        '''
        try:
            fileIn = open(self.fileName, "r")
            line = fileIn.readline()
            fileIn.close()
            try:
                value = int(line)
                return value
            except Exception as e:
                self.show_message('ERROR reading value from ID file {}. {}'.format(self.fileName, str(e)))
                return REVOLICO_BASE_ID
        except Exception as e:
            self.show_message('ERROR reading ID file {}. {}'.format(self.fileName, str(e)))
            return REVOLICO_BASE_ID


    def scrape_page_ad(self, pageAsText):
        '''Recibe como texto una pagina de anuncio de revolico e intenta obtener los datos
        del anuncio que se encuentran en un JSON al final de la pagina. Si logra obtener los
        datos, los devuelve en una JSON, de lo contrario devuelve None.
        '''
        try:
            content = BeautifulSoup(pageAsText, 'html.parser')
            data = content.find_all(id='__NEXT_DATA__')
            dataAsJSON = json.loads(data[0].get_text())
            adTypeKey = 'AdType:{}'.format(dataAsJSON['props']['pageProps']['id'])
            apollo_state = dataAsJSON['props']['pageProps']['__APOLLO_STATE__']
            if adTypeKey in apollo_state:
                resultJSON = {}
                resultJSON['id'] = self.revolicoAdID
                resultJSON['viewCount'] = apollo_state[adTypeKey]['viewCount']
                resultJSON['permalink'] = apollo_state[adTypeKey]['permalink']
                resultJSON['phone'] = apollo_state[adTypeKey]['phone']
                resultJSON['title'] = apollo_state[adTypeKey]['title']
                resultJSON['price'] = apollo_state[adTypeKey]['price']
                resultJSON['currency'] = apollo_state[adTypeKey]['currency']
                resultJSON['name'] = apollo_state[adTypeKey]['name']
                resultJSON['status'] = apollo_state[adTypeKey]['status']
                resultJSON['isAuto'] = apollo_state[adTypeKey]['isAuto']
                resultJSON['updatedOnToOrder'] = apollo_state[adTypeKey]['updatedOnToOrder']
                resultJSON['updatedOnByUser'] = apollo_state[adTypeKey]['updatedOnByUser']
                try:
                    keyProvince = apollo_state[adTypeKey]['province']['__ref']
                    if keyProvince:
                        resultJSON['provinceID'] = apollo_state[keyProvince]['id']
                        resultJSON['provinceName'] = apollo_state[keyProvince]['name']
                except Exception as e:
                    pass
                try:
                    keyMunicipality = apollo_state[adTypeKey]['municipality']['__ref']
                    if keyMunicipality:
                        resultJSON['municipalityID'] = apollo_state[keyMunicipality]['id']
                        resultJSON['municipalityName'] = apollo_state[keyMunicipality]['name']
                except Exception as e:
                    pass
                try:
                    keySubcategory = apollo_state[adTypeKey]['subcategory']['__ref']
                    if keySubcategory:
                        resultJSON['subcategoryID'] = apollo_state[keySubcategory]['id']
                        resultJSON['subcategoryName'] = apollo_state[keySubcategory]['title']
                        try:
                            keyParentCategory = apollo_state[keySubcategory]['parentCategory']['__ref']
                            if keyParentCategory:
                                resultJSON['categoryID'] = apollo_state[keyParentCategory]['id']
                                resultJSON['categoryName'] = apollo_state[keyParentCategory]['title']
                        except:
                            pass
                except:
                    pass
                resultJSON['description'] = apollo_state[adTypeKey]['description']
                resultJSON['imagesCount'] = apollo_state[adTypeKey]['imagesCount']
                if int(resultJSON['imagesCount']) > 0:
                    try:
                        resultJSON['images'] = []
                        imagesList = apollo_state[adTypeKey]['images']['edges']
                        if imagesList:
                            for image in imagesList:
                                imageKey = image['node']['__ref']
                                images = {}
                                if 'high' in apollo_state[imageKey]['urls']:
                                    images['high'] = apollo_state[imageKey]['urls']['high']
                                if 'thumb' in apollo_state[imageKey]['urls']:
                                    images['thumb'] = apollo_state[imageKey]['urls']['thumb']
                                resultJSON['images'].append(images)
                    except:
                        pass
                return resultJSON
        except Exception as e:
            self.show_message('ERROR scraping page of ad {}. {}'.format(str(self.revolicoAdID), str(e)))
        return None


    def get_random_url(self, pageID):
        '''Devuelve una URl de revolico seleccionada de manera aleatoria.
        La URL se utiliza para hacer el pedido de una pagina a partir de su ID.
        No importar cual sea la URL, siempre devuelve la pagina que se le pide por ID.
        Esto solo se hace aleatorio para no hacer el pedido siempre desde una misma URL
        y asi evitar cualquier sobrecarga que sea rastreable en una misma URL.
        '''
        keyCategory = random.choice(REVOLICO_CATEGORIES)
        url = '{}{}/{}.html'.format(URL_REVOLICO_BASE, random.choice(REVOLICO_CATEGORIES_URL[keyCategory]), pageID)
        return url


    def get_page(self, pageID, userAgent=None):
        '''Pide la página del ID pasado en parametro y devuelve sus datos como JSON en 'ad'.
        Si la página del ID indicado no existe, entonces devuelve None en 'ad'.
        Si se produce un error, devuelve el tipo de error en 'error'.
        '''
        if userAgent is None:
            header = {'user-agent': random.choice(UA_LIST)}
        else:
            header = {'user-agent': userAgent}
        try:
            page = requests.get(self.get_random_url(pageID), headers=header)
            if page.status_code == 200:
                dataJSON = self.scrape_page_ad(page.content)
                if dataJSON is not None:
                    self.show_message(dataJSON)
                    # Calcula el tiempo en horas de la última actualización anuncio.
                    utc = datetime.datetime.utcnow()
                    dtOnByUser = datetime.datetime.strptime(dataJSON['updatedOnByUser'], "%Y-%m-%dT%H:%M:%S.%f%z")
                    dtOnToOrder = datetime.datetime.strptime(dataJSON['updatedOnToOrder'], "%Y-%m-%dT%H:%M:%S.%f%z")
                    deltaAsHoursOnByUser = (utc - dtOnByUser.replace(tzinfo=None)).total_seconds()/(60*60)
                    deltaAsHoursOnToOrder = (utc - dtOnToOrder.replace(tzinfo=None)).total_seconds()/(60*60)
                    deltaAsHours = abs(max([deltaAsHoursOnByUser, deltaAsHoursOnToOrder]))
                    # Conforma etiquetas con la categoría y subcategorías, eliminando redundancias y palabras innnecesarias.
                    words = '{}-{}'.format(dataJSON['subcategoryName'], dataJSON['categoryName']).lower()
                    words = words.replace('autos', 'transporte')
                    for string in ['/', ' a ', ' de ', ' en la ']:
                        words = words.replace(string, '-')
                    words = words.replace(' ', '-')
                    notShow = ['compra', 'venta', 'otros', 'servicios', 'empleo']
                    tags = [tag for tag in words.rsplit('-') if tag not in notShow and tag != '']
                    return {'ad':dataJSON, 'hours':deltaAsHours, 'tags':tags}
                else:
                    self.show_message('WARNING no ad page for ID {}'.format(pageID))
                    return {'ad':None}
            else:
                self.show_message('ERROR getting ad page. Type:{}'.format(page.status_code))
                return {'error':page.status_code}
        except Exception as e:
            self.show_message('ERROR getting ad page. Type:0 Msg:{}'.format(str(e)))
            return {'error':0}

        
    def get_next_page(self, useSleep=True, ignoreIfAuto=True, userAgent=None):
        '''Permite obtener la página siguiente sin tener que indicar el ID.
        Si la página del ID indicado se encuentra, devuelve sus datos como JSON en 'ad'.
        Si la página del ID indicado no existe, entonces devuelve None en 'ad'.
        Si se produce un error, devuelve el tipo de error en 'error'.
        '''
        result = self.get_page(self.revolicoAdID, userAgent)
        if 'ad' in result:
            if result['ad'] is not None:
                self._countNones = 0
                hoursOfAd = float(result['hours'])
                if hoursOfAd > self.maxHours:
                    # El anuncio tiene más horas de antiguedad que el máximo permitido.
                    # Hay que devolver el anuncio para seguir buscando otros anuncios más recientes.
                    self.show_message('INFO page {} has hours equal to {}'.format(self.revolicoAdID, round(hoursOfAd, 2)))
                    self._lastSuccessID = self.revolicoAdID
                    if not self.id_to_file(self._lastSuccessID):
                        self.show_message('WARNING ID not saved on file.')
                    self.revolicoAdID += int(self._increment)
                    self._increment = round(self._increment * random.choice([1.5, 1.6, 1.7, 1.8, 1.9, 2]))
                    self.show_message('DATA')
                    self.show_message(json.dumps(result, indent=4))
                    if ignoreIfAuto:
                        if result['ad']['isAuto'] == True:
                            return {'ad':None}
                    return result
                else:
                    # El anuncio se considera demasiado actual por lo que no se debe devolver ahora.
                    # No se debe incrementar el ID, pues el anuncio debe ser mostrado luego.
                    # Los siguientes incrementos deben realizarse
                    self._increment = int(1)
                    self.revolicoAdID = self._lastSuccessID + 1
                    return {'ad':None}
                
            elif result['ad'] is None:
                if self.revolicoAdID == self._lastSuccessID:
                    self.revolicoAdID = REVOLICO_BASE_ID + random.randint(0, 1000)
                elif self._countNones < self._maxNones:
                    # Asume que es un ID dentro del rango valido, pero que no tiene asignada una página.
                    # Agrega un nuevo None al contador de Nones para saber si vienen de forma consecutiva.
                    self.revolicoAdID += int(self._increment)
                    self._countNones += 1
                    return result
                else:
                    # Si ya son muchos Nones, entiende que no es casual, que el ID está
                    # fuera del rango y debe regresar al último ID conocido que estaba
                    # dentro del rango. Reinicia el contador de Nones consecutivos.
                    self.revolicoAdID = int(self._lastSuccessID)
                    self._countNones = 0
                    self._increment = int(1)
                    return result
        if useSleep:
            time.sleep(random.choice(SLEEP_TIMES))
        return result
        



#TEST CODE
def test_class():
    '''Esta funcion prueba el funcionamiento de la clase.'''
    revolico = ScraperRevolico(0.5, False)       # Crea la clase que raspa a revolico.com
    data = revolico.get_page(REVOLICO_BASE_ID)         # Para obtener una página por su ID.
    for n in range(10000):
        data = revolico.get_next_page()                # Para obtener páginas consecutivas.
        if data['ad'] is not None:
            print(json.dumps(data, indent=4))

#test_class()



