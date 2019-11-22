from mongoengine import *

connect("web_shop_bot")


class Texts(Document):
    title = StringField(max_length=255)
    body = StringField(max_length=4096)


class Properties(DynamicEmbeddedDocument):
    weight = FloatField(min_value=0)


class Category(Document):
    title = StringField(max_length=255, required=True)
    description = StringField(max_length=512)
    subcategory = ListField(ReferenceField('self'))
    parent = ReferenceField('self')

    @classmethod
    def get_root_categories(cls):
        return cls.objects(parent=None)

    @property
    def is_parent(self):
        return bool(self.subcategory)

    @property
    def is_root(self):
        return not bool(self.parent)

    @property
    def get_products(self, **kwargs):
        return Product.objects(category=self, **kwargs)

    def add_subcategory(self, obj):
        obj.parent = self
        obj.save()
        self.subcategory.append(obj)
        self.save()


class Product(Document):
    title = StringField(max_length=255)
    description = StringField(max_length=1024)
    price = IntField(min_value=0)
    new_price = IntField(min_value=0)
    is_discount = BooleanField(default=False)
    properties = EmbeddedDocumentField(Properties)
    category = ReferenceField(Category)
    p_img = FileField()

    @property
    def get_price(self):
        if self.is_discount:
            return str(self.new_price / 100)
        return str(self.price / 100)

    @classmethod
    def get_discount_products(cls, **kwargs):
        return cls.objects(is_discount=True, **kwargs)

    def add_img(self, img):
        self.img.put(img, content_type='image/jpg')
        self.save()


class User(Document):
    user_id = StringField(max_length=124)
    user_name = StringField(max_length=124)
    phone = StringField(default='')

    @property
    def show_cart(self):
        return Cart.objects(user=self, active=True)

    @property
    def show_history(self):
        return CartHistory.objects(user=self)



class Cart(Document):
    user = ReferenceField(User)
    product = ListField(ReferenceField(Product))
    active = BooleanField(default=True)

    def add_to_cart(self, obj):
        self.product.append(obj)
        self.save()

    @classmethod
    def sum_cost(cls, user):
        sum_all = 0
        cart = cls.objects(user=user, active=True).get()
        for product in cart.product:
            sum_all += float(product.get_price)
        return sum_all


class CartHistory(Document):
    user = ReferenceField(User)
    cart = ListField(ReferenceField(Cart))

    def add_to_cart(self, obj):
        self.cart.append(obj)
        self.save()
