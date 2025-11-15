def setup_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📊 Мой профиль$"), show_profile))
    
    # Обработчики для онбординга - УПРОЩЕННАЯ ВЕРСИЯ
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_nko_name))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_nko_activity))