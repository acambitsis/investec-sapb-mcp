"""
Investec API MCP Server

This server provides MCP tools to interact with the Investec API.
"""

import logging
from datetime import date, datetime
from typing import Any, Dict, Optional, Union

# Import our configuration
from config import config
from investec_api.client import InvestecClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("investec-api-mcp")

# This will be installed from the requirements.txt
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    logger.error(
        "Error: MCP package not found. Please install it with 'uv pip install \"mcp[cli]\"'"
    )
    exit(1)

# Initialize FastMCP server
mcp = FastMCP("investec")

# Initialize the Investec client
client = InvestecClient(
    client_id=config.client_id,
    client_secret=config.client_secret,
    api_key=config.api_key,
    use_sandbox=config.use_sandbox,
    timeout=config.timeout,
)

# Log configuration values at debug level with sensitive data masked
logger.debug(
    "Configuration: client_id=%s, client_secret=%s, api_key=%s, use_sandbox=%s, timeout=%s",
    f"{config.client_id[:4]}..." if config.client_id else "Not set",
    "***" if config.client_secret else "Not set",
    "***" if config.api_key else "Not set",
    config.use_sandbox,
    config.timeout,
)


# Helper function to format dates properly
def format_date(date_value: Union[str, date, datetime]) -> str:
    """Format date to a human-readable string."""
    if isinstance(date_value, str):
        return date_value
    return date_value.strftime("%Y-%m-%d")


# Helper function for account details
def format_account(account: Dict[str, Any]) -> str:
    """Format account information into a readable string."""
    return f"""
Account Name: {account.get("account_name", "Unknown")}
Account Number: {account.get("account_number", "Unknown")}
Account Type: {account.get("product_name", "Unknown")}
Current Balance: {account.get("current_balance", 0)} {account.get("currency_code", "")}
Available Balance: {account.get("available_balance", 0)} {account.get("currency_code", "")}
"""


# Helper function for transaction details
def format_transaction(transaction: Dict[str, Any]) -> str:
    """Format transaction information into a readable string."""
    return f"""
Date: {transaction.get("transaction_date", "Unknown")}
Description: {transaction.get("description", "Unknown")}
Amount: {transaction.get("amount", 0)} {transaction.get("currency_code", "")}
Type: {transaction.get("transaction_type", "Unknown")}
Status: {transaction.get("status", "Unknown")}
"""


# MCP Tools


@mcp.tool()
async def get_accounts() -> str:
    """Get all accounts for the authenticated user."""
    try:
        accounts = client.get_accounts()
        if not accounts:
            return "No accounts found."

        account_info = []
        for account in accounts:
            account_dict = account.to_dict()
            account_info.append(format_account(account_dict))

        return "\n---\n".join(account_info)
    except Exception as e:
        return f"Error retrieving accounts: {str(e)}"


@mcp.tool()
async def get_account_balance(account_id: str) -> str:
    """Get the balance for a specific account.

    Args:
        account_id: The ID of the account
    """
    try:
        balance = client.get_account_balance(account_id)
        balance_dict = balance.to_dict()

        return f"""
Current Balance: {balance_dict.get("current_balance", 0)} {balance_dict.get("currency_code", "")}
Available Balance: {balance_dict.get("available_balance", 0)} {balance_dict.get("currency_code", "")}
"""
    except Exception as e:
        return f"Error retrieving account balance: {str(e)}"


@mcp.tool()
async def get_account_transactions(
    account_id: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    transaction_type: Optional[str] = None,
) -> str:
    """Get transactions for a specific account.

    Args:
        account_id: The ID of the account
        from_date: Start date for transactions (YYYY-MM-DD)
        to_date: End date for transactions (YYYY-MM-DD)
        transaction_type: Filter transactions by type
    """
    try:
        transactions = client.get_account_transactions(
            account_id,
            from_date=from_date,
            to_date=to_date,
            transaction_type=transaction_type,
        )

        if not transactions:
            return "No transactions found for the specified criteria."

        transaction_info = []
        for transaction in transactions[:10]:  # Limit to 10 transactions
            transaction_dict = transaction.to_dict()
            transaction_info.append(format_transaction(transaction_dict))

        result = "\n---\n".join(transaction_info)

        if len(transactions) > 10:
            result += f"\n\nShowing 10 of {len(transactions)} transactions."

        return result
    except Exception as e:
        return f"Error retrieving account transactions: {str(e)}"


