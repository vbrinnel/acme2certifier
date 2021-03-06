#!/usr/bin/python
# -*- coding: utf-8 -*-
""" django handler for acmesrv.py """
from __future__ import print_function
import json
from acme.models import Account, Authorization, Certificate, Challenge, Nonce, Order, Status

class DBstore(object):
    """ helper to do datebase operations """

    def __init__(self, debug=False, logger=None):
        """ init """
        self.logger = logger

    def account_add(self, data_dic):
        """ add account in database """
        self.logger.debug('DBStore.account_add({0})'.format(data_dic))
        account_list = self.account_lookup('jwk', data_dic['jwk'])
        if account_list:
            created = False
            aname = account_list['name']
        else:
            obj, created = Account.objects.update_or_create(name=data_dic['name'], defaults=data_dic)
            obj.save()
            aname = data_dic['name']
        return (aname, created)

    # django specific
    def account_getinstance(self, aname):
        """ get account instance """
        self.logger.debug('DBStore.account_getinstance({0})'.format(aname))
        return Account.objects.get(name=aname)

    def account_lookup(self, mkey, value):
        """ search account for a given id """
        self.logger.debug('DBStore.account_lookup({0}:{1})'.format(mkey, value))
        account_dict = Account.objects.filter(**{mkey: value}).values('id', 'jwk', 'name', 'contact', 'alg', 'created_at')[:1]
        if account_dict:
            result = account_dict[0]
        else:
            result = None
        return result

    def account_delete(self, aname):
        """ add account in database """
        self.logger.debug('DBStore.account_delete({0})'.format(aname))
        result = Account.objects.filter(name=aname).delete()
        return result

    def account_update(self, data_dic):
        """ update existing account """
        self.logger.debug('DBStore.account_update({0})'.format(data_dic))
        obj, _created = Account.objects.update_or_create(name=data_dic['name'], defaults=data_dic)
        obj.save()
        self.logger.debug('acct_id({0})'.format(obj.id))
        return obj.id

    def jwk_load(self, aname):
        """ looad account informatino and build jwk key dictionary """
        self.logger.debug('DBStore.jwk_load({0})'.format(aname))
        account_dict = Account.objects.filter(name=aname).values('jwk', 'alg')[:1]
        jwk_dict = {}
        if account_dict:
            jwk_dict = json.loads(account_dict[0]['jwk'].decode())
            jwk_dict['alg'] = account_dict[0]['alg']
        return jwk_dict

    def nonce_add(self, nonce):
        """ check if nonce is in datbase
        in: nonce
        return: rowid """
        self.logger.debug('DBStore.nonce_add({0})'.format(nonce))
        obj = Nonce(nonce=nonce)
        obj.save()
        return obj.id

    def nonce_check(self, nonce):
        """ ceck if nonce is in datbase
        in: nonce
        return: true in case nonce exit, otherwise false """
        self.logger.debug('DBStore.nonce_check({0})'.format(nonce))
        nonce_list = Nonce.objects.filter(nonce=nonce).values('nonce')[:1]
        return bool(nonce_list)

    def nonce_delete(self, nonce):
        """ delete nonce from datbase
        in: nonce """
        self.logger.debug('DBStore.nonce_delete({0})'.format(nonce))
        Nonce.objects.filter(nonce=nonce).delete()

    def order_add(self, data_dic):
        """ add order to database """
        self.logger.debug('DBStore.order_add({0})'.format(data_dic))
        # replace accountid with instance
        data_dic['account'] = self.account_getinstance(data_dic['account'])

        # replace orderstatus with an instance
        data_dic['status'] = self.status_getinstance(data_dic['status'], 'id')
        obj, _created = Order.objects.update_or_create(name=data_dic['name'], defaults=data_dic)
        obj.save()
        self.logger.debug('order_id({0})'.format(obj.id))
        return obj.id

    # django specific
    def order_getinstance(self, value=id, mkey='id'):
        """ get order instance """
        self.logger.debug('DBStore.order_getinstance({0}:{1})'.format(mkey, value))
        return Order.objects.get(**{mkey: value})

    # django specific
    def status_getinstance(self, value, mkey='id'):
        """ get account instance """
        self.logger.debug('DBStore.status_getinstance({0}:{1})'.format(mkey, value))
        return Status.objects.get(**{mkey: value})

    def authorization_add(self, data_dic):
        """ add authorization to database """
        self.logger.debug('DBStore.authorization_add({0})'.format(data_dic))

        # get some instance for DB insert
        if 'order' in data_dic:
            data_dic['order'] = self.order_getinstance(data_dic['order'], 'id')
        if 'status' in data_dic:
            data_dic['status'] = self.status_getinstance(data_dic['status'], 'name')

        # add authorization
        obj, _created = Authorization.objects.update_or_create(name=data_dic['name'], defaults=data_dic)
        obj.save()
        self.logger.debug('auth_id({0})'.format(obj.id))
        return obj.id

    def authorization_update(self, data_dic):
        """ update existing authorization """
        self.logger.debug('DBStore.authorization_update({0})'.format(data_dic))

        # get some instance for DB insert
        if 'status' in data_dic:
            data_dic['status'] = self.status_getinstance(data_dic['status'], 'name')

        # add authorization
        obj, _created = Authorization.objects.update_or_create(name=data_dic['name'], defaults=data_dic)
        obj.save()

        self.logger.debug('auth_id({0})'.format(obj.id))
        return obj.id

    def authorization_lookup(self, mkey, value, vlist=('type', 'value')):
        """ search account for a given id """
        self.logger.debug('authorization_lookup({0}:{1}:{2})'.format(mkey, value, vlist))
        authz_list = Authorization.objects.filter(**{mkey: value}).values(*vlist)[::1]
        return authz_list

    # django specific
    def authorization_getinstance(self, name):
        """ get authorization instance """
        self.logger.debug('DBStore.authorization_getinstance({0})'.format(name))
        return Authorization.objects.get(name=name)

    def challenge_add(self, data_dic):
        """ add challenge to database """
        self.logger.debug('DBStore.challenge_add({0})'.format(data_dic))

        # get order instance for DB insert
        data_dic['authorization'] = self.authorization_getinstance(data_dic['authorization'])

        # replace orderstatus with an instance
        data_dic['status'] = self.status_getinstance(data_dic['status'])

        # add authorization
        obj, _created = Challenge.objects.update_or_create(name=data_dic['name'], defaults=data_dic)
        obj.save()
        self.logger.debug('cid({0})'.format(obj.id))
        return obj.id

    def challenge_lookup(self, mkey, value, vlist=('type', 'token', 'status__name')):
        """ search account for a given id """
        self.logger.debug('challenge_lookup({0}:{1})'.format(mkey, value))
        challenge_list = Challenge.objects.filter(**{mkey: value}).values(*vlist)[:1]
        if challenge_list:
            result = challenge_list[0]
            if 'status__name' in result:
                result['status'] = result['status__name']
                del result['status__name']
            if 'authorization__name' in result:
                result['authorization'] = result['authorization__name']
                del result['authorization__name']
        else:
            result = None
        return result

    def challenge_update(self, data_dic):
        """ update challenge """
        self.logger.debug('challenge_update({0})'.format(data_dic))
        # replace orderstatus with an instance
        if 'status' in data_dic:
            data_dic['status'] = self.status_getinstance(data_dic['status'], 'name')
        obj, _created = Challenge.objects.update_or_create(name=data_dic['name'], defaults=data_dic)
        obj.save()

    def order_lookup(self, mkey, value, vlist=('name', 'notbefore', 'notafter', 'identifiers', 'status__name', 'account__name', 'expires')):
        """ search orders for a given ordername """
        self.logger.debug('order_lookup({0}:{1})'.format(mkey, value))
        order_list = Order.objects.filter(**{mkey: value}).values(*vlist)[:1]
        if order_list:
            result = order_list[0]
            if 'status__name' in result:
                result['status'] = result['status__name']
                del result['status__name']
            if 'account_name' in result:
                result['account'] = result['account__name']
                del result['account__name']
        else:
            result = None
        return result

    def certificate_add(self, data_dic):
        """ add csr/certificate to database """
        self.logger.debug('DBStore.certificate_add()')

        # get order instance for DB insert
        if 'order' in data_dic:
            data_dic['order'] = self.order_getinstance(data_dic['order'], 'name')
        # add certificate/CSR
        obj, _created = Certificate.objects.update_or_create(name=data_dic['name'], defaults=data_dic)
        obj.save()
        self.logger.debug('DBStore.certificate_add() ended with :{0}'.format(obj.id))
        return obj.id

    def order_update(self, data_dic):
        """ update order """
        self.logger.debug('order_update({0})'.format(data_dic))
        # replace orderstatus with an instance
        if 'status' in data_dic:
            data_dic['status'] = self.status_getinstance(data_dic['status'], 'name')
        obj, _created = Order.objects.update_or_create(name=data_dic['name'], defaults=data_dic)
        obj.save()

    def certificate_lookup(self, mkey, value, vlist=('name', 'csr', 'cert', 'order__name')):
        """ search certificate based on "something" """
        self.logger.debug('DBStore.certificate_lookup({0}:{1})'.format(mkey, value))
        certificate_list = Certificate.objects.filter(**{mkey: value}).values(*vlist)[:1]
        if certificate_list:
            result = certificate_list[0]
            if 'order__name' in result:
                result['order'] = result['order__name']
                del result['order__name']
        else:
            result = None
        self.logger.debug('DBStore.certificate_lookup() ended with: {0}'.format(result))
        return result

    def certificate_account_check(self, account_name, certificate):
        """ check issuer against certificate """
        self.logger.debug('DBStore.certificate_account_check({0})'.format(account_name))

        result = None
        certificate_list = self.certificate_lookup('cert_raw', certificate, ['name', 'order__name', 'order__account__name'])

        if certificate_list:
            if account_name:
                # if there is an acoount name validate it against the account_name from db-query
                if account_name == certificate_list['order__account__name']:
                    result = certificate_list['order']
            else:
                # no account name given (message signed with domain key
                result = certificate_list['order']

        self.logger.debug('DBStore.certificate_account_check() ended with: {0}'.format(result))
        return result
