"""
🦊 FENNEC ACADEMY - بوت تلغرام تعليمي
منصة تعليمية جزائرية شاملة

للتجربة المحلية: ضع TOKEN مباشرة
للإنتاج على Render: سيأخذ من Environment Variables
"""

import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from datetime import datetime

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# قاعدة بيانات مؤقتة
users_db = {}
videos_db = []
marketplace_items = []

# ================== بيانات المنصة ==================

CHANNELS = {
    'primary': {
        'name': '📖 الطور الابتدائي',
        'years': {
            '1': 'السنة الأولى ابتدائي',
            '2': 'السنة الثانية ابتدائي',
            '3': 'السنة الثالثة ابتدائي',
            '4': 'السنة الرابعة ابتدائي',
            '5': 'السنة الخامسة ابتدائي'
        }
    },
    'middle': {
        'name': '📐 الطور المتوسط',
        'years': {
            '1': 'السنة الأولى متوسط',
            '2': 'السنة الثانية متوسط',
            '3': 'السنة الثالثة متوسط',
            '4': 'السنة الرابعة متوسط (BEM)'
        }
    },
    'high': {
        'name': '🎓 الطور الثانوي',
        'years': {
            '1': 'السنة الأولى ثانوي',
            '2': 'السنة الثانية ثانوي',
            '3': 'السنة الثالثة ثانوي (BAC)'
        }
    }
}

SUBJECTS = {
    'math': '🔢 الرياضيات',
    'physics': '⚛️ الفيزياء',
    'arabic': '📚 اللغة العربية',
    'french': '🇫🇷 اللغة الفرنسية',
    'english': '🇬🇧 اللغة الإنجليزية',
    'islamic': '☪️ التربية الإسلامية'
}

BARIDIMOB_INFO = """
💳 *الدفع عبر بريدي موب CCP*

📱 الحساب: CCP 00799999900012345678
👤 باسم: أكاديمية الفنك

*خطوات الدفع:*
1️⃣ افتح تطبيق بريدي موب
2️⃣ اختر "تحويل أموال"
3️⃣ أدخل رقم الحساب أعلاه
4️⃣ أدخل المبلغ (990 دج أو 1990 دج)
5️⃣ التقط لقطة شاشة للإيصال

📸 بعد الدفع:
أرسل صورة الإيصال إلى @FennecAcademyPayment

⏱️ التفعيل خلال 2-6 ساعات
"""

TEACHER_GUIDE = """
📚 *دليل الأساتذة*

*كيف ترفع فيديو؟*
📹 استخدم: /upload_video
📝 أرسل الفيديو مع عنوان الدرس

*كم تربح؟*
💰 50 دج لكل فيديو يُنشر
💰 عمولة 20% من اشتراكات طلابك

*كيف تسحب أرباحك؟*
💵 عند وصول 1000 دج
📱 استخدم: /withdraw
🏦 أدخل رقم CCP الخاص بك

*متابعة الأرباح:*
• /my_earnings - رصيدك
• /my_videos - فيديوهاتك
"""

# ================== دوال المساعدة ==================

def get_user(user_id):
    return users_db.get(user_id, None)

def save_user(user_id, data):
    users_db[user_id] = data
    logger.info(f"✅ حفظ بيانات: {user_id}")

