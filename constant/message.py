class ReadyMessage:
    start_conversation = "سلام.\n" \
                         "به بازوی *معرفی کانال‌ها و بازوهای بله* خوش آمدید. لطفا یکی از گزینه‌های زیر را انتخاب کنید:"
    send_content_plz = "لطفا متن خود را ارسال نمایید."
    choose_content_type = "درخواست شما برای کدام نوع است؟"
    no_content_type_available = "*هیچ نوعی موجود نمی باشد.*\n" \
                                "از ادمین درخواست کنید تا نوع جدید تعریف کند."

    enter_content_name = "نام {} خود را وارد کنید."
    enter_content_nick_name = "لطفا آی‌دی {} خود را (بدون @) وارد کنید."
    enter_content_description = "لطفا توضیحات {} خود را وارد کنید."
    choose_content_category = "لطفا دسته‌بندی {} خود را انتخاب کنید."
    upload_content_log = "لطفا تصویر معرفی {} خود را بارگذاری کنید.\n" \
                         "*نکته:* ترجیحا تصویر در ابعاد مربعی و با کیفیت ارسال کنید." \
                         " تصویر پست معرفی مهم‌ترین معرف شماست؛ از ارسال تصاویر نامربوط و شلوغ پرهیز فرمایید."
    success_send_content = "{} شما با *موفقیت*" \
                           " در لیست انتظار برای درج در کانال منتخبین و پایگاه داده‌ی این بازو قرار گرفت.\n" \
                           "به محض *تایید یا رد* این درخواست، از طریق همین بازو مطلع خواهید شد."
    choose_type = "نوع را انتخاب نمایید."
    category_changed_successfully = "دسته‌بندی با *موفقیت* به {} تغییر کرد."

    choose_category = "دسته‌بندی را انتخاب نمایید."
    no_type_available = "متاسفانه!\n" \
                        "*هیچ* نوعی وجود ندارد."
    no_category_available = "متاسفانه!\n" \
                            "*هیچ* دسته‌بندی وجود ندارد."
    choose_what_to_do = "برای مدیریت انواع و دسته‌بندی‌ها چه کاری می‌خواهید انجام دهید؟"
    enter_category_name = "نام دسته را وارد نمایید."
    enter_category_new_name = "نام جدید این دسته را وارد نمایید."

    enter_type_name = "نام نوع را وارد نمایید."
    enter_new_type_name = "نام جایگزین برای این نوع را وارد کنید:"
    deleted_successfully = "*{}* با موفقیت حذف گردید."
    edit_name_successfully = "نام {} به *{}* با *موفقیت* تغییر یافت."
    category_added_successfully = "دسته {} با *موفقیت* اضافه گردید."
    type_added_successfully = "نوع {} با *موفقیت* اضافه گردید."
    content_not_found = "مطلب مورد نظر پیدا نشد!"
    publish_status = "وضعیت انتشار: {}"
    request_content_text = "کد محتوا: {}\n" \
                           "📺 {} \n" \
                           "📄 {}\n" \
                           "🔖 #{} #{}\n" \
                           "🆔 @{}\n" \
                           "🔗 https://ble.im/{}"
    content_template = "📺 {} \n" \
                       "📄 {}\n" \
                       "🔖 #{} #{}\n" \
                       "🆔 @{}\n" \
                       "🔗 https://ble.im/{}"

    accept_content = "درخواست کانال {} با آیدی {} در صف انتشار قرار گرفت."
    accept_content_client = "*تبریک! *\nدرخواست کانال {} با آیدی {} برای معرفی در کانال منتخبین پذیرفته شد."
    reject_content = "کانال {} با آیدی {} رد شد.\n" \
                     "لطفا دلیل رد درخواست را بنویسید در غیر این صورت *عدم ذکر دلیل* را بزنید.\n" \
                     "*نکته:*  این دلیل برای درخواست کننده ارسال می‌شود."
    reject_content_client = "متأسفیم!\nدرخواست درج کانال {} با آیدی {} برای معرفی در کانال منتخبین پذیرفته *نشد. *"
    reason = "دلیل: {}"
    reason_sent_to_client = "دلیل رد شما برای کاربر مربوطه با *موفقیت* ارسال شد."
    accept_content_with_edit_client = "*تبریک! *\nدرخواست درج کانال {} با آیدی {} با" \
                                      " شرط اصلاح برای معرفی در کانال منتخبین پذیرفته شد."
    what_to_edit = "کدام ویژگی درخواست را تغییر می‌دهید؟"
    enter_new_text = "{} جدید را وارد کنید:"
    replace_successfully = "متن {} کانال با *موفقیت* تغییر یافت.\n"
    replace_logo_successfully = "عکس مطلب با *موفقیت* تغییر یافت."
    no_new_content_recently = "متاسفانه! *هیچ* درخواست جدیدی یافت نشد."
    send_new_logo = "عکس جدید را ارسال کنید:"
    content_sent_before = "این درخواست پیش تر منتشر شده است و دیگر امکان اصلاح ندارد."
    # ---------------------------------------------------------------------------------------------------------
    error = "*خطایی رخ داده است. *" \
            " لطفا دوباره امتحان کنید."
    wrong_case_happened = "قالب ورودی معتبر نیست!\n" \
                          "لطفا *دوباره* تلاش کنید."
    information = "بات ثبت کانال در کانال منتخبین بله"
    send_new_publish_hour = "ساعت انتشار جدید را در قالب یک در عدد بین ۰ تا ۲۳ بفرستید."
    invalid_publish_hour = "خطا! ساعت ورودی قالب درستی ندارد." \
                           "لطفا دوباره تلاش کنید."
    set_publish_hour_successfully = "ساعت انتشار جدید به درستی تنظیم گردید."
    duplicated_category = "خطا! نام *دسته* مورد نظر شما تکراری است."
    duplicated_type = "خطا! نام *نوع مطلب* مورد نظر شما تکراری است."


class TMessage:
    cancel = "لغو"
    keep_on = "تایید و ادامه"
    start = "ادامه"
    info = "راهنما"
    back = "بازگشت به منو اصلی"
    search_content = "پیمایش در کانال‌ها و بازوها"
    set_publish_time = "تنظیم زمان ارسال به کانال منتخبین"
    show_types = "نمایش نوع ها"
    request_content = "درخواست معرفی"
    get_sent_content = "آخرین درخواست‌های رسیده"
    get_archive_content = "دریافت مطالب آرشیو"
    # =======================================================
    manage_category = "مدیریت دسته ها"
    manage_type = "مدیریت نوع ها"
    add_category = "افزودن دسته‌بندی جدید"
    edit_category = "ویرایش دسته‌بندی"
    remove_category = "حذف دسته‌بندی"
    add_type = "افزودن نوع جدید"
    edit_type = "ویرایش نوع"
    remove_type = "حذف نوع"
    # =======================================================
    content_name = "نام"
    content_nick_name = "آی‌دی"
    content_description = "توضیح"
    content_category = "دسته‌بندی"
    content_logo = "تصویر"
    # =======================================================
    no_reason = "عدم ذکر دلیل"
    preview = "پیش نمایش"
    accept = "تایید انتشار"
    reject = "رد کردن"
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
    nick_name = "^[a-zA-Z0-9$!%*?&#^-_.+]+$"
