from aitrados_api.models.base_model import Endpoint, APIVersion


SERVER_ADDRESS_INFO_REQUEST_DATA: Endpoint = Endpoint(
    name="server address_info",
    path="server/address_info",
    version=APIVersion.V2,
    description="Get server address information",
    mandatory_params=[

    ],
    optional_params=[

    ],
)