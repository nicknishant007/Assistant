def resolve_variables(
    params: dict,
    step_results: dict
):

    resolved = {}

    for key, value in params.items():

        if (
            isinstance(value, str)
            and value.startswith("$")
        ):

            path = value[1:]

            parts = path.split(".")

            if len(parts) != 2:

                raise ValueError(
                    f"Invalid variable reference: {value}"
                )

            step_id = parts[0]

            field_name = parts[1]

            if step_id not in step_results:

                raise ValueError(
                    f"Step '{step_id}' not found"
                )

            result = step_results[
                step_id
            ]

            if field_name not in result:

                raise ValueError(
                    f"Field '{field_name}' not found in step '{step_id}'"
                )

            resolved[key] = result[
                field_name
            ]

        else:

            resolved[key] = value

    return resolved