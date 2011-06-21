from ...requests import requests, wrappers
from .request import MongoRequest


def merge_dicts(dict1, dict2):
    def merge_key(key, dict1, dict2):
        if type(dict1[key]) == type(dict2[key]):
            if isinstance(dict1[key], dict):
                new_dict = dict(dict1[key])
                new_dict.update(dict2[key])
                return new_dict
            elif isinstance(dict1[key], list):
                new_list = list(dict1[key])
                new_list.extend(dict2[key])
                return new_list
        raise

    final_dict = {}
    for key in dict1:
        if key in dict2:
            final_dict[key] = merge_key(key, dict1, dict2)
        else:
            final_dict[key] = dict1[key]

    for key in dict2:
        if key not in dict1:
            final_dict[key] = dict2[key]
    return final_dict


class MongoWrapper(wrappers.RequestWrapper):
    class_map = wrappers.RequestWrapper.class_map.copy()

    def to_mongo(self):
        raise NotImplementedError()


@MongoWrapper.register_wrapper(requests.StoredItemsRequest)
class StoredItemsWrapper(wrappers.StoredItemsWrapper, MongoWrapper):

    def to_mongo(self):
        return MongoRequest()


@MongoWrapper.register_wrapper(requests.FilterRequest)
class FilterWrapper(wrappers.FilterWrapper, MongoWrapper):

    def to_mongo(self):
        expression = self.subject.to_mongo()
        expression.spec = merge_dicts(
            expression.spec,
            self.predicate.to_mongo())
        return expression


@MongoWrapper.register_wrapper(requests.AndRequest)
class AndWrapper(wrappers.AndWrapper, MongoWrapper):

    def to_mongo(self):
        return merge_dicts(
            self.subject.to_mongo(),
            self.other.to_mongo())


@MongoWrapper.register_wrapper(requests.OrRequest)
class OrWrapper(wrappers.OrWrapper, MongoWrapper):

    def to_mongo(self):
        return {"$or":
                [self.subject.to_mongo(),
                 self.other.to_mongo()]}


@MongoWrapper.register_wrapper(requests.LeRequest)
class LeWrapper(wrappers.LeWrapper, MongoWrapper):

    def to_mongo(self):
        return {self.subject.to_mongo():
                {"$lte":
                 self.other.to_mongo()}}


@MongoWrapper.register_wrapper(requests.GeRequest)
class GeWrapper(wrappers.GeWrapper, MongoWrapper):

    def to_mongo(self):
        return {self.subject.to_mongo():
                {"$gte":
                 self.other.to_mongo()}}


@MongoWrapper.register_wrapper(requests.LtRequest)
class LtWrapper(wrappers.LtWrapper, MongoWrapper):

    def to_mongo(self):
        return {self.subject.to_mongo():
                {"$lt":
                 self.other.to_mongo()}}


@MongoWrapper.register_wrapper(requests.GtRequest)
class GtWrapper(wrappers.GtWrapper, MongoWrapper):

    def to_mongo(self):
        return {self.subject.to_mongo():
                {"$gt":
                 self.other.to_mongo()}}


@MongoWrapper.register_wrapper(requests.NeRequest)
class NeWrapper(wrappers.NeWrapper, MongoWrapper):

    def to_mongo(self):
        return {self.subject.to_mongo():
                {"$ne":
                 self.other.to_mongo()}}


@MongoWrapper.register_wrapper(requests.EqRequest)
class EqWrapper(wrappers.BooleanOperationWrapper, MongoWrapper):

    def to_mongo(self):
        return {self.subject.to_mongo(): self.other.to_mongo()}


@MongoWrapper.register_wrapper(requests.LiteralRequest)
class LiteralWrapper(wrappers.LiteralWrapper, MongoWrapper):

    def to_mongo(self):
        return self.value


@MongoWrapper.register_wrapper(requests.AttributeRequest)
class AttributeWrapper(wrappers.AttributeWrapper, MongoWrapper):

    def to_mongo(self):
        return self.attr_name


@MongoWrapper.register_wrapper(requests.LenRequest)
class LenWrapper(wrappers.LenWrapper, MongoWrapper):

    def to_mongo(self):
        expression = self.subject.to_mongo()
        expression.count = True
        return expression


@MongoWrapper.register_wrapper(requests.OneRequest)
class OneWrapper(wrappers.OneWrapper, MongoWrapper):

    def to_mongo(self):
        expression = self.subject.to_mongo()
        expression.one = True
        return expression
