'''Este bot para Telegram permite obtener anuncios de revolico.com mediante scraping de
las páginas de anuncios y los envía a canales, grupos y usuarios receptores de publicidad.
El scraping obtiene los anuncios más recientes y los embellece dándoles formato y agregándole emojis.
El bot tiene comandos útiles para ver la lista, agregar o quitar receptores o administradores.
El bot solo responde a los comandos del usuario ROOT y de los administradores agregados.
Los anuncios obtenidos, según su subcategoría,  son reclasificados.
Las listas de receptores y administradores se guardan en ficheros locales como txt.
'''

__version__ = '1.0'
__author__ = 'Santiago Orellana Perez'
__created__ = '13/mayo/2022'
__tested__ = 'Python 3.10'

from telegram import (ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, Update)
from telegram.ext import (Application, Updater, CommandHandler, MessageHandler, CallbackQueryHandler,
                          CallbackContext, ConversationHandler, filters, ContextTypes)
from telegram.constants import ChatAction
import datetime
import asyncio
import threading
from functools import wraps
from data_out import *
from const import *
from scraper_revolico import *


#-----------------------------------------------------------------------
# Constantes para configuracion basica.
#-----------------------------------------------------------------------

TOKEN = 'YOUR_TOKEN'
ADMIN_ROOT_ID = 715046259  #Santiago Orellana
FILE_RECEIVERS = './receivers.txt'
FILE_ADMINS = './admins.txt'

_scraper = None
_receivers = None
_admins = None

_bot_status = STATUS_PAUSED
_bot_submenu = ''


async def show_presentation(context):
    msg = f'{EMOJI_TITLE} <b>AdFillerBot</b> {EMOJI_TITLE}'
    await to_cmd('START', msg)
    msg = msg + f'\n\n{EMOJI_OK} Este bot se utiliza para enviar anuncios de forma masiva a grupos, canales y usuarios. '
    msg = msg + f'\n\n{EMOJI_OK} Para conocerlo utilice el comando /help'
    await show_message(context, ADMIN_ROOT_ID, msg)


async def get_argument(context, index, errorMessage, userID):
    '''Obtiene el argumento de la linea de comandos.'''
    try:
        return str(context.args[index])
    except:
        await context.bot.send_message(userID, errorMessage)
        return None


async def to_file(fileName, data):
    '''Crea un fichero nuevo y escribe los datos a la primera linea.'''
    try:
        fileOut = open(fileName, 'w')
        fileOut.write(data)
        fileOut.close()
        return True
    except Exception as e:
        await to_cmd('ERROR', 'to_file(): {}'.format(str(e)))
        return False


async def from_file(fileName):
    '''Lee los datos de la primera linea de un fichero.'''
    try:
        fileIn = open(fileName, "r")
        line = fileIn.readline()
        fileIn.close()
        return line
    except Exception as e:
        return None


#-----------------------------------------------------------------------
# Para establecer o quitar las tareas de trading que se ejecutan.
#-----------------------------------------------------------------------

async def job_execute_scraping(context) -> None:
    '''Execute the bot scraping and send ads messages.'''
    global _scraper
    global _bot_status
    global _receivers
    if _scraper:
        if _bot_status == STATUS_RUNING:
            await show_messages_ad(context, _receivers, _scraper.get_next_page()) 


async def job_set(context, jobName, jobSeconds, jobHandler):
    '''Agrega una nueva tarea en la cola de tareas. Se utiliza para ejecutar periódicamente el procesador de scraping.'''
    try:
        if context.job_queue.get_jobs_by_name(jobName):
            return False
        context.job_queue.run_repeating(jobHandler, jobSeconds, name=jobName)
        return True
    except Exception as e:
        await to_cmd('ERROR', 'on: job_set(): '.format(str(e)))
        return False


#-----------------------------------------------------------------------
# Controladores de comandos recibidos
#-----------------------------------------------------------------------

