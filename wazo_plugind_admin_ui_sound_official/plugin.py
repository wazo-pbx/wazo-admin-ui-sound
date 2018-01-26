# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask_babel import lazy_gettext as l_
from flask_menu.classy import register_flaskview

from wazo_admin_ui.helpers.plugin import create_blueprint
from wazo_admin_ui.helpers.destination import register_destination_form, register_listing_url

from .form import SoundDestinationForm
from .service import SoundService
from .view import SoundView, SoundListingView, SoundFileView

sound = create_blueprint('sound', __name__)


class Plugin(object):

    def load(self, dependencies):
        core = dependencies['flask']

        SoundView.service = SoundService()
        SoundView.register(sound, route_base='/sound')
        register_flaskview(sound, SoundView)

        SoundFileView.service = SoundService()
        SoundFileView.register(sound, route_base='/sound_files')
        register_flaskview(sound, SoundFileView)

        SoundListingView.service = SoundService()
        SoundListingView.register(sound, route_base='/sound_listing')

        register_destination_form('sound', l_('Sound'), SoundDestinationForm)

        register_listing_url('sound', 'sound.SoundListingView:list_json')

        core.register_blueprint(sound)
