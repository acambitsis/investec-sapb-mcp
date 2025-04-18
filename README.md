# Investec SAPB MCP Server

## Overview

The `investec-sapb-mcp` project is a Python-based MCP (Model Context Protocol) server designed to interact with the [Investec SA private banking API](https://developer.investec.com/za/api-products/documentation/SA_PB_Account_Information). This server allows AI applications to perform actions against the Investec API—such as managing accounts, transactions, and beneficiary payments—using a standardized interface. By leveraging MCP, the project enables seamless integration between LLM Client that support MCP and the Investec API without the need for custom code for each integration.

### What is MCP?
Model Context Protocol (MCP) is an open standard introduced by Anthropic in late 2024 that standardizes how AI applications connect with external tools, data sources, and systems. Often described as a "USB-C port for AI applications," MCP creates a universal interface allowing any AI assistant to plug into any data source or service without requiring custom code for each integration.

MCP solves the integration complexity problem by transforming what was previously an "M×N problem" (requiring custom integrations between M AI applications and N tools/systems) into a simpler "M+N problem" through standardization. This significantly reduces development time and maintenance requirements.

---

## Installation

To set up the `investec-sapb-mcp` project, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/acambitsis/investec-sapb-mcp.git
   cd investec-sapb-mcp
   ```

2. **Install `uv` for package management**:
   `uv` is used for managing Python packages in this project. Follow the installation guide [here](https://docs.astral.sh/uv/getting-started/installation/) to set up `uv` on your system.

3. **Create and activate a virtual environment**:
   ```bash
   uv venv .venv
   source .venv/bin/activate  # On Unix/macOS
   # OR
   .venv\Scripts\activate     # On Windows
   ```

4. **Install dependencies**:
   Use `uv` to install the required packages:
   ```bash
   uv sync
   ```

5. **Set up environment variables**:
   Create a `.env` file in the root directory and add the following variables:
   ```
   INVESTEC_CLIENT_ID=your_client_id
   INVESTEC_CLIENT_SECRET=your_client_secret
   INVESTEC_API_KEY=your_api_key
   INVESTEC_USE_SANDBOX=true  # Set to false for production
   INVESTEC_TIMEOUT=30
   ```
   Replace `your_client_id`, `your_client_secret`, and `your_api_key` with your actual Investec API credentials.

   **⚠️ Security Warning**: Never hardcode API keys, client IDs, or secrets in the code. Always use environment variables or a secure vault.

---

## Usage

To use the `investec-sapb-mcp` server, follow these steps:

1. **Start the MCP server**:
   Test that the server runs with following command:
   ```bash
   uv run server.py
   ```

2. **Connect via an MCP-compatible AI application**:
   Use an AI application that supports MCP (e.g., Claude Desktop or 5ire) to connect to the server. The AI can then use the exposed tools to interact with the Investec API.

3. **Available Tools**:
   The server exposes several tools for interacting with the Investec API:
   - **`get_accounts`**: Retrieve all accounts for the authenticated user.
   - **`transfer_multiple`**: Transfer funds to one or multiple accounts.
   - **`pay_beneficiaries`**: Pay one or multiple beneficiaries.

   For detailed usage of each tool, refer to the docstrings in `server.py`.

### Example Usage
Here's an example of how an AI might use the `get_accounts` tool:
```markdown
**User Query**: "List all my accounts."

**AI Response**: "Here are your accounts:
- Account Name: Savings Account, Account Number: 123456789, Balance: 5000.00 ZAR
- Account Name: Cheque Account, Account Number: 987654321, Balance: 1500.00 ZAR"
```

---

## Testing

To run the tests for this project, follow these steps:

1. **Install test dependencies**:
   ```bash
   uv add pytest
   ```

2. **Run tests**:
   ```bash
   pytest tests/
   ```

   The tests use the sandbox environment by default. Ensure your `.env` file is configured correctly for testing.

---

## Contributing

We welcome contributions to the `investec-sapb-mcp` project. To contribute, follow these steps:

1. **Fork the repository**:
   Click the "Fork" button on the GitHub repository page.

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-improvement
   ```

3. **Make your changes**:
   Implement your feature or bug fix, ensuring to follow the project's coding standards.

4. **Submit a pull request**:
   Push your changes to your fork and submit a pull request to the main repository with a clear description of your changes.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

This `README.md` should provide everything you need to get started with the `investec-sapb-mcp` project. Let me know if you'd like me to adjust or add anything!