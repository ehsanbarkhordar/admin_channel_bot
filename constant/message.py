class ReadyMessage:
    start_conversation = "سلام.\nبه بات *مدیریت کانال و گروه* خوش آمدید. لطفا یکی از گزینه های زیر را انتخاب کنید."
    choose_your_channel = "لطفا کانالی را که قصد ارسال مطلب در آن را دارید انتخاب کنید."
    send_content_plz = "لطفا متن خود را ارسال نمایید."
    enter_channel_name = "نام کانال خود را وارد کنید."
    enter_channel_nick_name = "لطفا آیدی کانال خود را با @ وارد کنید."
    enter_channel_description = "لطفا توضیحات کانال خود را وارد کنید."
    choose_channel_category = "لطفا دسته بندی کانال خود را انتخاب نمایید."
    upload_channel_log = "لطفا عکس کانال را آپلود کنید."
    success_send_content = "کانال شما با *موفقیت* در لیست انتظار برای درج در کانال های منتخبین بله قرار گرفت.\n" \
                           "به محض تایید یا رد به شما از طریق همین بات اعلان می گردد."
    enter_category_name = "نام دسته را وارد نمایید."
    category_added_successfully = "دسته {} با *موفقیت* اضافه گردید."
    request_content_text = "نام کانال: {}\n" \
                           "آیدی کانال: {}\n" \
                           "توضیحات کانال: {}\n" \
                           "دسته کانال: {}\n"
    accept_content = "کانال {} با آیدی {} پذیرفته شد."
    accept_content_client = "تبریک!\nدرخواست درج کانال {} با آیدی {} برای معرفی در کانال منتخبین پذیرفته شد."
    reject_content = "کانال {} با آیدی {} رد شد."
    reject_content_client = "متأسفیم!\nدرخواست درج کانال {} با آیدی {} برای معرفی در کانال منتخبین پذیرفته نشد."
    accept_content_with_edit_client = "تبریک!\nدرخواست درج کانال {} با آیدی {} با شرط اصلاح برای معرفی در کانال منتخبین پذیرفته شد."
    replace_description = "متن جایگزین توضیحات کانال {} با آیدی {} را وارد نمایید."
    replace_description_success_fully = "متن توضیحات کانال با موفقیت تغییر یافت. و کانال اکسپت شد."
    no_new_content_recently = "هیچ درخواست جدیدی یافت نشد!"
    channel_sent_before = "این کانال قبلا فرستاده شده است."
    # ---------------------------------------------------------------------------------------------------------
    error = "*خطایی رخ داده است. *" \
            " لطفا دوباره امتحان کنید."
    information = "Created by:\n" \
                  "@EhsanBarkhordar"


class TMessage:
    cancel = "لغو"
    keep_on = "تایید و ادامه"
    edit = "اصلاح میکنم"
    start = "ادامه"
    info = "راهنما"
    back = "بازگشت به منو اصلی"
    send_content = "درخواست معرفی کانال شما"
    get_sent_content = "دریافت مطالب تازه فرستاده شده"
    get_archive_content = "دریافت مطالب آرشیو"
    add_category = "اضافه کردن دسته جدید"
    accept = "تایید"
    reject = "رد"
    accept_with_edit = "تایید با شرط اصلاح"


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
