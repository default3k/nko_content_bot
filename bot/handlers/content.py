def setup_handlers(application):
    handler = ContentHandler()
    
    # Обработчики контента
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^🎯 Создать пост$"), handler.start_content_creation))
    application.add_handler(CallbackQueryHandler(handler.handle_post_type_selection, pattern="^post_type_"))
    application.add_handler(CallbackQueryHandler(handler.handle_create_more, pattern="^create_more$"))
    application.add_handler(CallbackQueryHandler(handler.handle_edit_profile, pattern="^edit_profile$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler.handle_topic_description))