# Super Simple YNAB API Client

It really is. This isn't a fancy client, just a simple one.

## Requirements

* Python 3
* `requests`
* `requests-futures`
* A Personal Access Token generated from https://app.youneedabudget.com/settings/developer

## Usage

Since this is so simple, it should be self-explanatory. See the docstrings in the methods.
Some simple examples:

```python
ynab = YNABClient('your-personal-access-token')

# Get budgets:
budgets = ynab.budgets()

# Get payees:
payees = ynab.payees('my-budget-id')

# Get transactions:
transactions = ynab.transactions('my-budget-id')

# Update a transaction:
ynab.update_transaction('my-budget-id', 'transaction_id', {
	'key-to-update': 'new-value'
})

# Or, update multiple transactions:
ynab.update_transactions('my-budget-id', [
	'transaction-id-1': {'payee_id': 'new-payee-id'},
	'transaction-id-2': {'payee_id': 'new-payee-id'},
])
```

# License

[MIT](./LICENSE)
