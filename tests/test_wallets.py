import unittest

from .resources import handler, User, Wallet


class WalletsTest(unittest.TestCase):
    def test_create_wallet(self):
        params = {
            'first_name': 'Mark',
            'last_name': 'Zuckerberg',
            'email': 'mark@leetchi.com',
            'ip_address': '127.0.0.1',
            'tag': 'custom_information'
        }

        user = User(**params)
        user.save(handler)

        wallet_params = {
            'tag': 'user',
            'name': 'Mark Zuckerberg wallet',
            'description': 'Wallet of Mark Zuckerberg',
            'raising_goal_amount': 1200,
            'users': [user]
        }

        wallet = Wallet(**wallet_params)
        wallet.save(handler=handler)

        params = dict(wallet_params, **{
            'collected_amount': 0,
            'amount': 0,
            'spent_amount': 0,
            'is_closed': True
        })

        for k, v in params.items():
            self.assertEqual(getattr(wallet, k), v)

        w = Wallet.get(wallet.get_pk(), handler)

        for k, v in wallet_params.items():
            self.assertEqual(getattr(w, k), v)

        self.assertEqual(w.get_pk(), wallet.get_pk())

        self.assertEqual(w.users, [user])

    def test_related_wallet(self):
        user = User(**{
            'first_name': 'Mark',
            'last_name': 'Zuckerberg',
            'email': 'mark@leetchi.com',
            'ip_address': '127.0.0.1',
            'tag': 'custom_information'
        })
        user.save(handler)

        wallet = Wallet(**{
            'tag': 'user',
            'name': 'Mark Zuckerberg wallet',
            'description': 'Wallet of Mark Zuckerberg',
            'raising_goal_amount': 1200,
            'users': [user]
        })

        wallet.save(handler=handler)

        user = User.get(user.get_pk(), handler=handler)

        self.assertEqual(user.wallets, [wallet])