@mcp.tool()
async def get_pending_transactions(account_id: str) -> str:
    """Get pending transactions for a specific account.

    Args:
        account_id: The ID of the account
    """
    try:
        pending = client.get_account_pending_transactions(account_id)

        if not pending:
            return "No pending transactions found."

        pending_info = []
        for transaction in pending:
            transaction_dict = transaction.to_dict()
            pending_info.append(format_transaction(transaction_dict))

        return "\n---\n".join(pending_info)
    except Exception as e:
        return f"Error retrieving pending transactions: {str(e)}"


@mcp.tool()
async def get_beneficiaries() -> str:
    """Get all beneficiaries for the authenticated user."""
    try:
        beneficiaries = client.get_beneficiaries()

        if not beneficiaries:
            return "No beneficiaries found."

        beneficiary_info = []
        for beneficiary in beneficiaries:
            beneficiary_dict = beneficiary.to_dict()
            beneficiary_info.append(f"""
Beneficiary ID: {beneficiary_dict.get("beneficiary_id", "Unknown")}
Name: {beneficiary_dict.get("name", "Unknown")}
Account Number: {beneficiary_dict.get("account_number", "Unknown")}
Bank: {beneficiary_dict.get("bank_name", "Unknown")}
Type: {beneficiary_dict.get("beneficiary_type", "Unknown")}
Status: {beneficiary_dict.get("status", "Unknown")}
Last Payment Amount: {beneficiary_dict.get("last_payment_amount", "Unknown")}
Last Payment Date: {beneficiary_dict.get("last_payment_date", "Unknown")}
""")

        return "\n---\n".join(beneficiary_info)
    except Exception as e:
        return f"Error retrieving beneficiaries: {str(e)}"


@mcp.tool()
async def get_beneficiary_categories() -> str:
    """Get beneficiary categories available to the authenticated user."""
    try:
        categories = client.get_beneficiary_categories()
        categories_dict = categories.to_dict()

        if not categories_dict:
            return "No beneficiary categories found."

        return f"""
ID: {categories_dict.get("id", "Unknown")}
Name: {categories_dict.get("name", "Unknown")}
Is Default: {categories_dict.get("is_default", "Unknown")}
"""
    except Exception as e:
        return f"Error retrieving beneficiary categories: {str(e)}"


@mcp.tool()
async def transfer_multiple(
    account_id: str,
    transfers: str,
    profile_id: Optional[str] = None,
) -> str:
    """Transfer funds to one or multiple accounts.

    Args:
        account_id: The source account ID
        transfers: JSON string representing a list of transfers with format:
                  [{"beneficiary_account_id": "ACCOUNT_ID",
                    "amount": "10.00",
                    "my_reference": "My Ref",
                    "their_reference": "Their Ref"}]
        profile_id: Optional profile ID
    """
    try:
        import json

        from investec_api.models.transfer import TransferItem

        # Parse the transfers JSON string into a list of dictionaries
        transfer_dicts = json.loads(transfers)

        # Convert the dictionaries to TransferItem objects
        transfer_items = []
        for transfer in transfer_dicts:
            transfer_item = TransferItem(
                beneficiary_account_id=transfer.get("beneficiary_account_id"),
                amount=transfer.get("amount"),
                my_reference=transfer.get("my_reference"),
                their_reference=transfer.get("their_reference"),
            )
            transfer_items.append(transfer_item)

        # Execute the transfer
        response = client.transfer_multiple(account_id, transfer_items, profile_id)
        response_dict = response.to_dict()

        # Format the response
        transfer_responses = response_dict.get("transfer_responses", [])
        if not transfer_responses:
            return "No transfer responses received."

        result = []
        for resp in transfer_responses:
            result.append(f"""
Payment Reference: {resp.get("payment_reference_number", "Unknown")}
Payment Date: {resp.get("payment_date", "Unknown")}
Status: {resp.get("status", "Unknown")}
Beneficiary Name: {resp.get("beneficiary_name", "Unknown")}
Beneficiary Account ID: {resp.get("beneficiary_account_id", "Unknown")}
Authorisation Required: {resp.get("authorisation_required", False)}
""")

        return "\n---\n".join(result)

    except Exception as e:
        return f"Error executing transfers: {str(e)}"


