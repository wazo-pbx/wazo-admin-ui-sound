# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask_babel import lazy_gettext as l_

from wazo_admin_ui.helpers.destination import register_destination_form

from .form import SoundDestinationForm


class Plugin(object):

    def load(self, dependencies):
        register_destination_form('sound', l_('Sound'), SoundDestinationForm)
