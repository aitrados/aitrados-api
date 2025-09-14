from aitrados_api.models.base_model import Endpoint, APIVersion, EndpointParam, ParamLocation, ParamType, DataFormat
EVENT_LIST_REQUEST_DATA: Endpoint = Endpoint(
    name="economic_calendar_event_list",
    path="economic_calendar/event_list",
    version=APIVersion.V2,
    description="Get a list of economic calendar events.",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="country_iso_code",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Country ISO code (e.g., US, CN)",
        ),
        EndpointParam(
            name="event_code",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Event code",
        ),
        EndpointParam(
            name="source_id",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Source ID, length 64",
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

EVENT_REQUEST_DATA: Endpoint = Endpoint(
    name="economic_calendar_even",
    path="economic_calendar/event",
    version=APIVersion.V2,
    description="Get an economic calendar event.",
    mandatory_params=[],
    optional_params=[

        EndpointParam(
            name="country_iso_code",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Country ISO code (e.g., US, CN)",
        ),
        EndpointParam(
            name="event_code",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Event code",
        ),
        EndpointParam(
            name="source_id",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Source ID, length 64",
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
            required=False,
            description="Sort direction (asc or desc)",
        ),
    ],
)

EVENT_CODES_REQUEST_DATA: Endpoint = Endpoint(
    name="economic_calendar_event_codes",
    path="economic_calendar/event_codes/{country_iso_code}",
    version=APIVersion.V2,
    description="Get all economic calendar event codes.",
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