import unittest
import time

try:
    from selenium import selenium
except ImportError:
    use_selenium = False
else:
    use_selenium = True

from .resources import handler, User, Wallet, Contribution, get_bank_account


class ContributionsTest(unittest.TestCase):
    def setUp(self):
        global use_selenium

        if use_selenium:
            try:
                self.selenium = selenium("localhost",
                                         4444, "*firefox", "http://www.google.com")

                self.selenium.start()
            except Exception:
                use_selenium = False

    def test_create_contribution(self):
        user = User(**{
            'first_name': 'Mark',
            'last_name': 'Zuckerberg',
            'email': 'mark@leetchi.com',
            'ip_address': '127.0.0.1',
            'tag': 'custom_information',
            'can_register_mean_of_payment': True
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

        new_user = User(**{
            'first_name': 'Bill',
            'last_name': 'Gates',
            'email': 'bill@leetchi.com',
            'ip_address': '127.0.0.1',
            'tag': 'custom_information'
        })

        new_user.save(handler)

        new_wallet = Wallet(**{
            'tag': 'user',
            'name': 'Bill Gates wallet',
            'description': 'Wallet of Bill Gates',
            'raising_goal_amount': 15200,
            'users': [new_user]
        })

        new_wallet.save(handler=handler)

        params = {
            'tag': 'project',
            'user': user,
            'wallet': new_wallet,
            'amount': 1000,
            'return_url': 'http://ulule.com',
            'client_fee_amount': 0,
            'register_mean_of_payment': True
        }

        contribution = Contribution(**params)

        contribution.save(handler)

        self.assertEqual(contribution.user_id, user.get_pk())
        self.assertEqual(contribution.wallet_id, new_wallet.get_pk())
        self.assertEqual(contribution.payment_url is None, False)

        params = {
            'tag': 'project',
            'user': user,
            'wallet_id': 0,
            'amount': 1000,
            'return_url': 'http://ulule.com',
            'client_fee_amount': 0,
            'register_mean_of_payment': True
        }

        contribution = Contribution(**params)

        contribution.save(handler)

        self.assertEqual(contribution.user_id, user.get_pk())
        self.assertEqual(contribution.wallet_id, 0)
        self.assertEqual(contribution.payment_url is None, False)

        if use_selenium:
            self.selenium.open(contribution.payment_url)

            bank_account = get_bank_account()

            self.selenium.type('//*[@id="number"]', bank_account['number'])
            self.selenium.type('//*[@name="expirationDate_month"]', bank_account['expiration']['month'])
            self.selenium.type('//*[@name="expirationDate_year"]', bank_account['expiration']['year'])
            self.selenium.type('//*[@id="cvv"]', bank_account['cvv'])

            #self.selenium.click('//*[@id="submitButton"]')

            time.sleep(10)

            contribution = Contribution.get(contribution.get_pk(), handler)

            self.assertEqual(contribution.is_succeeded, True)
            self.assertEqual(contribution.is_completed, True)

            wallet = Wallet.get(new_wallet.get_pk(), handler)

            self.assertEqual(wallet.collected_amount, 1000)
            self.assertEqual(wallet.amount, 1000)
            self.assertEqual(wallet.spent_amount, 0)
