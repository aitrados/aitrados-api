from aitrados_api.models.base_model import Endpoint, APIVersion, EndpointParam, ParamLocation, ParamType, DataFormat
REFERENCE_REQUEST_DATA: Endpoint = Endpoint(
    name="asset_reference",
    path="{schema_asset}/reference/{country_symbol}",
    version=APIVersion.V2,
    description="Get reference data for a specific asset",
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
    ],
    optional_params=[]

)
OPTION_SEARCH_REQUEST_DATA: Endpoint = Endpoint(
    name="option_search",
    path="option/search/{schema_asset}/{country_symbol}/{option_type}/moneyness/{moneyness}",
    version=APIVersion.V2,
    description="Search options based on various parameters",
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
            description="country symbol (e.g., US:SPY)",
        ),
        EndpointParam(
            name="option_type",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="type of option (call, put)",
        ),
        EndpointParam(
            name="moneyness",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="moneyness of the option (in_the_money, out_of_the_money)",
        ),
    ],
    optional_params=[
        EndpointParam(
            name="ref_asset_price",
            location=ParamLocation.QUERY,
            param_type=ParamType.FLOAT,
            required=False,
            description="reference asset price for moneyness calculation",
        ),
        EndpointParam(
            name="strike_price",
            location=ParamLocation.QUERY,
            param_type=ParamType.FLOAT,
            required=False,

            description="specific strike price to filter options",
        ),
        EndpointParam(
            name="expiration_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATETIME,
            required=False,
            description="expiration date of the options",
        ),
        EndpointParam(
            name="limit",
            location=ParamLocation.QUERY,
            param_type=ParamType.INTEGER,
            default=100,
            required=False,
            description="number of results to return",
        ),
        EndpointParam(
            name="sort_by",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="sorting criteria for the results",
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

OPTIONS_EXPIRATION_DATE_LIST_REQUEST_DATA: Endpoint = Endpoint(
    name="options_expiration_date_list",
    path="option/expiration_date_list/{schema_asset}/{country_symbol}",
    version=APIVersion.V2,
    description="Get a list of option expiration dates for a specific asset",
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
            description="country symbol (e.g., US:SPY)",
        ),
    ],
    optional_params=[

    ],
)


STOCK_CORPORATE_ACTION_LIST_REQUEST_DATA: Endpoint = Endpoint(
    name="stock_corporate_action_list",
    path="stock/stock_corporate_action/list/{country_symbol}",
    version=APIVersion.V2,
    description="Get corporate actions (dividends, splits) for a specific stock",
    mandatory_params=[
        EndpointParam(
            name="country_symbol",
            location=ParamLocation.PATH,
            param_type=ParamType.STRING,
            required=True,
            description="country symbol (e.g., US:TSLA)",
        ),

        EndpointParam(
            name="from_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATETIME,
            required=True,
            description="Start date in YYYY-MM-DD format",
        ),


    ],
    optional_params=[

        EndpointParam(
            name="action_type",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            required=False,
            description="Type of corporate action: 'dividend' or 'split'",
        ),


        EndpointParam(
            name="to_date",
            location=ParamLocation.QUERY,
            param_type=ParamType.DATETIME,
            required=False,
            description="End date in YYYY-MM-DD format",
        ),

        EndpointParam(
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
            name="next_page_key",
            location=ParamLocation.QUERY,
            param_type=ParamType.STRING,
            default=None,
            required=False,
            description="next_page_key",
        )

    ],

)