@mcp.tool()
async def pay_beneficiaries(account_id: str, payments: str) -> str:
    """Pay one or multiple beneficiaries.

    Args:
        account_id: The source account ID
        payments: JSON string representing a list of payments with format:
                 [{"beneficiary_id": "BENEFICIARY_ID",
                   "amount": "10.00",
                   "my_reference": "My Ref",
                   "their_reference": "Their Ref"}]
    """
    try:
        import json

        from investec_api.models.payment import BeneficiaryPaymentItem

        # Parse the payments JSON string into a list of dictionaries
        payment_dicts = json.loads(payments)

        # Convert the dictionaries to BeneficiaryPaymentItem objects
        payment_items = []
        for payment in payment_dicts:
            payment_item = BeneficiaryPaymentItem(
                beneficiary_id=payment.get("beneficiary_id"),
                amount=payment.get("amount"),
                my_reference=payment.get("my_reference"),
                their_reference=payment.get("their_reference"),
            )
            payment_items.append(payment_item)

        # Execute the payment
        response = client.pay_beneficiaries(account_id, payment_items)
        response_dict = response.to_dict()

        # Format the response
        payment_responses = response_dict.get("payment_responses", [])
        if not payment_responses:
            return "No payment responses received."

        result = []
        for resp in payment_responses:
            result.append(f"""
Payment Reference: {resp.get("payment_reference_number", "Unknown")}
Payment Date: {resp.get("payment_date", "Unknown")}
Status: {resp.get("status", "Unknown")}
Beneficiary Name: {resp.get("beneficiary_name", "Unknown")}
Beneficiary Account ID: {resp.get("beneficiary_account_id", "Unknown")}
Authorisation Required: {resp.get("authorisation_required", False)}
""")

        return "\n---\n".join(result)

    except Exception as e:
        return f"Error making beneficiary payments: {str(e)}"


@mcp.tool()
async def get_profiles() -> str:
    """Get all profiles for the authenticated user."""
    try:
        profiles = client.get_profiles()

        if not profiles:
            return "No profiles found."

        profile_info = []
        for profile in profiles:
            profile_dict = profile.to_dict()
            profile_info.append(f"""
Profile ID: {profile_dict.get("profile_id", "Unknown")}
Profile Name: {profile_dict.get("profile_name", "Unknown")}
Profile Type: {profile_dict.get("profile_type", "Unknown")}
""")

        return "\n---\n".join(profile_info)
    except Exception as e:
        return f"Error retrieving profiles: {str(e)}"


@mcp.tool()
async def get_profile_accounts(profile_id: str) -> str:
    """Get all accounts for a specific profile.

    Args:
        profile_id: The ID of the profile
    """
    try:
        accounts = client.get_profile_accounts(profile_id)

        if not accounts:
            return "No accounts found for this profile."

        account_info = []
        for account in accounts:
            account_dict = account.to_dict()
            account_info.append(format_account(account_dict))

        return "\n---\n".join(account_info)
    except Exception as e:
        return f"Error retrieving profile accounts: {str(e)}"


if __name__ == "__main__":
    # Check if required environment variables are set
    if not config.client_id or not config.client_secret or not config.api_key:
        logger.error("Error: Required environment variables are not set.")
        logger.error(
            "Please set INVESTEC_CLIENT_ID, INVESTEC_CLIENT_SECRET, and INVESTEC_API_KEY."
        )
        exit(1)

    # Initialize and run the server
    logger.info("Starting Investec API MCP server")
    mcp.run(transport="stdio")
