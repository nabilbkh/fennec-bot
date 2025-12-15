import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import json
from datetime import datetime

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# قاعدة بيانات مؤقتة (في الإنتاج استخدم قاعدة بيانات حقيقية)
users_db = {}
courses_db = {}
teachers_db = {}
marketplace_db = {}

# ================== بيانات المنصة ==================

EDUCATION_LEVELS = {
    'primary': {
        'name': '📖 الطور الابتدائي',
        'description': 'من السنة الأولى إلى الخامسة ابتدائي',
        'courses': 580,
        'teachers': 145
    },
    'middle': {
        'name': '📐 الطور المتوسط',
        'description': 'من السنة الأولى إلى الرابعة متوسط + تحضير BEM',
        'courses': 820,
        'teachers': 235
    },
    'high': {
        'name': '🎓 الطور الثانوي',
        'description': 'جميع الشعب + تحضير البكالوريا BAC',
        'courses': 1200,
        'teachers': 420
    },
    'university': {
        'name': '🏛️ التعليم الجامعي',
        'description': 'جميع التخصصات الجامعية',
        'courses': 2500,
        'teachers': 680
    }
}

SUBJECTS = {
    'math': '🔢 الرياضيات',
    'physics': '⚛️ الفيزياء',
    'arabic': '📚 اللغة العربية',
    'french': '🇫🇷 اللغة الفرنسية',
    'english': '🇬🇧 اللغة الإنجليزية',
    'history': '📜 التاريخ والجغرافيا',
    'science': '🔬 العلوم الطبيعية',
    'islamic': '☪️ التربية الإسلامية',
    'economy': '💰 العلوم الاقتصادية',
    'philosophy': '🤔 الفلسفة'
}

SUBSCRIPTION_PLANS = {
    'basic': {
        'name': 'الخطة الأساسية',
        'price': 990,
        'features': [
            '50 درس شهريًا',
            'امتحانات أساسية',
            'دعم عبر البريد',
            'شهادات إلكترونية'
        ]
    },
    'premium': {
        'name': 'الخطة الشاملة',
        'price': 1990,
        'features': [
            'دروس غير محدودة',
            'جميع الامتحانات',
            'حصص مباشرة',
            'دعم فوري',
            'خصومات السوق'
        ]
    },
    'teacher': {
        'name': 'خطة الأستاذ',
        'price': 0,
        'features': [
            'قناة تعليمية خاصة',
            'دروس فيديو غير محدودة',
            'حصص مباشرة',
            'عمولة 15%'
        ]
    }
}

# ================== دوال المساعدة ==================

def get_user(user_id):
    """جلب بيانات المستخدم"""
    return users_db.get(user_id, None)

def save_user(user_id, data):
    """حفظ بيانات المستخدم"""
    users_db[user_id] = data
    logger.info(f"تم حفظ بيانات المستخدم: {user_id}")

