from mongoengine import connect
import models
from random import randint
import os

connect("web_shop_bot")


categories = ['Phone', 'laptop', 'TV']
subcategories = [['headphones', 'battery', 'phone cases'], ['charging cable', 'laptop case'],
                 ['speakers', 'remotes', 'players']]
product =[[['Panasonic RP', 'JBL C45BT', 'HyperX'],['500 mA/h', '800 mA/h'],['iPhone X', 'iPhone 8', 'iPhone 7']],
          [['original', 'multifunctional'],['MakBook', 'Lenovo', ]],
          [['ubl2go', 'sony bass', 'true bass'],['original', 'multifunctional'],['lg dvd', 'sony vhs']]]


for i in categories:
    models.Category(title=i, description=f'{i} directory description',).save()

    for j in subcategories[categories.index(i)]:
        subcut = models.Category(title=j, description=f'{j} directory description',).save()
        models.Category.objects(title=i).get().add_subcategory(subcut)
#
for i in product:
    for j, m in zip(subcategories[product.index(i)], i):
        for y in m:
            product_price = randint(1000, 10000)
            discount_price = product_price/2
            if m.index(y) % 2 == 0:

                models.Product(title=y, description=f'{y} directory description', price=product_price,
                            new_price=product_price, category=models.Category.objects(title=j).get()).save()
            else:

                models.Product(title=y, description=f'{y} directory description', price=product_price,
                               new_price=discount_price, is_discount=True,
                               category=models.Category.objects(title=j).get()).save()



for product in models.Product.objects:
    p_img = open('1.jpg', 'rb')
    product.p_img.put(p_img, content_type='image/jpeg')
    product.save()


news = ['Осенняя распродажа', 'Черная пятница', 'Сезонные скидки']
for i in news:
    models.Texts(title='News', body=i).save()

about ='Нашему магазину уже много лет :) Мы находимся в ЦУМе'
models.Texts(title='about', body=str(about)).save()