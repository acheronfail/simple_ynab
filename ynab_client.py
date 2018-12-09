import requests
from requests_futures.sessions import FuturesSession

# TODO: throttle requests in line with YNAB's rate limits
# TODO: use "server_knowledge" in transactions endpoints

class YNABClient:
  """
  A super simple client that interfaces with the YNAB API.
  This uses the `https://api.youneedabudget.com/v1` API and you'll need to have
  a YNAB Personal Access Token.
  """

  def __init__(self, auth_token):
    self.__auth_token = auth_token
    self.__base_url = 'https://api.youneedabudget.com/v1'

  def _headers(self):
    return {'Authorization': 'Bearer {}'.format(self.__auth_token)}

  def _get(self, path):
    url = '{base_url}{path}'.format(base_url=self.__base_url, path=path)
    r = requests.get(url, headers=self._headers())
    r.raise_for_status()
    return r.json()['data']

  def _put(self, path, json):
    url = '{base_url}{path}'.format(base_url=self.__base_url, path=path)
    r = requests.put(url, json=json, headers=self._headers())
    r.raise_for_status()
    return r.json()['data']

  def _patch(self, path, json):
    url = '{base_url}{path}'.format(base_url=self.__base_url, path=path)
    r = requests.patch(url, json=json, headers=self._headers())
    r.raise_for_status()
    return r.json()['data']

  # User

  def user(self):
    """Returns authenticated user information"""
    return self._get('/user')['user']

  # Budgets

  def budgets(self):
    """Returns budgets list with summary information"""
    return self._get('/budgets')['budgets']

  def budget(self, budget_id):
    """Returns a single budget with all related entities.
    This resource is effectively a full budget export.
    """
    url = '/budgets/{}'.format(budget_id)
    return self._get(url)['budget']

  def budget_settings(self, budget_id):
    """Returns settings for a budget"""
    url = '/budgets/{}/settings'.format(budget_id)
    return self._get(url)

  # Accounts

  def accounts(self, budget_id):
    """Returns all accounts"""
    url = '/budgets/{}/accounts'.format(budget_id)
    return self._get(url)['accounts']

  def account(self, budget_id, account_id):
    """Returns a single account"""
    url = '/budgets/{}/accounts/{}'.format(budget_id, account_id)
    return self._get(url)['accounts']

  # Categories

  def categories(self, budget_id):
    """Returns all categories grouped by category group.
    Amounts (budgeted, activity, balance, etc.) are specific to the current
    budget month (UTC).
    """
    url = '/budgets/{}/categories'.format(budget_id)
    return self._get(url)['category_groups']

  def category(self, budget_id, category_id):
    """Returns a single category. Amounts (budgeted, activity, balance, etc.)
    are specific to the current budget month (UTC).
    """
    url = '/budgets/{}/categories/{}'.format(budget_id, category_id)
    return self._get(url)['category']

  def category_month(self, budget_id, month, category_id):
    """Returns a single category for a specific budget month.
    Amounts (budgeted, activity, balance, etc.) are specific to the current
    budget month (UTC).
    """
    url = '/budgets/{}/months/{}/categories/{}'.format(budget_id, month, category_id)
    return self._get(url)['category']

  def update_category_month(self, budget_id, month, category_id, month_category):
    """Update an existing month category"""
    url = '/budgets/{}/months/{}/categories/{}'.format(budget_id, month, category_id)
    return self._patch(url, json={'month_category': month_category})['category']

  # Payees

  def payee(self, budget_id, payee_id):
    url = '/budgets/{}/payees/{}'.format(budget_id, payee_id)
    return self._get(url)['payee']

  def payees(self, budget_id):
    url = '/budgets/{}/payees'.format(budget_id)
    return self._get(url)['payees']

  # Months

  def months(self, budget_id):
    """Returns all budget months"""
    url = '/budgets/{}/months'.format(budget_id)
    return self._get(url)['months']

  def month(self, budget_id, month):
    """Returns a single budget month"""
    url = '/budgets/{}/months/{}'.format(budget_id, month)
    return self._get(url)['month']

  # Transactions

  def transactions(self, budget_id):
    """Returns budget transactions"""
    url = '/budgets/{}/transactions'.format(budget_id)
    return self._get(url)['transactions']

  def add_transactions(self, budget_id, transactions):
    """Creates a single transaction or multiple transactions. If you provide a
    body containing a ‘transaction’ object, a single transaction will be created
    and if you provide a body containing a ‘transactions’ array, multiple
    transactions will be created.
    """
    url = '/budgets/{}/transactions'.format(budget_id)
    return self._post(url, json=transactions)

  def account_transactions(self, budget_id, account_id):
    """Returns all transactions for a specified account"""
    url = '/budgets/{}/accounts/{}/transactions'.format(budget_id, account_id)
    return self._get(url)['transactions']

  def category_transactions(self, budget_id, category_id):
    """Returns all transactions for a specified category"""
    url = '/budgets/{}/categories/{}/transactions'.format(budget_id, category_id)
    return self._get(url)['transactions']

  def payee_transactions(self, budget_id, payee_id):
    """Returns all transactions for a specified payee"""
    url = '/budgets/{}/payees/{}/transactions'.format(budget_id, payee_id)
    return self._get(url)['transactions']

  def transaction(self, budget_id, transaction_id):
    """Returns a single transaction"""
    url = '/budgets/{}/transactions/{}'.format(budget_id, transaction_id)
    return self._get(url)['transaction']

  def update_transaction(self, budget_id, transaction_id, transaction):
    """Updates a single transaction"""
    url = '/budgets/{}/transactions/{}'.format(budget_id, transaction_id)
    return self._put(url, json={'transaction': transaction})['transaction']

  def update_transactions(self, budget_id, transactions):
    """
    Updates multiple transactions.
    Pass transactions as a dictionary with transaction id's for keys, and the
    transaction's update for values. For example, updating the payee for
    multiple transactions:

    {
      'transaction-id-1': {'payee_id': 'new-payee-id'},
      'transaction-id-2': {'payee_id': 'new-payee-id'},
      'etc'
    }
    """
    fs = FuturesSession()
    futures = []

    for i, tx_id in enumerate(transactions):
      path = '/budgets/{}/transactions/{}'.format(budget_id, tx_id)
      url = '{base_url}{path}'.format(base_url=self.__base_url, path=path)
      futures.append(fs.put(url, json={'transaction': transactions[tx_id]}, headers=self._headers()))

    while len(futures) > 0:
      print('\r{} remaining...'.format(len(futures)), end='')
      future = futures.pop(0)
      r = future.result()
      r.raise_for_status()

    print('\rNumber of transactions updated: {}'.format(len(transactions)), end='')
