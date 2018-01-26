# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import jsonify, request, render_template, redirect, url_for, send_file, flash
from flask_babel import lazy_gettext as l_
from flask_classful import route
from flask_menu.classy import classy_menu_item
from io import BytesIO
from requests.exceptions import HTTPError

from wazo_admin_ui.helpers.classful import (BaseView,
                                            LoginRequiredView,
                                            flash_basic_form_errors)
from wazo_admin_ui.helpers.destination import listing_urls

from .form import SoundForm, SoundFilenameForm


class SoundView(BaseView):
    form = SoundForm
    resource = 'sound'

    @classy_menu_item('.sound', 'Sound Files', order=6, icon="file-sound-o")
    def index(self):
        return super(SoundView, self).index()

    def _index(self, form=None):
        try:
            resource_list = self.service.list()
            resource_list['items'] = [d for d in resource_list['items'] if d['name'] != 'system']
            for resource in resource_list['items']:
                resource['id'] = resource['name']
        except HTTPError as error:
            self._flash_http_error(error)
            return redirect(url_for('admin.Admin:get'))

        return render_template(self._get_template('list'),
                               form=self.form(),
                               resource_list=resource_list,
                               listing_urls=listing_urls)

    def _map_resources_to_form_errors(self, form, resources):
        form.populate_errors(resources.get('sound', {}))
        return form


class SoundFileView(BaseView):
    form = SoundFilenameForm
    resource = 'sound'

    @classy_menu_item('.advanced', l_('Advanced'), order=9)
    @classy_menu_item('.advanced.sound_system', l_('Sound Files System'), order=2, icon="file-sound-o")
    def sound_files_system(self):
        resource_list = self._get_sound_files_by_category('system')
        return render_template(self._get_template('list_system_files'),
                               form=self.form(),
                               resource_list=resource_list,
                               listing_urls=listing_urls)

    def list_files(self, category):
        resource_list = self._get_sound_files_by_category(category)
        return render_template(self._get_template('list_files'),
                               form=SoundFilenameForm(),
                               resource_list=resource_list,
                               listing_urls=listing_urls)

    def _get_sound_files_by_category(self, category):
        try:
            resource_list = self.service.get(category)
            for resource in resource_list['files']:
                resource['id'] = resource['name']
            return resource_list
        except HTTPError as error:
            self._flash_http_error(error)
            return redirect(url_for('admin.Admin:get'))

    def download_sound_filename(self, category, sound_filename):
        kwargs = {}
        if request.args.get('format'):
            kwargs.update({'format': request.args.get('format')})
        if request.args.get('language'):
            kwargs.update({'language': request.args.get('language')})

        binary_content = self.service.download_sound_filename(category,
                                                              sound_filename,
                                                              **kwargs)

        return send_file(
            BytesIO(binary_content),
            attachment_filename='{}.wav'.format(sound_filename),
            as_attachment=True,
            mimetype='audio/wav'
        )

    @route('/upload_sound_filename/<category>', methods=['POST'])
    def upload_sound_filename(self, category):
        if 'sound_filename' not in request.files:
            flash('[upload] Upload attempt with no file', 'error')
            return redirect(url_for('.{}:{}'.format(self.__class__.__name__,
                                                    'list_files'), category=category))

        file = request.files.get('sound_filename')

        form = self.form()
        resources = self._map_form_to_resources_post(form)

        if not form.csrf_token.validate(form):
            flash_basic_form_errors(form)
            return self._new(form)

        try:
            self.service.upload_sound_filename(category, file.filename, file.read(), **resources)
        except HTTPError as error:
            form = self._fill_form_error(form, error)
            self._flash_http_error(error)
            return self._new(form)

        return redirect(url_for('.{}:{}'.format(self.__class__.__name__,
                                                'list_files'), category=category))

    def delete_sound_filename(self, category, sound_filename):
        self.service.delete_sound_filename(category,
                                           sound_filename)

        return redirect(url_for('.{}:{}'.format(self.__class__.__name__,
                                                'list_files'), category=category))

    def _map_resources_to_form_errors(self, form, resources):
        form.populate_errors(resources.get('sound', {}))
        return form


class SoundListingView(LoginRequiredView):

    def list_json(self):
        sounds = self.service.list()
        results = []
        for sound in sounds['items']:
            for file in sound['files']:
                if sound['name'] == 'system':
                    for format in file['formats']:
                        results.append({'id': file['name'], 'text': self._prepare_sound_filename_infos(file, format)})
                else:
                    for format in file['formats']:
                        results.append({'id': format['path'], 'text': self._prepare_sound_filename_infos(file, format)})
        return jsonify({'results': results})

    def _prepare_sound_filename_infos(self, file, format):
        return '{}.{} ({})'.format(file['name'], format['format'], format['language'])