def check_user(func):
    '''Chequea que el usuario tenga permiso para utilizar la funcion.'''
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        try:
            cid = update.message.chat_id
            userID = update.effective_user.id
        except:
            return        
        if userID == ADMIN_ROOT_ID or userID in [admin['id'] for admin in _admins]:
            return await func(update, context, *args, **kwargs)
        else:
            await to_cmd('REJECTED', 'Usuario no autorizado: {}'.format(userID))
            await show_message(context, cid, 'No autorizado!')
            return 
    return wrapped


def send_action(action):
    '''Muestra una accion mientras se esta procesando el comando.'''
    def wrapped(func):
        @wraps(func)
        async def command_func(update, context, *args, **kwargs):
            await context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return await func(update, context,  *args, **kwargs)
        return command_func
    return wrapped


@send_action(ChatAction.TYPING)
@check_user
async def handler_start(update, context, restart=False):
    '''Muestra un mensaje de bienvenida y reinicia las variables del bot para que pueda ser utilizado.'''
    global _receivers
    global _bot_status
    if restart:
        await to_cmd('INFO', 'RESTART')
    else:
        await to_cmd('INFO', 'START')
    _bot_status = STATUS_RUNING
    
    # Intenta cargar la lista de receptores de publicidad.
    line = await from_file(FILE_RECEIVERS)
    if line is not None:
        try:
            _receivers = json.loads(line)
        except Exception as e:
            _receivers = []
            await to_cmd('WARNING', 'Failed to load Receivers List. {}'.format(str(e)))
    else:
        await to_cmd('INFO', 'No receivers assigned.')
        
    # Intenta cargar la lista de administradores.
    line = await from_file(FILE_ADMINS)
    if line is not None:
        try:
            _admins = json.loads(line)
        except Exception as e:
            _admins = []
            await to_cmd('WARNING', 'Failed to load Admins List. {}'.format(str(e)))
    else:
        await to_cmd('INFO', 'No admins assigned.')
        
    await job_set(context, 'job_execute_scraping', 10, job_execute_scraping)  
    await show_presentation(context)
    #await show_main_menu(update, context)


@check_user
async def handler_pause(update, context):
    global _bot_status
    _bot_status = STATUS_PAUSED
    await to_cmd('INFO', 'PAUSE')
    await show_message(context, ADMIN_ROOT_ID, f'{EMOJI_OK} Detenido temporalmente!')
    #await show_main_menu(update, context)


@check_user
async def handler_continue(update, context):
    '''Continua el funcionamiento del botpara obtener datos del exchange y hacer operaciones.'''
    global _bot_status
    _bot_status = STATUS_RUNING
    await to_cmd('INFO', 'CONTINUE')
    await show_message(context, ADMIN_ROOT_ID, f'{EMOJI_OK} Funcionando ahora!')
    #await show_main_menu(update, context)


@check_user
async def handler_restart(update, context):
    '''Reinicia el funcionamiento del bot para comenzar desde el inicio y recargar los parámetros y variables.'''
    global _bot_status
    if _bot_status == STATUS_RUNING:
        await handler_start(update, context, restart=True)


@send_action(ChatAction.TYPING)
@check_user
async def handler_view(update, context):
    '''Muestra los grupos, canales y usuarios que reciben la publicidad del bot.'''
    global _receivers
    userID = update.effective_user.id
    msg = f'{EMOJI_OK} Receptores de publicidad:\n'
    if _receivers is not None:
        if len(_receivers) > 0:
            msg = msg + '\nReceptor - Categoría'
            for receive in _receivers:
                try:
                    msg = msg + '\n{} - {}'.format(str(receive['id']), str(receive['category']))
                except Exception as e:
                    await to_cmd('ERROR', 'Error in ad receiver list. {}'.format(str(e)))
                    return
            await show_message(context, userID, msg)
            return
    await show_message(context, userID, f'{EMOJI_NONE} No se han establecido receptores de publicidad.')


