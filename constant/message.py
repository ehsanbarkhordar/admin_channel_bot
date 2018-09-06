class ReadyMessage:
    start_conversation = "سلام.\n" \
                         "به بازوی *معرفی کانال‌ها و بازوهای بله* خوش آمدید. لطفا یکی از گزینه‌های زیر را انتخاب کنید:"
    send_content_plz = "لطفا متن خود را ارسال نمایید."
    choose_content_type = "درخواست شما برای کدام نوع است؟"
    enter_content_name = "نام کانال خود را وارد کنید."
    enter_content_nick_name = "لطفا آی‌دی کانال خود را (بدون @) ذکر کنید."
    enter_content_description = "لطفا توضیحات کانال خود را وارد کنید."
    choose_content_category = "لطفا دسته‌بندی [کانال/خیریه‌ي/فروشگاه/بازوی] خود را انتخاب کنید."
    upload_content_log = "لطفا تصویر معرفی [کانال/خیریه/فروشگاه/بازوی] خود را بارگذاری کنید.\n" \
                         "*نکته:* ترجیحا تصویر در ابعاد مربعی و با کیفیت ارسال کنید." \
                         " تصویر پست معرفی مهم‌ترین معرف شماست؛ از ارسال تصاویر نامربوط و شلوغ پرهیز فرمایید."
    success_send_content = "[کانال/خیریه‌ی/فروشگاه/بازوی] شما با *موفقیت*" \
                           " در لیست انتظار برای درج در کانال منتخبین و پایگاه داده‌ی این بازو قرار گرفت.\n" \
                           "به محض *تایید یا رد* این درخواست، از طریق همین بازو مطلع خواهید شد."
    choose_type = "نوع را انتخاب نمایید."
    enter_category_name = "نام دسته را وارد نمایید."
    enter_type_name = "نام نوع را وارد نمایید."

    category_added_successfully = "دسته {} با *موفقیت* اضافه گردید."
    type_added_successfully = "نوع {} با *موفقیت* اضافه گردید."

    request_content_text = "📺 {} \n" \
                           "📄 {}\n" \
                           "🔖 #{}\n" \
                           "🆔 @{}\n" \
                           "🔗 https://ble.im/{}"

    accept_content = "درخواست کانال {} با آیدی {} در صف انتشار قرار گرفت."
    accept_content_client = "تبریک!\nدرخواست کانال {} با آیدی {} برای معرفی در کانال منتخبین پذیرفته شد."
    reject_content = "کانال {} با آیدی {} رد شد.\n" \
                     "لطفا دلیل رد درخواست را بنویسید در غیر این صورت *عدم ذکر دلیل* را بزنید.\n" \
                     "*نکته:*  این دلیل برای درخواست کننده ارسال می‌شود."
    reject_content_client = "متأسفیم!\nدرخواست درج کانال {} با آیدی {} برای معرفی در کانال منتخبین پذیرفته نشد."
    reason = "*دلیل: *{}"
    reason_sent_to_client = "دلیل رد شما برای کاربر مربوطه با موفقیت ارسال شد."
    accept_content_with_edit_client = "تبریک!\nدرخواست درج کانال {} با آیدی {} با" \
                                      " شرط اصلاح برای معرفی در کانال منتخبین پذیرفته شد."
    replace_description = "متن جایگزین توضیحات کانال {} با آیدی {} را وارد نمایید.\n" \
                          "اگر میخواهید فقط عکس مطلب را تغییر دهید بر روی دکمه *تغییر عکس* بزنید."
    replace_description_successfully = "متن توضیحات کانال با موفقیت تغییر یافت.\n" \
                                       "در ادامه اگر مایل به تغییر عکس مطلب هستید" \
                                       " روی دکمه *تغییر عکس* کلیک کنید و" \
                                       " در غیر این صورت دکمه *بازگشت به منو اصلی* را بفشارید."
    replace_logo_successfully = "عکس مطلب با *موفقیت* تغییر یافت."
    no_new_content_recently = "متاسفانه!*هیچ* درخواست جدیدی یافت نشد."
    send_new_logo = "عکس جدید را ارسال کنید:"
    content_sent_before = "این درخواست پیش تر منتشر شده است و دیگر امکان اصلاح ندارد."
    # ---------------------------------------------------------------------------------------------------------
    error = "*خطایی رخ داده است. *" \
            " لطفا دوباره امتحان کنید."
    information = "بات ثبت کانال در کانال منتخبین بله"
    duplicated_category = "خطا! نام *دسته* مورد نظر شما تکراری است."
    duplicated_type = "خطا! نام *نوع مطلب* مورد نظر شما تکراری است."


class TMessage:
    cancel = "لغو"
    keep_on = "تایید و ادامه"
    edit = "اصلاح میکنم"
    start = "ادامه"
    info = "راهنما"
    back = "بازگشت به منو اصلی"
    search_content = "پیمایش در کانال‌ها و بازوها"
    show_types = "نمایش نوع ها"
    request_content = "درخواست معرفی"
    get_sent_content = "آخرین درخواست‌های رسیده"
    get_archive_content = "دریافت مطالب آرشیو"
    add_category = "اضافه کردن دسته جدید"
    add_type = "اضافه کردن نوع جدید"
    no_reason = "عدم ذکر دلیل"
    change_logo = "تغییر عکس"
    accept = "تایید انتشار"
    reject = "رد"
    accept_with_edit = "تایید با شرط تغییر"


class LogMessage:
    start = "conversation started"
    success_send_message = "success send message"
    fail_send_message = "failed send message"
    max_fail_retried = "max fails retried"
    invalid_game = "invalid game"
    edit_name = "edit name started"

    fail_notification = "notification push failed"
    success_notification = "{} notification pushed"

    insert_predict_error = "error in insertion predicts"
    no_game = "no game is valid"
    new_user_detected = "new user start conversation"

    bot_error = "there is a problem with bot, program is exiting"
    request_game_id = "a game id result requested"

    get_prediction_started = "take prediction started"
    wrong_prediction = "wrong prediction occurred"
    right_prediction = "right prediction occurred"
    cancel_progress = "progress canceled"

    respond_notification = "respond to push message"

    info = "info showed"

    got_name = "name received"
    got_phone_number = "phone number received"

    take_iran_goals = "taking iran goals"
    take_opponent_team = "take opponent team"

    get_past_prediction = "get past prediction started"

    request_valid_predictions = "request valid predictions"

    change_template_failed = "change template message failed"

    change_template_success = "change template message success"
    check_db_connection = "Check db connection"
    fail_to_connect_db = "fail to connect db"
    success_connect_db = "db is connected"
    db_string_executed = "db string executed"

    fail_create_table = "fail create table"
    success_create_table = "success create table or table existed before"

    success_user_registration = "user registration was successful"
    invalid_phone_number = "phone number is invalid"


class Regex:
    phone_number_regex = '(^(\+98|0098|0)?9\d{9})|(^(\+۹۸|۰۰۹۸|۰)?۹[۰-۹]{9})$'
    score_regex = '(^[0-9]+)$|(^[۰-۹]+)$'
    persian_number_regex = '([۰-۹])+'
    number_regex = '^([0-9]+|[۰-۹]+)$'
    persian_regex = "[ء|\s|آ-ی]+"
    any_match = "(.*)"