def get_main_keyboard(user_type='student'):
    """لوحة المفاتيح الرئيسية"""
    if user_type == 'teacher':
        keyboard = [
            ['📚 دروسي', '👥 طلابي'],
            ['💰 أرباحي', '📊 إحصائياتي'],
            ['⚙️ الإعدادات', 'ℹ️ المساعدة']
        ]
    else:
        keyboard = [
            ['📖 الدروس', '🎓 المراحل التعليمية'],
            ['🛒 السوق الأكاديمي', '📋 الامتحانات'],
            ['👨‍🏫 الأساتذة', '💳 اشتراكي'],
            ['⚙️ الإعدادات', 'ℹ️ المساعدة']
        ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ================== معالجات الأوامر ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر البداية /start"""
    user = update.effective_user
    user_id = user.id
    
    welcome_text = f"""
🦊 مرحبًا بك في *أكاديمية الفنك*
*FENNEC ACADEMY*

أهلاً {user.first_name}! 👋

منصة التعليم الجزائرية الشاملة 🇩🇿
من الابتدائي إلى الجامعة في مكان واحد!

📚 *ما نقدمه:*
✅ دروس لجميع المراحل التعليمية
✅ أساتذة محترفون
✅ امتحانات تفاعلية
✅ سوق أكاديمي للمواد الدراسية
✅ شهادات معتمدة

من فضلك، اختر نوع حسابك:
"""
    
    keyboard = [
        [InlineKeyboardButton("👨‍🎓 طالب", callback_data='register_student')],
        [InlineKeyboardButton("👨‍🏫 أستاذ", callback_data='register_teacher')],
        [InlineKeyboardButton("ℹ️ معلومات أكثر", callback_data='info')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر المساعدة"""
    help_text = """
📖 *دليل استخدام أكاديمية الفنك*

*الأوامر المتاحة:*
/start - البداية والتسجيل
/courses - عرض الدروس المتاحة
/teachers - قائمة الأساتذة
/marketplace - السوق الأكاديمي
/exams - الامتحانات
/subscribe - خطط الاشتراك
/profile - ملفي الشخصي
/help - المساعدة

*للطلاب:*
📚 تصفح الدروس حسب المرحلة
📋 حل الامتحانات والاختبارات
🛒 شراء المواد من السوق
👨‍🏫 متابعة الأساتذة المفضلين

*للأساتذة:*
📹 رفع الدروس والفيديوهات
💰 كسب المال من الاشتراكات
📊 متابعة الإحصائيات
👥 إدارة الطلاب

للدعم: @FennecAcademySupport
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأزرار"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    # التسجيل كطالب
    if data == 'register_student':
        user_data = {
            'type': 'student',
            'name': query.from_user.first_name,
            'registration_date': datetime.now().isoformat(),
            'level': None,
            'subscription': None,
            'points': 0,
            'courses_completed': 0
        }
        save_user(user_id, user_data)
        
        text = """
✅ *تم التسجيل بنجاح كطالب!*

الآن اختر مرحلتك التعليمية:
"""
        keyboard = [
            [InlineKeyboardButton("📖 ابتدائي", callback_data='level_primary')],
            [InlineKeyboardButton("📐 متوسط", callback_data='level_middle')],
            [InlineKeyboardButton("🎓 ثانوي", callback_data='level_high')],
            [InlineKeyboardButton("🏛️ جامعي", callback_data='level_university')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    
    # التسجيل كأستاذ
    elif data == 'register_teacher':
        user_data = {
            'type': 'teacher',
            'name': query.from_user.first_name,
            'registration_date': datetime.now().isoformat(),
            'specialization': None,
            'students_count': 0,
            'courses_count': 0,
            'earnings': 0,
            'rating': 0
        }
        save_user(user_id, user_data)
        
        text = """
✅ *تم التسجيل بنجاح كأستاذ!*

مرحبًا بك في فريق الأساتذة! 👨‍🏫

*مميزاتك:*
📹 رفع دروس فيديو غير محدودة
💰 كسب المال من اشتراكات الطلاب
📊 إحصائيات مفصلة
🎯 عمولة 15% على كل اشتراك

اختر تخصصك:
"""
        keyboard = [
            [InlineKeyboardButton("🔢 رياضيات", callback_data='spec_math')],
            [InlineKeyboardButton("⚛️ فيزياء", callback_data='spec_physics')],
            [InlineKeyboardButton("📚 عربية", callback_data='spec_arabic')],
            [InlineKeyboardButton("🇫🇷 فرنسية", callback_data='spec_french')],
            [InlineKeyboardButton("📜 أخرى", callback_data='spec_other')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    
    # اختيار المرحلة التعليمية
    elif data.startswith('level_'):
        level = data.replace('level_', '')
        user = get_user(user_id)
        if user:
            user['level'] = level
            save_user(user_id, user)
            
            level_info = EDUCATION_LEVELS[level]
            text = f"""
✅ *تم اختيار: {level_info['name']}*

{level_info['description']}

📚 عدد الدروس: {level_info['courses']}
👨‍🏫 عدد الأساتذة: {level_info['teachers']}

يمكنك الآن البدء بالتعلم! 🎓
استخدم القائمة أدناه للتصفح:
"""
            await query.edit_message_text(text, parse_mode='Markdown')
            await context.bot.send_message(
                chat_id=user_id,
                text="اختر من القائمة:",
                reply_markup=get_main_keyboard('student')
            )
    
    # اختيار التخصص للأستاذ
    elif data.startswith('spec_'):
        spec = data.replace('spec_', '')
        user = get_user(user_id)
        if user:
            user['specialization'] = spec
            save_user(user_id, user)
            
            text = f"""
✅ *تم حفظ تخصصك!*

يمكنك الآن البدء برفع الدروس والمحاضرات 📹

*خطواتك القادمة:*
1️⃣ ارفع أول درس فيديو
2️⃣ حدد سعر الاشتراك لقناتك
3️⃣ ابدأ في كسب المال! 💰

استخدم القائمة أدناه:
"""
            await query.edit_message_text(text, parse_mode='Markdown')
            await context.bot.send_message(
                chat_id=user_id,
                text="لوحة التحكم:",
                reply_markup=get_main_keyboard('teacher')
            )
    
    # معلومات أكثر
    elif data == 'info':
        text = """
📱 *عن أكاديمية الفنك*

منصة تعليمية جزائرية رائدة تهدف لربط الطلاب بأفضل الأساتذة وتوفير محتوى تعليمي عالي الجودة.

*🎯 رؤيتنا:*
جعل التعليم الجزائري متاحًا للجميع عبر التكنولوجيا

*📊 إحصائياتنا:*
• 5,250+ درس ومحاضرة
• 1,480+ أستاذ محترف
• 25,000+ طالب مسجل
• 98% نسبة رضا المستخدمين

*💳 الدفع:*
نستخدم Mastercard للدفع الآمن والسريع

📧 تواصل معنا:
info@fennecacademy.dz
"""
        keyboard = [
            [InlineKeyboardButton("🚀 ابدأ الآن", callback_data='register_student')],
            [InlineKeyboardButton("🔙 رجوع", callback_data='back_start')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def courses_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض الدروس المتاحة"""
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    if not user:
        await update.message.reply_text("⚠️ يجب التسجيل أولاً! استخدم /start")
        return
    
    text = """
📚 *الدروس المتاحة*

اختر المادة التي تريد دراستها:
"""
    
    keyboard = []
    for key, value in SUBJECTS.items():
        keyboard.append([InlineKeyboardButton(value, callback_data=f'subject_{key}')])
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data='back_main')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def teachers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة الأساتذة"""
    text = """