@check_user
async def handler_new(update, context):
    '''Permite agregar un nuevo grupo, canal o usuario a la lista de receptores de publicidad.'''
    global _receivers
    userID = update.effective_user.id
    msg = f'{EMOJI_ERROR} Falta el primer parámetro: \nDebe indicar el link con @ de un grupo o canal o indicar el ID de un usuario.'
    receiver = await get_argument(context, 0, msg, userID)
    if receiver is None: return
    msg = f'{EMOJI_ERROR} Falta el segundo parámetro: \nDebe indicar un nombre de categoría. \nInfórmese con el comando /categories'
    category = await get_argument(context, 1, msg, userID)
    if category is None: return
    category = str(category).lower()
    if category in SETVMAS_CATEGORIES:
        _receivers.append({'id':receiver, 'category':category})
        await to_file(FILE_RECEIVERS, json.dumps(_receivers))
        await show_message(context, userID, f'{EMOJI_OK} Receptor establecido.')
    else:
        await show_message(context, userID, f'{EMOJI_ERROR} Esa categoría no existe o está mal escrita.')


@check_user
async def handler_del(update, context):
    '''Permite eliminar un grupo, canal o usuario de la lista de receptores de publicidad.'''
    global _receivers
    userID = update.effective_user.id
    msg = f'{EMOJI_ERROR} Falta el primer parámetro: \nDebe indicar el link con @ de un grupo o canal o indicar el ID de un usuario.'
    receiverID = await get_argument(context, 0, msg, userID)
    if receiverID is None: return
    _receivers = [element for element in _receivers if element['id'] != receiverID]
    await to_file(FILE_RECEIVERS, json.dumps(_receivers))
    await show_message(context, userID, f'{EMOJI_OK} Receptor eliminado.')


@send_action(ChatAction.TYPING)
@check_user
async def handler_help(update, context):
    '''Muestra la ayuda del bot.'''
    userID = update.effective_user.id
    msg = f'{EMOJI_OK}<b>Lista de comandos:</b>\n'
    for command in COMMANDS:
        if command['root'] and userID == ADMIN_ROOT_ID: continue
        msg = msg + '<b>{}</b> - {}\n'.format(command['name'], command['description'][0])
    await show_message(context, userID, msg)


@send_action(ChatAction.TYPING)
@check_user
async def handler_admins(update, context):
    '''Muestra la lista de administradores del bot.'''
    global _admins
    userID = update.effective_user.id
    msg = f'{EMOJI_OK} Administradores de publicidad:\n'
    if _admins is not None:
        if len(_admins) > 0:
            for admin in _admins:
                msg = msg + '\n{}'.format(str(admin))
            await show_message(context, userID, msg)
            return
    await show_message(context, userID, f'{EMOJI_NONE} No se han asignado administradores.')


@check_user
async def handler_add(update, context):
    '''Permite agregar un nuevo administrador.'''
    global _admins
    userID = update.effective_user.id
    newAdminID = await get_argument(context, 0, f'{EMOJI_ERROR} Falta el primer parámetro: \nDebe indicar el ID de un usuario.', userID)
    if newAdminID is None: return
    newAdminName = await get_argument(context, 1, f'{EMOJI_ERROR} Falta el segundo parámetro: \nDebe indicar un nombre para el administrador.', userID)
    if newAdminName is None: return
    _admins.append({'id':newAdminID, 'name':newAdminName})
    await to_file(FILE_ADMINS, json.dumps(_admins))
    await show_message(context, userID, f'{EMOJI_OK} Administrador establecido.')


@check_user
async def handler_ban(update, context):
    '''Permite eliminar un administrador.'''
    global _admins
    userID = update.effective_user.id
    adminID = await get_argument(context, 0, f'{EMOJI_ERROR} Falta un parámetro: \nDebe indicar el ID de un usuario.', userID)
    if adminID is None: return
    _admins = [admin for admin in _admins if admin['id'] != adminID]
    await to_file(FILE_ADMINS, json.dumps(_admins))
    await show_message(context, userID, f'{EMOJI_OK} Administrador eliminado.')


