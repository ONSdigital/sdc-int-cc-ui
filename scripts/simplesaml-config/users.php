<?php

$config = array(

    'admin' => array(
        'core:AdminPassword',
    ),

    'example-userpass' => array(
        'exampleauth:UserPass',
        'fred:pw' => array(
            'uid' => array('1'),
            'emailaddress' => 'fred@home.com',
            'givenname' => 'Fred',
            'surname' => 'Bloggs',
        ),
        'jane:pw' => array(
            'uid' => array('2'),
            'emailaddress' => 'jane@home.com',
            'givenname' => 'Jane',
            'surname' => 'Doe',
        ),
        'sel:pw' => array(
            'uid' => array('2'),
            'emailaddress' => 'sel@ons.gov.uk',
            'givenname' => 'Survey Enquiry Line',
            'surname' => 'Operator',
        ),
        'top:pw' => array(
            'uid' => array('2'),
            'emailaddress' => 'top@ons.gov.uk',
            'givenname' => 'Telephone',
            'surname' => 'Operator',
        ),
        'mgr:pw' => array(
            'uid' => array('2'),
            'emailaddress' => 'mgr@ons.gov.uk',
            'givenname' => 'The',
            'surname' => 'Manager',
        ),
        'phil:pw' => array(
            'uid' => array('2'),
            'emailaddress' => 'philip.whiles@ext.ons.gov.uk',
            'givenname' => 'Philip',
            'surname' => 'Whiles',
        ),
        'pete:pw' => array(
            'uid' => array('2'),
            'emailaddress' => 'peter.bochel@ext.ons.gov.uk',
            'givenname' => 'Peter',
            'surname' => 'Bochel',
        ),
        'rob:pw' => array(
            'uid' => array('2'),
            'emailaddress' => 'robert.catling@ext.ons.gov.uk',
            'givenname' => 'Robert',
            'surname' => 'Catling',
        ),
        'simon:pw' => array(
            'uid' => array('2'),
            'emailaddress' => 'simon.diaz@ext.ons.gov.uk',
            'givenname' => 'Simon',
            'surname' => 'Diaz',
        ),
        'kieran:pw' => array(
            'uid' => array('2'),
            'emailaddress' => 'kieran.wardle@ext.ons.gov.uk',
            'givenname' => 'Kieran',
            'surname' => 'Wardle',
        ),
    ),
);
