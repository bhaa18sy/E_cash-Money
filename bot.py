import os
import logging
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    ConversationHandler, 
    ContextTypes, 
    filters
)

# تمكين التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# تعريف حالات المحادثة
NAME, PHONE, ADDRESS, AMOUNT, TRANSFER_NUMBER, RECIPIENT_NAME, RECIPIENT_ADDRESS, RECIPIENT_PHONE, RECEIPT_PHOTO = range(9)

# تخزين البيانات مؤقتاً (في بيئة حقيقية استخدم قاعدة بيانات)
user_data = {}

# تعريف لوحة المفاتيح
keyboard = ReplyKeyboardMarkup([
    ['حالة الحوالة', 'مكان وصول الحوالة الآن']
], resize_keyboard=True)

# بدء المحادثة
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'مرحباً! أهلاً بك في خدمة التحويلات.\nيرجى إدخال الاسم الثلاثي:',
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME

# معالجة الاسم
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id] = {'name': update.message.text}
    
    await update.message.reply_text('شكراً! الآن يرجى إدخال رقم الهاتف:')
    return PHONE

# معالجة رقم الهاتف
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id]['phone'] = update.message.text
    
    await update.message.reply_text('تم حفظ رقم الهاتف. الآن يرجى إدخال العنوان:')
    return ADDRESS

# معالجة العنوان
async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id]['address'] = update.message.text
    
    await update.message.reply_text('تم حفظ العنوان. الآن يرجى إدخال المبلغ:')
    return AMOUNT

# معالجة المبلغ
async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id]['amount'] = update.message.text
    
    await update.message.reply_text('تم حفظ المبلغ. الآن يرجى إدخال رقم الحوالة:')
    return TRANSFER_NUMBER

# معالجة رقم الحوالة
async def get_transfer_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id]['transfer_number'] = update.message.text
    
    await update.message.reply_text('تم حفظ رقم الحوالة. الآن يرجى إدخال اسم المستلم:')
    return RECIPIENT_NAME

# معالجة اسم المستلم
async def get_recipient_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id]['recipient_name'] = update.message.text
    
    await update.message.reply_text('تم حفظ اسم المستلم. الآن يرجى إدخال عنوان المستلم:')
    return RECIPIENT_ADDRESS

# معالجة عنوان المستلم
async def get_recipient_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id]['recipient_address'] = update.message.text
    
    await update.message.reply_text('تم حفظ عنوان المستلم. الآن يرجى إدخال رقم هاتف المستلم:')
    return RECIPIENT_PHONE

# معالجة رقم هاتف المستلم
async def get_recipient_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id]['recipient_phone'] = update.message.text
    
    await update.message.reply_text('تم حفظ رقم هاتف المستلم. الآن يرجى إرسال صورة الإشعار:')
    return RECEIPT_PHOTO

# معالجة صورة الإشعار
async def get_receipt_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    photo_file = await update.message.photo[-1].get_file()
    
    # حفظ معلومات الصورة (في بيئة حقيقية، احفظ الصورة في ملف أو قاعدة بيانات)
    user_data[user_id]['receipt_photo'] = photo_file.file_path
    
    # حساب وقت الانتهاء بعد 48 ساعة
    end_time = datetime.now() + timedelta(hours=48)
    user_data[user_id]['end_time'] = end_time
    
    # إرسال رسالة التأكيد
    await update.message.reply_text(
        f'تم استلام جميع المعلومات!\n'
        f'سيصل إشعار إلى رقمك عند التأكد من حالة الحوالة.\n'
        f'العد التنازلي: 48:00:00',
        reply_markup=keyboard
    )
    
    # بدء العد التنازلي (في بيئة حقيقية، استخدم مهمة مجدولة)
    context.job_queue.run_repeating(
        update_countdown, 
        interval=3600, 
        first=10, 
        data=user_id, 
        name=str(user_id)
    )
    
    return ConversationHandler.END

# تحديث العد التنازلي
async def update_countdown(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    user_id = job.data
    user_info = user_data.get(user_id)
    
    if user_info and 'end_time' in user_info:
        remaining = user_info['end_time'] - datetime.now()
        if remaining.total_seconds() > 0:
            hours, remainder = divmod(int(remaining.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            
            # في بيئة حقيقية، أرسل رسالة للمستخدم
            # await context.bot.send_message(chat_id=user_id, text=f'الوقت المتبقي: {hours:02d}:{minutes:02d}:{seconds:02d}')
        else:
            # أوقف المهمة عندما ينتهي الوقت
            context.job_queue.get_jobs_by_name(str(user_id))[0].schedule_removal()

# معالجة حالة الحوالة
async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_info = user_data.get(user_id)
    
    if user_info and 'end_time' in user_info:
        remaining = user_info['end_time'] - datetime.now()
        if remaining.total_seconds() > 0:
            hours, remainder = divmod(int(remaining.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            await update.message.reply_text(f'حالة الحوالة: قيد المعالجة\nالوقت المتبقي: {hours:02d}:{minutes:02d}:{seconds:02d}')
        else:
            await update.message.reply_text('تمت معالجة الحوالة بنجاح!')
    else:
        await update.message.reply_text('لا توجد حوالة نشطة.')

# معالجة مكان وصول الحوالة
async def check_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # هذه مجرد وظيفة تجريبية، في التطبيق الحقيقي تحتاج إلى دمج مع خدمة التتبع
    await update.message.reply_text('الحوالة حالياً في مركز التوزيع الرئيسي،预计 ستصل خلال 24 ساعة.')

# إلغاء المحادثة
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'تم إلغاء العملية.', 
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# الدالة الرئيسية
def main():
    # استبدل "YOUR_TOKEN" بـ token البوت الذي حصلت عليه من BotFather
    token = os.environ.get('BOT_TOKEN', 'YOUR_TOKEN_HERE')
    application = Application.builder().token(token).build()
    
    # إعداد معالج المحادثة
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_amount)],
            TRANSFER_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_transfer_number)],
            RECIPIENT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_recipient_name)],
            RECIPIENT_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_recipient_address)],
            RECIPIENT_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_recipient_phone)],
            RECEIPT_PHOTO: [MessageHandler(filters.PHOTO, get_receipt_photo)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.Regex('^حالة الحوالة$'), check_status))
    application.add_handler(MessageHandler(filters.Regex('^مكان وصول الحوالة الآن$'), check_location))
    
    # بدء البوت
    application.run_polling()

if __name__ == '__main__':
    main()