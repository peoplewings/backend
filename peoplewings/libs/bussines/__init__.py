class BussinesModel(object).
    _fields_ = []
    
    def object_to_json(self):
        result = "{"
        for i in _fields_:
            result = '%s%s:%s,' % (result, i, self.'%s' % i)
        return result
