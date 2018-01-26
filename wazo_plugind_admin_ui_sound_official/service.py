# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from wazo_admin_ui.helpers.service import BaseConfdService
from wazo_admin_ui.helpers.confd import confd


class SoundService(BaseConfdService):
    resource_confd = 'sounds'

    def download_sound_filename(self, sound_name, file_name, **kwargs):
        return confd.sounds.download_file(sound_name, file_name, **kwargs)

    def delete_sound_filename(self, sound_name, sound_filename, **kwargs):
        confd.sounds.delete_file(sound_name, sound_filename, **kwargs)

    def upload_sound_filename(self, sound_name, sound_filename, binary_content, **kwargs):
        confd.sounds.upload_file(sound_name, sound_filename, binary_content, **kwargs)
