import telebot
from telebot.types import (
InlineKeyboardMarkup,
InlineKeyboardButton
)
from flask import Flask, request, abort
import config
import keyboards
from cron import cron_sleep_one_day
from models import models
from keyboards import ReplyKB
bot = telebot.TeleBot(config.TOKEN)
app = Flask(__name__)


# Empty webserver index, return nothing, just http 200
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return None

# Process webhook calls
@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)


@cron_sleep_one_day
def get_status():
    for user in models.User.objects():
        try:
            bot.send_chat_action(user.user_id, 'typing')
            obj = models.User.objects(user_id=user.user_id).get()
            obj.is_block = False
        except telebot.apihelper.ApiException:
            obj = models.User.objects(user_id=user.user_id).get()
            obj.is_block = True


@bot.message_handler(commands=['start'])
def start(message):
    greeting_str = 'Добро пожаловать в магазин minimall'

    keyboard = ReplyKB().generate_kb(*keyboards.beginning_kb.values())
    bot.send_message(message.chat.id, greeting_str, reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == keyboards.beginning_kb['products'])
def show_categories(message):
    """
    :param message:
    :return: listed root categories
    """

    kb = keyboards.InlineKB(key='root', lookup_field='id', named_arg='category')
    bot.send_message(message.chat.id, 'Выберите категорию', reply_markup=kb.generate_kb())


@bot.message_handler(func=lambda message: message.text == keyboards.beginning_kb['news'])
def news(message):
    for i in models.Texts.objects(title='News'):
        bot.send_message(message.chat.id, i.body)


@bot.message_handler(func=lambda message: message.text == keyboards.beginning_kb['about'])
def about(message):
    info = models.Texts.objects(title='about').get()
    bot.send_message(message.chat.id, info.body)


@bot.message_handler(func=lambda message: message.text == keyboards.beginning_kb['sales'])
def sales(message):
    products = models.Product.objects(is_discount=True)

    for product in products:
        kb = InlineKeyboardMarkup()
        kb.add(telebot.types.InlineKeyboardButton(text='Добавить в корзину', callback_data='cart_' + str(product.id)))

        bot.send_message(message.chat.id, parse_mode='HTML', text=f'Название товара: {product.title}')
        bot.send_photo(message.chat.id, product.p_img.read(), parse_mode='HTML',
                       caption=f'Описание: {product.description}\nЦена: {product.get_price}', reply_markup=kb)


@bot.message_handler(func=lambda message: message.text == keyboards.beginning_kb['cart'])
def show_products_in_cart(message):
    user = models.User.objects(user_id=str(message.from_user.id)).get()

    if not models.Cart.objects(user=user.id, active=True):
        return bot.send_message(message.chat.id, text='У вас нет продуктов в корзине')

    cart = models.Cart.objects(user=user.id, active=True).get()

    for products in cart.product:
        product = models.Product.objects(id=products.id).get()
        bot.send_message(message.chat.id, text=f'Название товара: {product.title}\nОписание: {product.description}\n'
                                               f'Цена: {product.get_price}')

    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton(text='Оформить заказ', callback_data='buy_' + str(user.id)))
    bot.send_message(message.chat.id, text=f'Итоговоя сумма: {cart.sum_cost(user.id)}', reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'category')
def show_products_or_sub_category(call):
    """

    :param call:
    :return: listed subcategories || listed products
    """
    obj_id = call.data.split('_')[1]
    category = models.Category.objects(id=obj_id).get()

    if category.is_parent:

        kb = keyboards.InlineKB(
            iterable=category.subcategory,
            lookup_field='id',
            named_arg='category'
        )
        kb.generate_kb()
        kb.add(InlineKeyboardButton(text=f'<< {category.title}', callback_data=f'back_{category.id}'))

        bot.edit_message_text(text=category.title, chat_id=call.message.chat.id, message_id=call.message.message_id,
                              reply_markup=kb)

    else:
        products = category.get_products()
        for product in products:
            kb = InlineKeyboardMarkup()
            kb.add(telebot.types.InlineKeyboardButton(text='Добавить в корзину',callback_data='cart_' + str(product.id)))

            bot.send_message(call.message.chat.id, parse_mode='HTML', text=f'Название товара: {product.title}')
            bot.send_photo(call.message.chat.id, product.p_img.read(), parse_mode='HTML',
                           caption=f'Описание: {product.description}\nЦена: {product.get_price}', reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'back')
def go_back(call):
    obj_id = call.data.split('_')[1]
    category = models.Category.objects(id=obj_id).get()

    if category.is_root:
        kb = keyboards.InlineKB(key='root', lookup_field='id', named_arg='category')
        kb.generate_kb()


    else:
        kb = keyboards.InlineKB(
            iterable=category.parent.subcategory,
            lookup_field='id',
            named_arg='category',
        )
        kb.generate_kb()
        kb.add(InlineKeyboardButton(text=f'<< {category.parent.title}',callback_data=f'back_{category.parent.id}'))

    text = 'Категории' if not category.parent else category.parent.title
    bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'cart')
def add_product_to_cart(call):

    product = models.Product.objects(id=call.data.split('_')[1]).get()

    if not models.User.objects(user_id=str(call.from_user.id)):
        models.User(user_id=str(call.from_user.id), user_name=call.from_user.username).save()

    user = models.User.objects(user_id=str(call.from_user.id)).get()
    if not user.show_cart:
        models.Cart(user=user).save()

    cart = models.Cart.objects(user=user.id, active=True).get()
    cart.add_to_cart(product)
    cart.save()

    bot.send_message(call.message.chat.id, f'{product.title} добавлен в корзину')


@bot.message_handler(func=lambda message: message.text == keyboards.beginning_kb['cart_history'])
def cart_history(message):
    user = models.User.objects(user_id=str(message.from_user.id)).get()

    if not user.show_history:
        return bot.send_message(message.chat.id, text='У вас нет покупок')

    carts_history = user.show_history

    for carts in carts_history:
        for cart in carts.cart:
            bot.send_message(message.chat.id, text=f'Корзина: {carts.cart.index(cart)+1}')
            for products in cart.product:
                product = models.Product.objects(id=products.id).get()
                bot.send_message(message.chat.id, text=f'Название товара: {product.title}')


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'buy')
def buy_cart(call):

    user = models.User.objects(user_id=str(call.from_user.id)).get()
    cart = models.Cart.objects(user=user.id, active=True).get()
    if not user.show_history:
        models.CartHistory(user=user).save()

    history_cart = models.CartHistory.objects(user=user.id).get()
    history_cart.add_to_cart(cart)
    cart.update(active=False)

    bot.send_message(call.message.chat.id, 'Спасибо за покупку наш менеджер с вами свяжется')

# bot.polling(none_stop=True)

if __name__ == '__main__':
    import time
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(config.webhook_url, certificate=open('webhook_cert.pem', 'r'))
    get_status()
    app.run(debug=True)