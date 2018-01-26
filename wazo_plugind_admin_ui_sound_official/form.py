# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask_babel import lazy_gettext as l_
from wtforms.fields import (SubmitField,
                            StringField,
                            SelectField,
                            BooleanField)
from wtforms.validators import InputRequired, Length

from wazo_admin_ui.helpers.destination import DestinationHiddenField
from wazo_admin_ui.helpers.form import BaseForm


class SoundFilenameForm(BaseForm):
    format = StringField(l_('Format'))
    language = StringField(l_('Language'))
    text = StringField(l_('Text'))
    path = StringField(l_('Path'))
    submit = SubmitField(l_('Submit'))


class SoundForm(BaseForm):
    name = StringField(l_('Name'))
    submit = SubmitField(l_('Submit'))


class SoundDestinationForm(BaseForm):
    set_value_template = '{name}.{format} ({language})'

    filename = SelectField(l_('Filename'), choices=[], validators=[InputRequired(), Length(max=255)])
    name = DestinationHiddenField()
    language = DestinationHiddenField()
    format = DestinationHiddenField()
    skip = BooleanField(l_('Skip'))
    no_answer = BooleanField(l_('No Answer'))
