def custom_parameters(query_serializer=None):
    def decorator(view_method):
        data = {}
        if query_serializer:
            data['query_serializer'] = query_serializer()
        view_method._scheme_params = data
        return view_method

    return decorator
