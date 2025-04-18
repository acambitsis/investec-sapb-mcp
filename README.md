# Investec API Python Client

A high-quality, typed Python wrapper for the Investec Open Banking API.

## Features

- Full support for all Investec API endpoints
- Type hints throughout for better code completion and error prevention
- Clean, consistent API for easy integration
- Proper error handling with custom exceptions
- Handles authentication transparently
- Model Context Protocol (MCP) server for integration with AI assistants

## Usage

### Setup

1. Clone the repository
2. Set up your environment variables (see `.env.example`)
3. Use the client directly in your code

### Authentication

```python
from investec_api import InvestecClient

# Initialize the client
client = InvestecClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    api_key="your_api_key",
    use_sandbox=True,  # Set to False for production
)
```

### Get Accounts

```python
# Get all accounts
accounts = client.get_accounts()

# Print account information
for account in accounts:
    print(f"Account ID: {account.account_id}")
    print(f"Name: {account.account_name}")
    print(f"Type: {account.product_name}")
    print("---")

    # Get account balance
    balance = client.get_account_balance(account.account_id)
    print(f"Current balance: {balance.current_balance} {balance.currency}")
    print(f"Available balance: {balance.available_balance} {balance.currency}")
```

### Get Transactions

```python
from datetime import date, timedelta

# Date range for transactions (last 30 days)
from_date = date.today() - timedelta(days=30)
to_date = date.today()

# Get transactions for an account
transactions = client.get_account_transactions(
    account_id="account_id_here",
    from_date=from_date,
    to_date=to_date,
    include_pending=True
)

for txn in transactions:
    txn_type = "DEBIT" if txn.type.value == "DEBIT" else "CREDIT"
    print(f"{txn.transaction_date}: {txn_type} {txn.amount} - {txn.description}")
```

### Transfer Funds

```python
from investec_api.models import TransferItem
from decimal import Decimal

# Create transfer items
transfers = [
    TransferItem(
        beneficiary_account_id="beneficiary_account_id_here",
        amount=Decimal("100.00"),
        my_reference="Payment reference",
        their_reference="Their reference"
    )
]

# Execute transfer
result = client.transfer_multiple(
    account_id="source_account_id_here",
    transfers=transfers
)

# Check results
for response in result.transfer_responses:
    print(f"Transfer reference: {response.payment_reference_number}")
    print(f"Status: {response.status}")
    print(f"Authorization required: {response.authorisation_required}")
```

### Pay Beneficiaries

```python
from investec_api.models import BeneficiaryPaymentItem
from decimal import Decimal

# First get all beneficiaries
beneficiaries = client.get_beneficiaries()

# Create payment items
payments = [
    BeneficiaryPaymentItem(
        beneficiary_id=beneficiaries[0].beneficiary_id,
        amount=Decimal("250.00"),
        my_reference="Monthly payment",
        their_reference="Invoice #12345"
    )
]

# Execute payment
result = client.pay_beneficiaries(
    account_id="source_account_id_here",
    payments=payments
)

# Check results
for response in result.transfer_responses:
    print(f"Payment reference: {response.payment_reference_number}")
    print(f"Status: {response.status}")
```

## Error Handling

```python
from investec_api import InvestecAPIError, InvestecAuthError, InvestecRequestError, InvestecRateLimitError

try:
    client.get_accounts()
except InvestecAuthError as e:
    print(f"Authentication failed: {e}")
except InvestecRateLimitError as e:
    print(f"Rate limit hit: {e}, status code: {e.status_code}")
except InvestecRequestError as e:
    print(f"API request failed: {e}, status code: {e.status_code}")
except InvestecAPIError as e:
    print(f"General API error: {e}")
```

## Documentation

For detailed API documentation, see the [Investec Open API documentation](https://developer.investec.com/za/api-products).

## License

MIT

## Development

### Setup

1. Clone the repository
2. Install dependencies:

```bash
uv pip install -r requirements.txt
```

3. Set up your environment variables (copy `.env.example` to `.env` and fill in your credentials)

### Running Tests

Run the tests using Python's module approach to ensure proper imports:

```bash
python -m pytest
```

This will run all tests in the `tests/` directory.

## MCP Server

This project includes an MCP server that provides tools to interact with the Investec API through the Model Context Protocol (MCP).

### MCP Features

The server exposes the following tools:

- `get_accounts`: Get all accounts for the authenticated user
- `get_account_balance`: Get the balance for a specific account
- `get_account_transactions`: Get transactions for a specific account
- `get_pending_transactions`: Get pending transactions for a specific account
- `get_beneficiaries`: Get all beneficiaries for the authenticated user
- `get_profiles`: Get all profiles for the authenticated user
- `get_profile_accounts`: Get all accounts for a specific profile

### Running the MCP Server

To run the server:

```bash
# First set up your authentication (see above)
# Then run the server
uv run server.py
```

### Integrating with Claude for Desktop

1. Install Claude for Desktop from https://claude.ai/
2. Configure Claude for Desktop to use this MCP server:

Open the Claude for Desktop configuration file at:
- MacOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%AppData%\Claude\claude_desktop_config.json`

Add the following to the configuration:

```json
{
    "mcpServers": {
        "investec": {
            "command": "uv",
            "args": [
                "--directory",
                "/ABSOLUTE/PATH/TO/investec-api-mcp",
                "run",
                "server.py"
            ]
        }
    }
}
```

Replace `/ABSOLUTE/PATH/TO/investec-api-mcp` with the absolute path to this directory.

3. Restart Claude for Desktop

### Example MCP Usage

Once connected to Claude for Desktop, you can use commands like:

- "Show me all my accounts"
- "What's my current balance on account [account_id]?"
- "Show me recent transactions for account [account_id]"
- "Are there any pending transactions on my account [account_id]?"
- "List all my beneficiaries" 
- "Show me all my profiles"

