from aitrados_api.models.base_model import Endpoint, APIVersion, EndpointParam, ParamLocation, ParamType, DataFormat


NEWS_LIST_REQUEST_DATA: Endpoint = Endpoint(
    name="news_list",
    path="news/list",
    version=APIVersion.V2,
    description="Get a list of news list.",
    mandatory_params=[],
    optional_params=[
        EndpointParam(
            name="from_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATETIME,
            required=True,
            description="Start date for filtering events",
        ),
        EndpointParam(
            name="to_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATETIME,
            required=True,
            description="End date for filtering events",
        ),
        EndpointParam(
            name="full_symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="full symbol:STOCK:US:TSLA",
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
            name="next_page_key",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            default=None,
            required=False,
            description="next_page_key",
        )



    ],
)
NEWS_LATEST_REQUEST_DATA: Endpoint = Endpoint(
    name="news_latest",
    path="news/latest",
    version=APIVersion.V2,
    description="Get a list of news list.",
    mandatory_params=[],
    optional_params=[

        EndpointParam(
            name="full_symbol",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="full symbol:STOCK:US:TSLA",
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
            default=5,
            required=False,
            description="Number of results to return (default 100, max 1001)",
        )


    ],
)