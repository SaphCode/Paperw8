def confirmation_required(desc_fn):
    def inner(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if request.args.get('confirm') != '1':
                desc = desc_fn()
                return redirect(url_for('confirm', 
                    desc=desc, action_url=quote(request.url)))
            return f(*args, **kwargs)
        return wrapper
    return inner