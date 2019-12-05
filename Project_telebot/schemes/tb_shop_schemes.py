from marshmallow import fields, Schema


class PropertiesSchema(Schema):
    weight = fields.Float()


class SubCategory(Schema):
    id = fields.String()
    title = fields.String()
    description = fields.String()
    parent = fields.Nested('self')


class CategorySchema(Schema):
    id = fields.String()
    title = fields.String()
    description = fields.String()
    subcategory = fields.List(fields.Nested(SubCategory()))
    parent = fields.Nested('self')


class ProductSchema(Schema):
    id = fields.String()
    title = fields.String()
    description = fields.String()
    price = fields.Int()
    new_price = fields.Int()
    is_discount = fields.Boolean()
    properties = fields.Nested(PropertiesSchema)
    category = fields.Nested(CategorySchema)
    # p_img = fields.File()


class TextsScheme(Schema):
    id = fields.String()
    title = fields.String()
    body = fields.String()
