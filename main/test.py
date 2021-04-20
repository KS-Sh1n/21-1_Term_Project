a = dict(first = "on", second = "on", third = "on")

def get_checked_site(form_):
    for value_tuple in form_.items():
        try:
            if value_tuple[1] == "on" and value_tuple[0] != "js_included":
                yield (value_tuple[0], )
            else:
                continue
        except:
            return

#result should be[(first,), (second,)]
b = get_checked_site(a)
print(len(list(b)))
print(len(list(b)))