def get_main_keyboard(user_type='student'):
    if user_type == 'teacher':
        keyboard = [
            ['📹 رفع فيديو', '💰 أرباحي'],
            ['📊 إحصائياتي', '🛒 السوق'],
            ['⚙️ حسابي', 'ℹ️ المساعدة']
        ]
    else:
        keyboard = [
            ['📖 الابتدائي', '📐 المتوسط', '🎓 الثانوي'],
            ['🛒 السوق', '💳 اشتراكي'],
            ['⚙️ حسابي', 'ℹ️ المساعدة']
        ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ================== معالجات الأوامر ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر البداية"""
    user = update.effective_user
    user_id = user.id
    
    welcome_text = f"""
🦊 *مرحبًا بك في أكاديمية الفنك*
*FENNEC ACADEMY*

أهلاً {user.first_name}! 👋

منصة التعليم الجزائرية الشاملة 🇩🇿

📚 *ما نقدمه:*
✅ دروس فيديو لجميع المراحل
✅ قنوات منظمة حسب السنة والمادة
✅ أساتذة محترفون
✅ سوق إلكتروني للمواد الدراسية
✅ دفع آمن عبر بريدي موب

*اختر نوع حسابك:*
"""
    
    keyboard = [
        [InlineKeyboardButton("👨‍🎓 أنا طالب", callback_data='register_student')],
        [InlineKeyboardButton("👨‍🏫 أنا أستاذ", callback_data='register_teacher')],
        [InlineKeyboardButton("ℹ️ معلومات", callback_data='info')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """المساعدة"""
    help_text = """
📖 *دليل الاستخدام*

*الأوامر الأساسية:*
/start - البداية والتسجيل
/help - المساعدة
/profile - ملفي الشخصي
/payment_info - معلومات الدفع

*للطلاب:*
📚 تصفح الدروس حسب المرحلة
🛒 شراء مواد من السوق
💳 إدارة الاشتراك

*للأساتذة:*
/upload_video - رفع فيديو
/my_earnings - أرباحي
/withdraw - سحب الأرباح
/teacher_guide - دليل الأساتذة

الدعم: @FennecAcademySupport
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأزرار"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == 'register_student':
        user_data = {
            'type': 'student',
            'name': query.from_user.first_name,
            'registration_date': datetime.now().isoformat(),
            'subscription': None,
            'videos_watched': 0
        }
        save_user(user_id, user_data)
        
        text = """
✅ *تم التسجيل بنجاح كطالب!*

يمكنك الآن تصفح الدروس:

📖 الطور الابتدائي (5 سنوات)
📐 الطور المتوسط (4 سنوات + BEM)
🎓 الطور الثانوي (3 سنوات + BAC)

استخدم القائمة أدناه 👇
"""
        await query.edit_message_text(text, parse_mode='Markdown')
        await context.bot.send_message(
            chat_id=user_id,
            text="اختر المرحلة:",
            reply_markup=get_main_keyboard('student')
        )
    
    elif data == 'register_teacher':
        user_data = {
            'type': 'teacher',
            'name': query.from_user.first_name,
            'registration_date': datetime.now().isoformat(),
            'earnings': 0,
            'videos_count': 0,
            'ccp_account': None
        }
        save_user(user_id, user_data)
        
        await query.edit_message_text(TEACHER_GUIDE, parse_mode='Markdown')
        await context.bot.send_message(
            chat_id=user_id,
            text="مرحباً في فريق الأساتذة! 👨‍🏫",
            reply_markup=get_main_keyboard('teacher')
        )
    
    elif data == 'info':
        text = """
📱 *عن أكاديمية الفنك*

منصة تعليمية جزائرية رائدة 🇩🇿

*📊 إحصائياتنا:*
• 1,480+ أستاذ محترف
• 25,000+ طالب مسجل
• 5,250+ درس ومحاضرة

*💳 الدفع:*
بريدي موب CCP - آمن وسريع

📧 info@fennecacademy.dz
"""
        keyboard = [
            [InlineKeyboardButton("🚀 ابدأ الآن", callback_data='register_student')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    
    elif data.startswith('year_'):
        parts = data.split('_')
        level = parts[1]
        year = parts[2]
        
        year_name = CHANNELS[level]['years'][year]
        
        text = f"*{year_name}*\n\n📚 المواد المتاحة:\n\n"
        keyboard = []
        
        for key, name in SUBJECTS.items():
            text += f"{name}\n"
            keyboard.append([InlineKeyboardButton(
                f"{name} - شاهد الدروس",
                callback_data=f'subject_{level}_{year}_{key}'
            )])
        
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data=f'back_{level}')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def show_level(update: Update, context: ContextTypes.DEFAULT_TYPE, level_key):
    """عرض السنوات الدراسية"""
    level = CHANNELS.get(level_key)
    if not level:
        await update.message.reply_text("❌ خطأ")
        return
    
    text = f"*{level['name']}*\n\nاختر السنة:\n"
    keyboard = []
    
    for year_key, year_name in level['years'].items():
        keyboard.append([InlineKeyboardButton(
            year_name,
            callback_data=f"year_{level_key}_{year_key}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def upload_video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رفع فيديو"""
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    if not user or user['type'] != 'teacher':
        await update.message.reply_text("⚠️ هذا الأمر للأساتذة فقط!")
        return
    
    text = """
📹 *رفع فيديو تعليمي*

أرسل الفيديو الآن مع عنوان الدرس

مثال:
"شرح النسب المئوية - رياضيات"

سنراجعه وننشره خلال 24 ساعة
"""
    
    context.user_data['uploading_video'] = True
    await update.message.reply_text(text, parse_mode='Markdown')

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الفيديو المرفوع"""
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    if not user or user['type'] != 'teacher':
        return
    
    if not context.user_data.get('uploading_video'):
        return
    
    video = update.message.video
    caption = update.message.caption or "درس جديد"
    
    video_data = {
        'teacher_id': user_id,
        'teacher_name': user['name'],
        'video_id': video.file_id,
        'caption': caption,
        'date': datetime.now().isoformat()
    }
    videos_db.append(video_data)
    
    user['videos_count'] = user.get('videos_count', 0) + 1
    user['earnings'] = user.get('earnings', 0) + 50
    save_user(user_id, user)
    
    context.user_data['uploading_video'] = False
    
    await update.message.reply_text(f"""
✅ *تم استلام الفيديو بنجاح!*

📹 العنوان: {caption}
💰 ربحك: +50 دج

📊 إجمالي أرباحك: {user['earnings']} دج
📹 عدد فيديوهاتك: {user['videos_count']}

سيتم نشره قريباً في القناة المناسبة!

/my_earnings - شاهد أرباحك
""", parse_mode='Markdown')

async def my_earnings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أرباح الأستاذ"""
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    if not user or user['type'] != 'teacher':
        await update.message.reply_text("⚠️ للأساتذة فقط!")
        return
    
    earnings = user.get('earnings', 0)
    videos = user.get('videos_count', 0)
    
    text = f"""
💰 *أرباحك*

━━━━━━━━━━━━━━━━

💵 الرصيد: *{earnings} دج*
📹 الفيديوهات: {videos}

━━━━━━━━━━━━━━━━

"""
    
    if earnings >= 1000:
        text += "✅ يمكنك السحب!\n/withdraw"
    else:
        text += f"⏳ باقي للسحب: {1000 - earnings} دج"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def withdraw_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """سحب الأرباح"""
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    if not user or user['type'] != 'teacher':
        await update.message.reply_text("⚠️ للأساتذة فقط!")
        return
    
    earnings = user.get('earnings', 0)
    
    if earnings < 1000:
        await update.message.reply_text(f"""
⚠️ الحد الأدنى: 1000 دج

رصيدك: {earnings} دج
باقي: {1000 - earnings} دج
""")
        return
    
    text = f"""
💰 *طلب سحب*

المبلغ: {earnings} دج

أرسل رقم حسابك CCP:
مثال: 00799999900012345678
"""
    
    context.user_data['awaiting_ccp'] = True
    await update.message.reply_text(text, parse_mode='Markdown')

async def marketplace_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """السوق الإلكتروني"""
    text = """
🛒 *السوق الإلكتروني*

*للشراء:*
📝 ملخصات - 300 دج
📚 بحوث - 500 دج
🎯 نماذج امتحانات - 200 دج

*للبيع:*
/sell_item - ارفع مادة للبيع

━━━━━━━━━━━━━━━━

قريباً: المزيد من المواد!
"""
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def payment_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معلومات الدفع"""
    await update.message.reply_text(BARIDIMOB_INFO, parse_mode='Markdown')

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الملف الشخصي"""
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    if not user:
        await update.message.reply_text("⚠️ استخدم /start أولاً")
        return
    
    if user['type'] == 'student':
        text = f"""
👤 *ملفك الشخصي*

📛 {user['name']}
🎓 طالب
📅 {user['registration_date'][:10]}
📺 مشاهدات: {user.get('videos_watched', 0)}

/help - المساعدة
"""
    else:
        text = f"""
👤 *ملفك الشخصي*

📛 {user['name']}
👨‍🏫 أستاذ
📹 فيديوهات: {user.get('videos_count', 0)}
💰 أرباح: {user.get('earnings', 0)} دج
📅 {user['registration_date'][:10]}

/my_earnings - أرباحي
/upload_video - رفع فيديو
"""
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الرسائل"""
    text = update.message.text
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    if not user:
        await update.message.reply_text("مرحباً! استخدم /start للبدء 🦊")
        return
    
    if context.user_data.get('awaiting_ccp'):
        ccp = text.strip()
        user['ccp_account'] = ccp
        earnings = user.get('earnings', 0)
        user['earnings'] = 0
        save_user(user_id, user)
        
        context.user_data['awaiting_ccp'] = False
        
        await update.message.reply_text(f"""
✅ *تم تسجيل طلب السحب!*

💰 المبلغ: {earnings} دج
🏦 الحساب: {ccp}

سيتم التحويل خلال 48 ساعة 🎉
""", parse_mode='Markdown')
        return
    
    if text == '📖 الابتدائي':
        await show_level(update, context, 'primary')
    elif text == '📐 المتوسط':
        await show_level(update, context, 'middle')
    elif text == '🎓 الثانوي':
        await show_level(update, context, 'high')
    elif text == '🛒 السوق':
        await marketplace_command(update, context)
    elif text == '⚙️ حسابي':
        await profile_command(update, context)
    elif text == 'ℹ️ المساعدة':
        await help_command(update, context)
    elif text == '📹 رفع فيديو':
        await upload_video_command(update, context)
    elif text == '💰 أرباحي':
        await my_earnings_command(update, context)
    elif text == '💳 اشتراكي':
        await payment_info_command(update, context)
    else:
        await update.message.reply_text("استخدم القائمة أو /help 🤔")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأخطاء"""
    logger.error(f"خطأ: {context.error}")

def main():
    """الدالة الرئيسية"""
    # للتجربة المحلية: ضع التوكن هنا
    # للإنتاج على Render: سيأخذ من Environment Variables
    TOKEN = os.getenv("TOKEN", "YOUR_BOT_TOKEN_HERE")
    
    if TOKEN = os.getenv("TOKEN", "YOUR_BOT_TOKEN_HERE")
        print("❌ خطأ: يجب وضع التوكن!")
        print("للتجربة: ضع التوكن في السطر 392")
        print("للإنتاج: أضف TOKEN في Environment Variables")
        return
    
    print("🦊 جاري تشغيل بوت أكاديمية الفنك...")
    print("=" * 50)
    
    app = Application.builder().token(TOKEN).build()
    
    # الأوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("upload_video", upload_video_command))
    app.add_handler(CommandHandler("my_earnings", my_earnings_command))
    app.add_handler(CommandHandler("withdraw", withdraw_command))
    app.add_handler(CommandHandler("marketplace", marketplace_command))
    app.add_handler(CommandHandler("payment_info", payment_info_command))
    app.add_handler(CommandHandler("profile", profile_command))
    
    # معالجات
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # معالج الأخطاء
    app.add_error_handler(error_handler)
    
    print("✅ البوت يعمل الآن!")
    print("=" * 50)
    print("📱 افتح تلغرام وابحث عن بوتك")
    print("🔴 لإيقاف البوت اضغط Ctrl+C")
    print("=" * 50)
    
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == '__main__':
    main()
