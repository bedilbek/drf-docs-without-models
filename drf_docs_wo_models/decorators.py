def custom_parameters(query_serializer=None, response_serializer=None):
    def decorator(view_method):
        data = {}
        if query_serializer:
            data['query_serializer'] = query_serializer()
        if response_serializer:
            data['response_serializer'] = response_serializer()
        view_method._scheme_params = data
        return view_method

    return decorator
