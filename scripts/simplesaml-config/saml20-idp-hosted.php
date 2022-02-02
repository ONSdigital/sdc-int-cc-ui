<?php

$metadata['__DYNAMIC:1__'] = array(
        'host' => '__DEFAULT__',
        'privatekey' => 'server.pem',
        'certificate' => 'server.crt',
        'auth' => 'example-userpass',
        'NameIDFormat' => 'urn:oasis:names:tc:SAML:2.0:nameid-format:persistent',

        'authproc' => array(
                3 => array(
                    'class' => 'saml:AttributeNameID',
                    'attribute' => 'emailaddress',
                    'Format' => 'urn:oasis:names:tc:SAML:2.0:nameid-format:persistent',
                ),
        ),
);
