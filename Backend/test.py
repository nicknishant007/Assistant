import asyncio

from services.notion.oauth import (
    discover_mcp_oauth,
    register_mcp_client,
)

from config.settings import settings


async def main():

    print("\n==============================")
    print("STEP 1: OAuth Discovery")
    print("==============================")

    metadata = await discover_mcp_oauth()

    print("\nAuthorization Endpoint:")
    print(
        metadata.get(
            "authorization_endpoint"
        )
    )

    print("\nToken Endpoint:")
    print(
        metadata.get(
            "token_endpoint"
        )
    )

    print("\nRegistration Endpoint:")
    print(
        metadata.get(
            "registration_endpoint"
        )
    )

    print("\nPKCE:")
    print(
        metadata.get(
            "code_challenge_methods_supported"
        )
    )

    print("\n==============================")
    print("STEP 2: Client Registration")
    print("==============================")

    credentials = await register_mcp_client(
        metadata=metadata,
        redirect_uri=settings.NOTION_REDIRECT_URI,
    )

    print("\nClient ID:")
    print(
        credentials.get(
            "client_id"
        )
    )

    print("\nClient Secret Returned:")
    print(
        bool(
            credentials.get(
                "client_secret"
            )
        )
    )


if __name__ == "__main__":
    asyncio.run(main())