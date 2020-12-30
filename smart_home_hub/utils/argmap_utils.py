from marshmallow import fields

# NOTE: Do not include fields.Number or fields.Double to preserve the
# 1-1 mapping. If these fields are used, a KeyError will be thrown
FIELD_TO_STR_MAP = {
    fields.Str: 'string',
    fields.Int: 'integer',
    fields.Float: 'float',
    fields.Bool: 'boolean',
    fields.DateTime: 'datetime',

    fields.List: 'list',
    fields.Dict: 'object'
}
STR_TO_FIELD_MAP = {
    v: k
    for k, v in FIELD_TO_STR_MAP.items()
}
