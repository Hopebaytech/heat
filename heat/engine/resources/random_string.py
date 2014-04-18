#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import random
import string

from six.moves import xrange

from heat.engine import constraints
from heat.engine import properties
from heat.engine import resource


class RandomString(resource.Resource):
    '''
    A resource which generates a random string.

    This is useful for configuring passwords and secrets on services.
    '''
    PROPERTIES = (
        LENGTH, SEQUENCE, SALT,
    ) = (
        'length', 'sequence', 'salt',
    )

    properties_schema = {
        LENGTH: properties.Schema(
            properties.Schema.INTEGER,
            _('Length of the string to generate.'),
            default=32,
            constraints=[
                constraints.Range(1, 512),
            ]
        ),
        SEQUENCE: properties.Schema(
            properties.Schema.STRING,
            _('Sequence of characters to build the random string from.'),
            default='lettersdigits',
            constraints=[
                constraints.AllowedValues(['lettersdigits', 'letters',
                                           'lowercase', 'uppercase',
                                           'digits', 'hexdigits',
                                           'octdigits']),
            ]
        ),
        SALT: properties.Schema(
            properties.Schema.STRING,
            _('Value which can be set or changed on stack update to trigger '
              'the resource for replacement with a new random string . The '
              'salt value itself is ignored by the random generator.')
        ),
    }

    attributes_schema = {
        'value': _('The random string generated by this resource. This value '
                   'is also available by referencing the resource.'),
    }

    _sequences = {
        'lettersdigits': string.ascii_letters + string.digits,
        'letters': string.ascii_letters,
        'lowercase': string.ascii_lowercase,
        'uppercase': string.ascii_uppercase,
        'digits': string.digits,
        'hexdigits': string.digits + 'ABCDEF',
        'octdigits': string.octdigits
    }

    @staticmethod
    def _generate_random_string(sequence, length):
        rand = random.SystemRandom()
        return ''.join(rand.choice(sequence) for x in xrange(length))

    def handle_create(self):
        length = self.properties.get(self.LENGTH)
        sequence = self._sequences[self.properties.get(self.SEQUENCE)]
        random_string = self._generate_random_string(sequence, length)
        self.data_set('value', random_string, redact=True)
        self.resource_id_set(random_string)

    def _resolve_attribute(self, name):
        if name == 'value':
            return self.data().get('value')


def resource_mapping():
    return {
        'OS::Heat::RandomString': RandomString,
    }
