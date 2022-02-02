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
        'marge:pw' => array(
            'uid' => array('3'),
            'emailaddress' => 'marge@home.com',
            'givenname' => 'Margerie',
            'surname' => 'Smith',
        ),
        'joe:pw' => array(
            'uid' => array('4'),
            'emailaddress' => 'joe@home.com',
            'givenname' => 'Joseph',
            'surname' => 'Jones',
        ),
        'grace:pw' => array(
            'uid' => array('5'),
            'emailaddress' => 'grace@home.com',
            'givenname' => 'Grace',
            'surname' => 'Kelly',
        ),
    ),

);
