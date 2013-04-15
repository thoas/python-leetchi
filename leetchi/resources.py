from .base import BaseApiModel

from .fields import (PrimaryKeyField, EmailField, CharField, BooleanField, DateTimeField,
                     IntegerField, ManyToManyField, ForeignKeyField, AmountField)


class User(BaseApiModel):
    id = PrimaryKeyField(api_name='ID')
    first_name = CharField(api_name='FirstName', required=True)
    last_name = CharField(api_name='LastName', required=True)
    password = CharField(api_name='Password', required=True)
    email = EmailField(api_name='Email', required=True)
    tag = CharField(api_name='Tag', required=True)
    can_register_mean_of_payment = BooleanField(api_name='CanRegisterMeanOfPayment')
    has_register_mean_of_payment = BooleanField(api_name='HasRegisterMeanOfPayment')
    creation_date = DateTimeField(api_name='CreationDate')
    update_date = DateTimeField(api_name='UpdateDate')
    ip_address = CharField(api_name='IP', required=True)
    birthday = CharField(api_name='Birthday')
    personal_wallet_amount = AmountField(api_name='PersonalWalletAmount')

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)


class Wallet(BaseApiModel):
    id = PrimaryKeyField(api_name='ID')

    tag = CharField(api_name='Tag')
    name = CharField(api_name='Name', required=True)

    description = CharField(api_name='Description', required=True)
    raising_goal_amount = AmountField(api_name='RaisingGoalAmount', required=True)
    expiration_date = DateTimeField(api_name='ExpirationDate', required=True)

    spent_amount = AmountField(api_name='SpentAmount')
    amount = AmountField(api_name='Amount')
    collected_amount = AmountField(api_name='CollectedAmount')
    remaining_amount = AmountField(api_name='RemainingAmount')
    contribution_limit_date = DateTimeField(api_name='ContributionLimitDate')
    is_closed = BooleanField(api_name='IsClosed')

    creation_date = DateTimeField(api_name='CreationDate')
    update_date = DateTimeField(api_name='UpdateDate')

    users = ManyToManyField(User, api_name='Owners')

    class Meta:
        verbose_name = 'wallet'
        verbose_name_plural = 'wallets'

    def __unicode__(self):
        return self.name


class PaymentCard(BaseApiModel):
    id = PrimaryKeyField(api_name='ID')
    tag = CharField(api_name='Tag', required=True)
    owner = ForeignKeyField(User, api_name='UserID', required=True)
    card_number = CharField(api_name='CardNumber', required=True)
    redirect_url = CharField(api_name='RedirectURL')
    return_url = CharField(api_name='ReturnURL', required=True)
    payment_url = CharField(api_name='PaymentURL')

    class Meta:
        verbose_name = 'card'
        verbose_name_plural = 'cards'


class Transfer(BaseApiModel):
    id = PrimaryKeyField(api_name='ID')
    tag = CharField(api_name='Tag', required=True)

    creation_date = DateTimeField(api_name='CreationDate')
    update_date = DateTimeField(api_name='UpdateDate')

    payer = ForeignKeyField(User, api_name='PayerID', required=True)
    beneficiary = ForeignKeyField(User, api_name='BeneficiaryID', required=True)

    amount = AmountField(api_name='Amount', required=True)

    payer_wallet = ForeignKeyField(Wallet, api_name='PayerWalletID', required=True)
    beneficiary_wallet = ForeignKeyField(Wallet, api_name='BeneficiaryWalletID', required=True)

    class Meta:
        verbose_name = 'transfer'
        verbose_name_plural = 'transfers'


class TransferRefund(BaseApiModel):
    id = PrimaryKeyField(api_name='ID')
    creation_date = DateTimeField(api_name='CreationDate')
    update_date = DateTimeField(api_name='UpdateDate')
    tag = CharField(api_name='Tag', required=True)

    transfer = ForeignKeyField(Transfer, api_name='TransferID', required=True)
    user = ForeignKeyField(User, api_name='UserID', required=True)

    class Meta:
        verbose_name = 'transfer-refund'
        verbose_name_plural = 'transfer-refunds'


