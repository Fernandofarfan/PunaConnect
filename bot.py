import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, filters
from database import register_user, get_user, get_team_members, match_user

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
FULL_NAME, ROLE, MODALITY = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_message = (
        "¡Bienvenido a la Team1 Hackathon Salta! 🚀\n\n"
        "Soy el bot de matchmaking. Mi objetivo es ayudarte a encontrar un equipo de hasta 4 personas "
        "con perfiles complementarios.\n\n"
        "Comandos disponibles:\n"
        "/registro - Para registrarte o actualizar tu perfil.\n"
        "/match - Para buscar un equipo.\n"
        "/miequipo - Para ver con quién te tocó.\n"
    )
    await update.message.reply_text(welcome_message)

async def registro_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "¡Genial! Vamos a crear tu perfil.\n"
        "Por favor, envíame tu nombre completo o alias."
    )
    return FULL_NAME

async def registro_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['fullname'] = update.message.text
    
    keyboard = [
        [InlineKeyboardButton("Backend", callback_data="Backend"),
         InlineKeyboardButton("Frontend", callback_data="Frontend")],
        [InlineKeyboardButton("Smart Contracts/Web3", callback_data="Smart Contracts/Web3")],
        [InlineKeyboardButton("UX/UI", callback_data="UX/UI"),
         InlineKeyboardButton("Negocios/PM", callback_data="Negocios/PM")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "¿Cuál es tu rol principal?",
        reply_markup=reply_markup
    )
    return ROLE

async def registro_role(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    context.user_data['role'] = query.data
    
    keyboard = [
        [InlineKeyboardButton("Presencial en Salta", callback_data="Presencial en Salta")],
        [InlineKeyboardButton("Remoto", callback_data="Remoto")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"Rol seleccionado: {query.data}\nAhora, ¿cuál es tu modalidad de participación?",
        reply_markup=reply_markup
    )
    return MODALITY

async def registro_modality(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    modality = query.data
    fullname = context.user_data['fullname']
    role = context.user_data['role']
    
    user = query.from_user
    username = user.username if user.username else ""
    
    register_user(user.id, username, fullname, role, modality)
    
    await query.edit_message_text(
        f"¡Registro completado con éxito! 🎉\n\n"
        f"👤 Nombre: {fullname}\n"
        f"🛠 Rol: {role}\n"
        f"📍 Modalidad: {modality}\n\n"
        f"Ahora puedes usar /match para buscar un equipo."
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Registro cancelado. Usa /registro cuando estés listo.")
    return ConversationHandler.END

async def match(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user = get_user(user_id)
    
    if not user:
        await update.message.reply_text("Primero debes registrarte usando /registro.")
        return
        
    if user.team_id:
        await update.message.reply_text("Ya tienes un equipo asignado. Usa /miequipo para ver los integrantes.")
        return
        
    team = match_user(user_id)
    
    if team:
        await update.message.reply_text(
            "¡Hemos encontrado un equipo para ti! 🎉\n"
            "Usa /miequipo para ver a tus compañeros y ponerte en contacto con ellos."
        )
    else:
        await update.message.reply_text(
            "En este momento no hay suficientes usuarios sin equipo para formarlo. "
            "Por favor, intenta de nuevo más tarde."
        )

async def miequipo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user = get_user(user_id)
    
    if not user:
        await update.message.reply_text("Primero debes registrarte usando /registro.")
        return
        
    if not user.team_id:
        await update.message.reply_text("Aún no tienes equipo. Usa /match para buscar uno.")
        return
        
    members = get_team_members(user.team_id)
    
    msg = "🏆 *Tu Equipo:*\n\n"
    for member in members:
        contact = f"@{member.username}" if member.username else "Sin @usuario"
        msg += f"👤 {member.fullname} | 🛠 {member.role} | 📍 {member.modality} | 📞 {contact}\n"
        
    await update.message.reply_text(msg, parse_mode="Markdown")

def main() -> None:
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        logger.error("TELEGRAM_TOKEN no está configurado como variable de entorno.")
        return

    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("registro", registro_start)],
        states={
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, registro_name)],
            ROLE: [CallbackQueryHandler(registro_role)],
            MODALITY: [CallbackQueryHandler(registro_modality)],
        },
        fallbacks=[CommandHandler("cancelar", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("match", match))
    application.add_handler(CommandHandler("miequipo", miequipo))

    logger.info("Iniciando bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
