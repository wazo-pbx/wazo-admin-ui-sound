# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import jsonify, request, render_template, redirect, url_for, send_file, flash
from flask_babel import lazy_gettext as l_
from flask_classful import route
from flask_menu.classy import classy_menu_item
from io import BytesIO
from requests.exceptions import HTTPError

from wazo_admin_ui.helpers.classful import (
    BaseView,
    LoginRequiredView,
    flash_basic_form_errors,
)
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
        except HTTPError as error:
            self._flash_http_error(error)
            return redirect(url_for('admin.Admin:get'))

        sounds = []
        for sound in resource_list['items']:
            if sound['name'] == 'system':
                continue
            sound['id'] = sound['name']
            sounds.append(sound)

        resource_list['items'] = sounds

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
            sound = self.service.get(category)
        except HTTPError as error:
            self._flash_http_error(error)
            return redirect(url_for('admin.Admin:get'))

        for file_ in sound['files']:
            file_['id'] = file_['name']

        return sound

    def download_sound_filename(self, category, filename):
        binary_content = self.service.download_sound_filename(
            category,
            filename,
            format_=request.args.get('format'),
            language=request.args.get('language'),
        )

        return send_file(
            BytesIO(binary_content),
            attachment_filename='{}.wav'.format(filename),
            as_attachment=True,
            mimetype='audio/wav'
        )

    @route('/upload_sound_filename/<category>', methods=['POST'])
    def upload_sound_filename(self, category):
        if 'filename' not in request.files:
            flash('[upload] Upload attempt with no file', 'error')
            return redirect(url_for('.SoundFileView:list_files', category=category))

        file_ = request.files.get('filename')

        form = self.form()
        resources = self._map_form_to_resources_post(form)

        if not form.csrf_token.validate(form):
            flash_basic_form_errors(form)
            return self._new(form)

        try:
            self.service.upload_sound_filename(category, file_.filename, file_.read(), **resources)
        except HTTPError as error:
            form = self._fill_form_error(form, error)
            self._flash_http_error(error)
            return self._new(form)

        return redirect(url_for('.SoundFileView:list_files', category=category))

    def delete_sound_filename(self, category, filename):
        # XXX: this remove filename from every language/format
        self.service.delete_sound_filename(category, filename)
        return redirect(url_for('.SoundFileView:list_files', category=category))

    def _map_resources_to_form_errors(self, form, resources):
        form.populate_errors(resources.get('sound', {}))
        return form


class SoundListingView(LoginRequiredView):

    def list_json(self):
        sounds = self.service.list()
        results = []
        for sound in sounds['items']:
            for file_ in sound['files']:
                for format_ in file_['formats']:
                    results.append({
                        'text': '{}.{} ({})'.format(file_['name'], format_['format'], format_['language']),
                        'id': file_['name'] if sound['name'] == 'system' else file_['path'],
                    })

        return jsonify({'results': results})