class Contribution(BaseApiModel):
    id = PrimaryKeyField(api_name='ID')
    tag = CharField(api_name='Tag', required=True)
    wallet = ForeignKeyField(Wallet, api_name='WalletID', required=True)
    user = ForeignKeyField(User, api_name='UserID', required=True)
    creation_date = DateTimeField(api_name='CreationDate')
    update_date = DateTimeField(api_name='UpdateDate')
    amount = AmountField(api_name='Amount', required=True)
    client_fee_amount = AmountField(api_name='ClientFeeAmount')
    leetchi_fee_amount = AmountField(api_name='LeetchiFeeAmount')
    is_succeeded = BooleanField(api_name='IsSucceeded')
    is_completed = BooleanField(api_name='IsCompleted')
    payment_url = CharField(api_name='PaymentURL')
    template_url = CharField(api_name='TemplateURL')
    return_url = CharField(api_name='ReturnURL', required=True)
    register_mean_of_payment = BooleanField(api_name='RegisterMeanOfPayment')
    error = CharField(api_name='Error')
    payment_card = ForeignKeyField(PaymentCard, api_name='PaymentCardID')
    type = CharField(api_name='Type')  # type of transaction: payline, ogone
    culture = CharField(api_name='Culture')

    class Meta:
        verbose_name = 'contribution'
        verbose_name_plural = 'contributions'

    def is_success(self):
        return self.is_succeeded and self.is_completed


class Withdrawal(BaseApiModel):
    id = PrimaryKeyField(api_name='ID')
    tag = CharField(api_name='Tag', required=True)
    wallet = ForeignKeyField(Wallet, api_name='WalletID', required=True)
    user = ForeignKeyField(User, api_name='UserID', required=True)
    creation_date = DateTimeField(api_name='CreationDate')
    update_date = DateTimeField(api_name='UpdateDate')
    amount = AmountField(api_name='Amount', required=True)
    amount_without_fees = AmountField(api_name='AmountWithoutFees')
    client_fee_amount = AmountField(api_name='ClientFeeAmount')
    leetchi_fee_amount = AmountField(api_name='LeetchiFeeAmount')
    is_succeeded = BooleanField(api_name='IsSucceeded')
    is_completed = BooleanField(api_name='IsCompleted')

    bank_account_owner_name = CharField(api_name='BankAccountOwnerName', required=True)
    bank_account_owner_address = CharField(api_name='BankAccountOwnerAddress', required=True)
    bank_account_iban = CharField(api_name='BankAccountIBAN', required=True)
    bank_account_bic = CharField(api_name='BankAccountBIC', required=True)

    error = CharField(api_name='Error')

    class Meta:
        verbose_name = 'withdrawal'
        verbose_name_plural = 'withdrawals'


class Refund(BaseApiModel):
    id = PrimaryKeyField(api_name='ID')
    tag = CharField(api_name='Tag', required=True)
    creation_date = DateTimeField(api_name='CreationDate')
    update_date = DateTimeField(api_name='UpdateDate')

    user = ForeignKeyField(User, api_name='UserID', required=True)
    contribution = ForeignKeyField(Contribution, api_name='ContributionID', required=True)

    is_succeeded = BooleanField(api_name='IsSucceeded')
    is_completed = BooleanField(api_name='IsCompleted')

    error = CharField(api_name='Error')

    class Meta:
        verbose_name = 'refund'
        verbose_name_plural = 'refunds'

    def is_success(self):
        return self.is_succeeded and self.is_completed


class Operation(BaseApiModel):
    id = PrimaryKeyField(api_name='ID')
    tag = CharField(api_name='Tag', required=True)
    creation_date = DateTimeField(api_name='CreationDate')
    update_date = DateTimeField(api_name='UpdateDate')

    user = ForeignKeyField(User, api_name='UserID', required=True)
    wallet = ForeignKeyField(Wallet, api_name='WalletID', required=True)
    amount = AmountField(api_name='Amount', required=True)

    transaction_type = CharField(api_name='TransactionType')
    transaction_id = IntegerField(api_name='TransactionID')

    class Meta:
        verbose_name = 'operation'
        verbose_name_plural = 'operations'