@send_action(ChatAction.TYPING)
@check_user
async def handler_categories(update, context):
    '''Muestra la lista de categorias publicitarias del bot.'''
    userID = update.effective_user.id
    msg = f'{EMOJI_OK} Categorías de publicidad disponibles:\n'
    if SETVMAS_CATEGORIES is not None:
        if len(SETVMAS_CATEGORIES) > 0:
            await show_message(context, userID, msg)
            for category in SETVMAS_CATEGORIES:
                msg = '\nCategoría: <b>{}</b>\n'.format(str(category))
                revolicoCategoriesID = SETVMAS_CATEGORIES[str(category)]['revolico_categories_id']
                if revolicoCategoriesID is not None:
                    if len(revolicoCategoriesID) > 0:
                        msg = msg + 'Etiquetas: '
                        for ID in revolicoCategoriesID:
                            msg = msg + str(REVOLICO_CATEGORIES_ID[str(ID)]).replace('/', ' ') + ' '
                await show_message(context, userID, msg)
            return
    await show_message(context, userID, f'{EMOJI_ERROR} No hay categorías.')


@check_user
async def handler_status(update, context):
    '''Le dice al usuario si el envío de mensajes está funcionando.'''
    global _bot_status
    userID = update.effective_user.id
    msg = f'{EMOJI_PAUSED} PAUSED \nNo se están enviando anuncios.'
    if _bot_status == STATUS_RUNING:
        msg = f'{EMOJI_RUNING} RUNING \nSe están enviando anuncios.'
    await show_message(context, userID, msg)


@check_user
async def handler_free_text(update, context) -> None:
    '''Este es el manejador principal que recibe todos los mensajes de texto que no sean comandos.'''
    text = update.message.text
    await handler_help(update, context)
    await to_cmd('INFO', text)


# Esto responde a cualquier usuario, para que puedan enviar su nombre.
async def handler_send(update, context):
    '''Para que los usuarios envien su nombre y obtener así tambien su ID.'''
    userID = update.effective_user.id
    name = await get_argument(context, 0, f'{EMOJI_ERROR} El parámetro del comando debe ser su nombre.', userID)
    if name is None: return
    await show_message(context, ADMIN_ROOT_ID, f'{EMOJI_NAME} Solicitud de administración:')
    await show_message(context, ADMIN_ROOT_ID, f'{userID} {name}')


async def error_handler(update, context):
    '''muestra las excepciones que se producen mientras se manejas las actualizaciones.'''
    await to_cmd('ERROR', 'Exception while handling an update: {}'.format(str(context.error)))


#-----------------------------------------------------------------------
# Este es el procedimiento principal, donde se ejecuta el bot.
#-----------------------------------------------------------------------
def main():
    global _scraper
    global _receivers
    global _admins
    print('>>> AdFiller Telegram Bot <<<')

    #Crea el scraper e inicia las variables globales.
    _scraper = ScraperRevolico(0.5, False)
    _receivers = []
    _admins = []

    #Crea la aplicacion del bot de telegram.
    application = Application.builder().token(TOKEN).build()

    #Manejadores para los comandos a los que responde el bot.
    application.add_handler(CommandHandler('start', handler_start))
    application.add_handler(CommandHandler('pause', handler_pause))
    application.add_handler(CommandHandler('continue', handler_continue))
    application.add_handler(CommandHandler('restart', handler_restart))
    application.add_handler(CommandHandler('view', handler_view))
    application.add_handler(CommandHandler('new', handler_new))
    application.add_handler(CommandHandler('del', handler_del))
    application.add_handler(CommandHandler('categories', handler_categories))
    application.add_handler(CommandHandler('admins', handler_admins))
    application.add_handler(CommandHandler('add', handler_add))
    application.add_handler(CommandHandler('ban', handler_ban))
    application.add_handler(CommandHandler('help', handler_help))
    application.add_handler(CommandHandler('status', handler_status))
    application.add_handler(CommandHandler('sendname', handler_send))
    
    #Recibe todos los textos y debe ser declarado despues de los otros controladores.
    application.add_handler(MessageHandler(filters.TEXT, handler_free_text))

    #Add the error handler
    application.add_error_handler(error_handler)

    #Comienza el bot y lo deja a la escucha de comandos.
    try:
        application.run_polling(poll_interval=1, timeout=20)
    except Exception as e:
        sync_to_file_cmd('ERROR', 'Connection error: {}'.format(str(e)))
        sync_to_file_cmd('CRITICAL', 'The application could not be started.')
        return


if __name__ == '__main__':
    main()