👨‍🏫 *أفضل الأساتذة*

━━━━━━━━━━━━━━━━━

*د. أحمد بن علي*
🔢 الرياضيات - الثانوي
👥 2,450 طالب | ⭐ 4.9
💰 990 دج/شهر
➡️ /teacher_ahmed

━━━━━━━━━━━━━━━━━

*أ. فاطمة مراد*
⚛️ الفيزياء - الثانوي
👥 1,890 طالب | ⭐ 4.8
💰 890 دج/شهر
➡️ /teacher_fatima

━━━━━━━━━━━━━━━━━

*د. كريم بوعزيز*
💰 العلوم الاقتصادية - جامعي
👥 3,200 طالب | ⭐ 5.0
💰 1,200 دج/شهر
➡️ /teacher_karim

━━━━━━━━━━━━━━━━━

🔍 المزيد من الأساتذة قريبًا...
"""
    await update.message.reply_text(text, parse_mode='Markdown')

async def marketplace_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """السوق الأكاديمي"""
    text = """
🛒 *السوق الأكاديمي*

اشترِ أو بع المواد الدراسية:

━━━━━━━━━━━━━━━━━

📝 *ملخصات شاملة*
ملخصات مركزة لجميع المواد
💰 500 دج | ⭐ 4.9 (234 تقييم)
➡️ /buy_summaries

━━━━━━━━━━━━━━━━━

🔬 *مشاريع جاهزة*
مشاريع نموذجية مع التوثيق
💰 1,200 دج | ⭐ 4.8 (156 تقييم)
➡️ /buy_projects

━━━━━━━━━━━━━━━━━

📚 *بحوث أكاديمية*
بحوث علمية موثقة ومراجع
💰 800 دج | ⭐ 5.0 (89 تقييم)
➡️ /buy_research

━━━━━━━━━━━━━━━━━

💡 *هل تريد بيع مواد دراسية؟*
➡️ /sell_materials
"""
    await update.message.reply_text(text, parse_mode='Markdown')

async def exams_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الامتحانات"""
    text = """
📋 *الامتحانات والاختبارات*

اختبر معلوماتك وحسّن مستواك!

━━━━━━━━━━━━━━━━━

📝 *امتحانات تفاعلية*
• اختيار من متعدد
• أسئلة مقالية
• تصحيح فوري
➡️ /start_exam

━━━━━━━━━━━━━━━━━

🎯 *امتحانات تجريبية*
• تحضير BEM
• تحضير BAC
• امتحانات جامعية
➡️ /mock_exams

━━━━━━━━━━━━━━━━━

📊 *نتائجي*
شاهد نتائجك وتقدمك
➡️ /my_results

━━━━━━━━━━━━━━━━━

🏆 *المتصدرون*
قارن نفسك مع الطلاب الآخرين
➡️ /leaderboard
"""
    await update.message.reply_text(text, parse_mode='Markdown')

