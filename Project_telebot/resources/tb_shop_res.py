from flask_restful import Resource
from flask import request, jsonify

from models.models import Category, Product, Texts
from schemes.tb_shop_schemes import TextsScheme, CategorySchema, ProductSchema


class CategoryResource(Resource):

    def get(self, id=None):
        if not id:
            return CategorySchema().dump(Category.objects, many=True)
        return CategorySchema().dump(Category.objects(id=id).get())

    def post(self, id=None):

        if not id:
            instance = Category(**request.json).save()
            return CategorySchema().dump(instance)

        category = Category.objects(id=id).get()
        return CategorySchema().dump(category)

    def put(self, id):

        obj = Category.objects(id=id).get()
        obj.update(**request.json)
        return CategorySchema().dump(obj.reload())

    def delete(self, id):
        CategorySchema().dump(Category.objects(id=id).delete())
        return jsonify(**{id: 'deleted'})


class ProductResource(Resource):

    def get(self, id=None):
        if not id:
            return ProductSchema().dump(Product.objects, many=True)
        return ProductSchema().dump(Product.objects(id=id).get())

    def post(self):
        instance = Product(**request.json).save()
        return ProductSchema().dump(instance)

    def put(self, id):
        obj = Product.objects(id=id).get()
        obj.update(**request.json)
        return ProductSchema().dump(obj.reload())

    def delete(self, id):
        ProductSchema().dump(Product.objects(id=id).delete())
        return jsonify(**{id: 'deleted'})


class TextsResource(Resource):
    def get(self, id=None):
        if not id:
            return TextsScheme().dump(Texts.objects, many=True)
        return TextsScheme().dump(Texts.objects(id=id).get())

    def post(self):
        instance = Texts(**request.json).save()
        return TextsScheme().dump(instance)

    def put(self, id):
        obj = Texts.objects(id=id).get()
        obj.update(**request.json)
        return TextsScheme().dump(obj.reload())

    def delete(self, id):
        TextsScheme().dump(Texts.objects(id=id).delete())
        return jsonify(**{id: 'deleted'})
