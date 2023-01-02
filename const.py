'''Cadenas de comandos, teclados, estados y variables del bot.'''
__version__ = '1.0'
__author__ = 'Santiago Orellana Perez'
__created__ = '10/mayo/2022'
__tested__ = 'Python 3.10'


# Emojis que se emplean para indicaciones y menus.
EMOJI_OK = '\U00002705'
EMOJI_ERROR = '\U0000274C'
EMOJI_WARNING = '\U00002757'
EMOJI_NONE = '\U00002716'
EMOJI_PAUSED = '\U000026AB'
EMOJI_RUNING = '\U0001F535'

# Emojis de los anuncios
EMOJI_TITLE = '\U0001F536\U0001F536\U0001F536'
EMOJI_PHONE = '\U0001F4DE'
EMOJI_NAME = '\U0001F464'
EMOJI_PRICE = '\U0001F4B0'
EMOJI_WHATSAPP = '\U0001F4AC'
EMOJI_LOCALIDAD = '\U0001F3E0'
EMOJI_TAG = '\U0001F4CC'

# Estados primarios del bot.
STATUS_RUNING = 3
STATUS_PAUSED = 4

COMMANDS = [
    {'name':'/start', 'root':False, 'description':['Inicia el bot.']},
    {'name':'/pause', 'root':False, 'description':['Detiene el envío de publicidad.']},
    {'name':'/continue', 'root':False, 'description':['Reanuda el envío de publicidad.']},
    {'name':'/restart', 'root':False, 'description':['Reinicia el bot y recarga datos desde ficheros.']},
    {'name':'/view', 'root':False, 'description':['Muestra la lista de receptores de publicidad.']},
    {'name':'/new receptor category', 'root':False, 'description':[
        'Agrega un nuevo receptor.',
        'El primer parámetro es el ID del usuario receptor o el enlace @nombre del grupo o canal al que se enviará la publicidad.',
        'El segundo parámetro es el nombre de la categoría de anuncios que se le debe enviar al receptor.',
        'Ejemplo: /new @setvmasinfo transporte'
        ]},
    {'name':'/del receptor', 'root':False, 'description':[
        'Elimina un receptor de publicidad.',
        'El parámetro es el ID del usuario receptor o el @nombre del grupo o canal al que se enviará la publicidad.',
        'Ejemplo: /del @setvmasinfo'
        ]},
    {'name':'/categories', 'root':False, 'description':['Muestra la lista de categorías de publicidad.']},
    {'name':'/admins', 'root':True, 'description':['Muestra la lista de administradores del bot.']},
    {'name':'/add userID', 'root':True, 'description':[
        'Agrega un nuevo administrador al bot.',
        'El primer parámetro es el ID del usuario que se agregará como administrador.',
        'El segundo parámetro es un nombre o alias del usuario.'
        'Ejemplo: /new @setvmasinfo transporte'
        ]},
    {'name':'/ban userID', 'root':True, 'description':[
        'Elimina un administrador del bot.',
        'El parámetro es el ID del usuario que dejará de ser administrador del bot.'
        ]},
    {'name':'/help', 'root':False, 'description':['Muestra la descripción de los comandos del bot.']},
    {'name':'/status', 'root':False, 'description':['Muestra el estado de funcionamiento del bot.']},
    {'name':'/send', 'root':False, 'description':[
        'Para enviar mensajes al administrador ROOT.',
        'El parámetro es el texto que se debe enviar al administrador ROOT.'
        ]}
    ]


# Contiene los nombres de las categorias que se utilizan en SetV+
# Los ID de revolico se utilizan para clasificar las subcategorias de revolico.com en categorias de SetV+
# Para cambiar las categorias, solo hay que mover los ID de revolico de una categoria SetV+ a otra.
SETVMAS_CATEGORIES = {
    'tecnologia':{
        'revolico_categories_id':[31, 32, 33, 34, 35, 39, 43, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12,
                                  13, 14, 15, 16, 18, 19, 20, 71, 76, 81, 213, 214, 216, 218]
        },
    'transporte':{
        'revolico_categories_id':[121, 122, 123, 124, 125, 204, 215]
        },
    'casas':{
        'revolico_categories_id':[101, 102, 103, 104, 105, 73, 75, 79, 36]
        },
    'servicios':{
        'revolico_categories_id':[71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 220]
        },
    'negocios':{
        'revolico_categories_id':[161, 162, 83, 42]
        },
    'viviendo':{
        'revolico_categories_id':[72, 74, 77, 78, 79, 80, 82, 40, 41, 37, 38, 44, 211, 217, 219, 220, 221]
        },
    'todos':{
        'revolico_categories_id':[0]  # Esto es para indicar que son todas las categorias.
        }
    }


SETVMAS_WORDS_EMOJIS = {
    'compra':'\U0001F6D2',
    'compro':'\U0001F6D2',
    'compram':'\U0001F6D2',
    'compramos':'\U0001F6D2',
    'venta':'\U0001F514',
    'vendo':'\U0001F514',
    'vende':'\U0001F514',
    'venden':'\U0001F514',
    'tengo':'\U0001F514',
    'busco':'\U0001F50D',
    'necesito':'\U0001F50D',
    'rebaja':'\U0001F525',
    'ganga':'\U0001F525',
    'remate':'\U0001F525',
    'new':'\U0001F195',
    '[new]':'\U0001F195',
    '(new)':'\U0001F195',
    'nuevo':'\U0001F195',
    'nueva':'\U0001F195',
    'nuevos':'\U0001F195',
    'nuevas':'\U0001F195',
    'original':'\U00002B50',
    'originales':'\U00002B50',
    'arreglamos':'\U0001F527',
    'reparacion':'\U0001F527',
    'reparación':'\U0001F527',
    'cambio':'\U0001F501',
    'cambia':'\U0001F501',
    'permuto':'\U0001F501',
    'permuta':'\U0001F501',
    'permutar':'\U0001F501'
    }