async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """خطط الاشتراك"""
    text = """
💳 *خطط الاشتراك*

اختر الخطة المناسبة لك:

━━━━━━━━━━━━━━━━━

📦 *الخطة الأساسية*
💰 990 دج/شهر

✅ 50 درس شهريًا
✅ امتحانات أساسية
✅ دعم عبر البريد
✅ شهادات إلكترونية

➡️ /subscribe_basic

━━━━━━━━━━━━━━━━━

⭐ *الخطة الشاملة* (الأكثر شعبية)
💰 1,990 دج/شهر

✅ دروس غير محدودة
✅ جميع الامتحانات
✅ حصص مباشرة مع الأساتذة
✅ دعم فوري عبر الدردشة
✅ خصومات في السوق الأكاديمي
✅ تحميل جميع المواد

➡️ /subscribe_premium

━━━━━━━━━━━━━━━━━

👨‍🏫 *خطة الأستاذ*
💰 مجانًا

✅ قناة تعليمية خاصة
✅ دروس فيديو غير محدودة
✅ نظام اشتراكات الطلاب
✅ عمولة 15% على المبيعات

➡️ /become_teacher

━━━━━━━━━━━━━━━━━

💳 الدفع الآمن عبر Mastercard
"""
    await update.message.reply_text(text, parse_mode='Markdown')

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض الملف الشخصي"""
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    if not user:
        await update.message.reply_text("⚠️ يجب التسجيل أولاً! استخدم /start")
        return
    
    if user['type'] == 'student':
        level_name = EDUCATION_LEVELS.get(user.get('level', 'primary'), {}).get('name', 'غير محدد')
        text = f"""
👤 *ملفك الشخصي*

📛 الاسم: {user['name']}
🎓 النوع: طالب
📚 المرحلة: {level_name}
💳 الاشتراك: {user.get('subscription', 'لا يوجد')}
🏆 النقاط: {user.get('points', 0)}
✅ الدروس المكتملة: {user.get('courses_completed', 0)}
📅 تاريخ التسجيل: {user['registration_date'][:10]}

━━━━━━━━━━━━━━━━━

⚙️ /edit_profile - تعديل البيانات
💳 /subscribe - ترقية الاشتراك
"""
    else:  # teacher
        text = f"""
👤 *ملفك الشخصي*

📛 الاسم: {user['name']}
👨‍🏫 النوع: أستاذ
📚 التخصص: {user.get('specialization', 'غير محدد')}
👥 عدد الطلاب: {user.get('students_count', 0)}
📹 عدد الدروس: {user.get('courses_count', 0)}
💰 الأرباح: {user.get('earnings', 0)} دج
⭐ التقييم: {user.get('rating', 0)}/5
📅 تاريخ التسجيل: {user['registration_date'][:10]}

━━━━━━━━━━━━━━━━━

📹 /upload_lesson - رفع درس جديد
💰 /my_earnings - أرباحي التفصيلية
"""
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الرسائل النصية"""
    text = update.message.text
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    if not user:
        await update.message.reply_text(
            "مرحبًا! يبدو أنك لم تسجل بعد.\nاستخدم /start للبدء 🦊"
        )
        return
    
    # معالجة الأزرار
    if text == '📖 الدروس':
        await courses_command(update, context)
    elif text == '👨‍🏫 الأساتذة':
        await teachers_command(update, context)
    elif text == '🛒 السوق الأكاديمي':
        await marketplace_command(update, context)
    elif text == '📋 الامتحانات':
        await exams_command(update, context)
    elif text == '💳 اشتراكي':
        await subscribe_command(update, context)
    elif text == 'ℹ️ المساعدة':
        await help_command(update, context)
    elif text == '⚙️ الإعدادات':
        await profile_command(update, context)
    elif text == '🎓 المراحل التعليمية':
        levels_text = "🎓 *اختر مرحلتك التعليمية:*\n\n"
        keyboard = []
        for key, value in EDUCATION_LEVELS.items():
            levels_text += f"{value['name']}\n{value['description']}\n\n"
            keyboard.append([InlineKeyboardButton(value['name'], callback_data=f'level_{key}')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(levels_text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update.message.reply_text(
            "عذرًا، لم أفهم ذلك. استخدم القائمة أو /help للمساعدة 🤔"
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأخطاء"""
    logger.error(f"حدث خطأ: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ عذرًا، حدث خطأ. يرجى المحاولة مرة أخرى."
        )

def main():
    """الدالة الرئيسية"""
    # استخدام التوكن من متغيرات البيئة
    TOKEN = os.getenv("TOKEN")
    
    if not TOKEN:
        logger.error("❌ التوكن غير موجود! تأكد من إضافة TOKEN في Environment Variables")
        return
    
    # إنشاء التطبيق
    app = Application.builder().token(TOKEN).build()
    
    # إضافة المعالجات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("courses", courses_command))
    app.add_handler(CommandHandler("teachers", teachers_command))
    app.add_handler(CommandHandler("marketplace", marketplace_command))
    app.add_handler(CommandHandler("exams", exams_command))
    app.add_handler(CommandHandler("subscribe", subscribe_command))
    app.add_handler(CommandHandler("profile", profile_command))
    
    # معالج الأزرار
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # معالج الرسائل
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # معالج الأخطاء
    app.add_error_handler(error_handler)
    
    # بدء البوت
    logger.info("🦊 بوت أكاديمية الفنك يعمل الآن...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == '__main__':
    main()
