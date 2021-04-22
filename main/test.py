def tuple_to_sitedata_dict(**kwargs):
    for key, value in kwargs.items():
        if type(value) is str and "," in value:
            kwargs[key] = value.split(sep = ",")
    return kwargs

dict = tuple_to_sitedata_dict(a = "1, 2", b = "2, 3", c = "3, 4", d= 4)
print(dict)