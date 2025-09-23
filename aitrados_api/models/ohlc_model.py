from aitrados_api.models.base_model import Endpoint, APIVersion, EndpointParam, ParamLocation, ParamType, DataFormat


OHLC_LATEST_LIST_REQUEST_DATA: Endpoint = Endpoint(
    name="ohlc_latest_price",
    path="{schema_asset}/bars/{country_symbol}/{interval}/latest",
    version=APIVersion.V2,
    description="Get latest price data",
    mandatory_params=[
        EndpointParam(
            name="schema_asset",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="schema asset (stock, crypto, forex, etc.)",
        ),
        EndpointParam(
            name="country_symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="country symbol (e.g., US:TSLA)",
        ),
        EndpointParam(
            name="interval",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Time interval",
        ),

    ],
    optional_params=[EndpointParam(
        name="format",
        location=ParamLocation.QUERY,
        param_type=ParamType.STRING,
        default=DataFormat.JSON,
        required=False,
        description="data format (json, csv)",
    ),

        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            default=150,
            required=False,
            description="data count limit (default 150, max 1000)",
        ),
        EndpointParam(
            name="is_eth",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            default=0,
            required=False,
            description="Whether to include data for US stocks' extended trading hours (pre-market and post-market). 0 = No, 1 = Yes. Default is 0.",
        ), ],

)

OHLC_HISTORY_LIST_REQUEST_DATA: Endpoint = Endpoint(
    name="ohlc_price",
    path="{schema_asset}/bars/{country_symbol}/{interval}/from/{from_date}/to/{to_date}",
    version=APIVersion.V2,
    description="Get intraday price data",
    mandatory_params=[
        EndpointParam(
            name="schema_asset",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="schema asset (stock, crypto, forex, etc.)",
        ),
        EndpointParam(
            name="country_symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="country symbol (e.g., US:TSLA)",
        ),
        EndpointParam(
            name="interval",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="Time interval (1min, 5min, 15min, 30min, 1hour, 4hour)",
        ),
        EndpointParam(
            name="from_date",
            location=ParamLocation.PATH,
            param_type=ParamType.DATETIME,
            required=True,
            description="Start date in YYYY-MM-DD format",
        ),
        EndpointParam(
            name="to_date",
            location=ParamLocation.PATH,
            param_type=ParamType.DATETIME,
            required=True,
            description="End date in YYYY-MM-DD format",
        ),

    ],
    optional_params=[EndpointParam(
            name="format",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            default=DataFormat.JSON,
            required=False,
            description="data format (json, csv)",
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
            default=150,
            required=False,
            description="data count limit (default 150, max 1000)",
        ),
        EndpointParam(
            name="next_page_key",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            default=None,
            required=False,
            description="next_page_key",
        ),
        EndpointParam(
            name="is_eth",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            default=0,
            required=False,
            description="Whether to include data for US stocks' extended trading hours (pre-market and post-market). 0 = No, 1 = Yes. Default is 0.",
        )

    ],

)
