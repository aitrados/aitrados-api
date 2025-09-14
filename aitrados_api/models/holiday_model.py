from aitrados_api.models.base_model import Endpoint, APIVersion, EndpointParam, ParamLocation, ParamType, DataFormat
HOLIDAY_CODES_REQUEST_DATA: Endpoint = Endpoint(
    name="holiday_codes",
    path="holiday/holiday_codes/{country_iso_code}",
    version=APIVersion.V2,
    description="Get all holiday codes of a country.",
    mandatory_params=[EndpointParam(
            name="country_iso_code",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Country ISO code (e.g., US, CN)",
        ),
    ],
    optional_params=[


    ],
)


HOLIDAY_LIST_REQUEST_DATA: Endpoint = Endpoint(
    name="holiday_list",
    path="holiday/list",
    version=APIVersion.V2,
    description="Get a list of holiday list.",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="full_symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=True,
            description="full symbol:STOCK:US:TSLA",
        ),
        EndpointParam(
            name="holiday_code",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Holiday code",
        ),
        EndpointParam(
            name="from_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATETIME,
            required=False,
            description="Start date for filtering events",
        ),
        EndpointParam(
            name="to_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATETIME,
            required=False,
            description="End date for filtering events",
        ),
        EndpointParam(
            name="sort",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            default="asc",
            required=False,
            description="Sort direction (asc or desc)",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            default=100,
            required=False,
            description="Number of results to return (default 100, max 1001)",
        ),
        EndpointParam(
            name="format",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            default="csv",
            required=False,
            description="Data format (json, csv)",
        ),
        EndpointParam(
            name="next_page_key",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            default=None,
            required=False,
            description="next_page_key",
        )

    ],
)