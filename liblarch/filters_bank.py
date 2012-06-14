# -*- coding: utf-8 -*-
"""
    liblarch.filters_bank
    ~~~~~~~~~~~~~~~~~~~~~

    filters_bank stores all of GTG's filters in centralized place

    :copyright: Copyright (c) 2011-2012 by the liblarch team, see AUTHORS.
    :license: LGPLv3 or later, see LICENSE for details.
"""


class Filter(object):
    def __init__(self, func, req):
        self.func = func
        self.dic = {}
        self.tree = req

    def set_parameters(self, dic):
        if dic:
            self.dic = dic

    def is_displayed(self, node_id):
        if self.tree.has_node(node_id):
            task = self.tree.get_node(node_id)
        else:
            return False

        if self.dic:
            value = self.func(task, parameters=self.dic)
        else:
            value = self.func(task)

        if 'negate' in self.dic and self.dic['negate']:
            value = not value

        return value

    def get_parameters(self, param):
        return self.dic.get(param, None)

    def is_flat(self):
        """ Should be the final list flat """
        return self.get_parameters('flat')

    def is_transparent(self):
        """ Is this filter transparent? """
        return self.get_parameters('transparent')


class FiltersBank(object):
    """
    Stores filter objects in a centralized place.
    """

    def __init__(self,tree):
        """
        Create several stock filters:

        :workview: Tasks that are active, workable, and started
        :active: Tasks of status Active
        :closed: Tasks of status closed or dismissed
        :notag: Tasks with no tags
        """
        self.tree = tree
        self.available_filters = {}
        self.custom_filters = {}

    ##########################################

    def get_filter(self, filter_name):
        """ Get the filter object for a given name """
        if self.available_filters.has_key(filter_name):
            return self.available_filters[filter_name]
        elif self.custom_filters.has_key(filter_name):
            return self.custom_filters[filter_name]
        else:
            return None

    def list_filters(self):
        """ List, by name, all available filters """
        liste = self.available_filters.keys()
        liste += self.custom_filters.keys()
        return liste

    def add_filter(self, filter_name, filter_func, parameters=None):
        """
        Adds a filter to the filter bank 

        :filter_name: identifies the filter in the bank
        :returns: True if the filter was added, False if was already in the bank
        """
        if filter_name not in self.list_filters():
            negate = False
            if filter_name.startswith('!'):
                negate = True
                filter_name = filter_name[1:]
            else:
                filter_obj = Filter(filter_func,self.tree)
                filter_obj.set_parameters(parameters)
            self.custom_filters[filter_name] = filter_obj
            return True
        else:
            return False

    def remove_filter(self, filter_name):
        """
        Remove a filter from the bank.
        Only custom filters that were added here can be removed
        Return False if the filter was not removed
        """
        if not self.available_filters.has_key(filter_name):
            if self.custom_filters.has_key(filter_name):
                self.unapply_filter(filter_name)
                self.custom_filters.pop(filter_name)
                return True
            else:
                return False
        else:
            return False
