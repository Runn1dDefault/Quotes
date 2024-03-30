from rest_framework.filters import BaseFilterBackend


class ListFilter(BaseFilterBackend):
    view_param = "filter_by_fields"
    description = ""

    @staticmethod
    def _get_filters(request, fields: dict[str, str]) -> dict[str, list[str]]:
        filters = {}
        for param, source in fields.items():
            values = [value.strip() for value in request.query_params.get(param, "").split(",") if value.strip()]
            if values:
                filters[source] = values
        return filters

    def _get_view_params(self, view) -> dict[str, str]:
        attr = getattr(view, self.view_param)
        assert isinstance(attr, dict)
        return attr

    def filter_queryset(self, request, queryset, view):
        view_params = self._get_view_params(view)
        filters = self._get_filters(request, view_params)
        if filters:
            return queryset.filter(**filters)
        return queryset

    def get_schema_operation_parameters(self, view):
        view_params = self._get_view_params(view)

        return [
            {
                'name': param,
                'required': False,
                'in': 'query',
                'description': self.description,
                'schema': {
                    'type': 'string',
                }
            }
            for param, source in view_params.items()
        ]
