========
Storelet
========

Storelet is a simple and easy to use framework for writing backup scripts in Python.

It currently supports the following:

* Compression to a zip file
* Inclusion of any number of directories
* Creation of new directories and files
* Uploading to Amazon S3

Right now, that's all it does as it's all I've needed. I expect to add more as time goes on, but if something is missing or feels wrong, feel free to submit a pull request.

I wrote this because Python is great at - amongst many things - writing small scripts like backup scripts and I think it's just as good as any custom tools or utilities you might find. Storelet just wraps up all the common boilerplate into a tiny little framework to write neat and easy to understand scripts.

Requirements
------------

Right now, storelet has only been tested on Python 2.7 and will not work on older versions. Python 3.x support is to be added. It also assumes the presence of the `zlib` library.

Install
-------

::

    $ pip install storelet
    

Getting Started
---------------

Your backup scripts will be simple Python files. Simply import ``storelet`` and use as follows:

::

    import storelet

    with storelet.ZipBackup("example") as backup:
        backup.include_directory("/home/mark/some/directory")
        backup.include_directory("/some/other/directory")
        
        backup.save_to_s3("my-bucket", "<access_key_goes_here>", "<secret_key_goes_here>")

That's it. All the files in the given directories will be included in a zip file, which will then be uploaded to your S3 bucket and named ``example_20130421163000.zip`` (where the final string of characters is the current date and time in ``YYYYMMDDhhmmss`` form).

In the above example, all the files and directories found in the two directories will be found in the root of the zip file. You may wish to change this in a couple of ways, as outlined below.

Changing include_directory behaviour
------------------------------------

Preserve the entire directory heirarchy in your zip file using the ``preserve_paths`` argument:

::

    backup.include_directory("/home/mark/some/directory", preserve_paths=True)
    
Put all the files/directories inside a new directory in the zip file:

::

    backup.include_directory("/home/mark/some/directory", name="my_special_directory")

Both arguments can be provided, in which case the entire heirarchy would be kept but nested inside the newly created directory. In addition, it is fine to use the same value for the ``name`` argument more than once. This will result in both directories' contents existing within a directory by that name.

Creating new directories
------------------------

Sometimes it's desirable to run additional commands (such as database backups for example) as part of a backup, and place these in a newly created directory. Storelet allows this using the following method:

::

    from subprocess import call
    import storelet
    
    with storelet.ZipBackup("example") as backup:
        with backup.include_new_dir("generated_directory") as d:
            call(["touch", "%s/touched.file" % d])
            # any commands or python code can generate files here

In this basic example, a new directory will exist inside the final zip file called ``generated_directory``, and inside will be an empty file called ``touched.file`` that was created by calling the system's ``touch`` command.

When ``with backup.include_new_dir("whatever") as d:`` is called, a new temporary directory is created. The string representation of the resulting variable (``d``), or ``d.path`` contains the location on disk (``e.g. /tmp/whatever``). Commands (or any code you like) can be run which place files into this directory. At the end of the ``with`` block, the contents of that directory are then included in the generated zip file, in a directory with your given name.
    
Saving the Backup
-----------------

Right now, the only backup process is uploading to Amazon S3:

::
    
    backup.save_to_s3("my-bucket", "<access_key_goes_here>", "<secret_key_goes_here>")

In the future, it is my intention to add more methods of preserving the backups. Right now, this fulfils my requirements.

Backup Types
------------

Right now, the only type of backup is a zip file, using ``ZipBackup``. In the future, I may add others such as tar files and so on. If you really don't want a zip file, storelet may not be right for you at the moment.

Logging
-------

Storelet uses the standard `Python logging`_ mechanism, and also offers a convenience method for setting up some reasonable logging defaults.

::
    
    import storelet

    storelet.setup_logging()

    # Backup stuff here

This will set up the logger to show all messages from INFO level upwards, and formats the output (which is sent to the standard output) to look like the following:

::

    ...
    2014-01-11 14:12:11,501 [INFO]: Added file /path/to/file1
    2014-01-11 14:12:11,501 [INFO]: Added file /path/to/file2
    2014-01-11 14:12:11,501 [INFO]: Added file /path/to/file3
    2014-01-11 14:12:11,502 [INFO]: Added file /path/to/file4
    2014-01-11 14:12:11,503 [INFO]: Added file /path/to/subdirectory/file1
    2014-01-11 14:12:11,503 [INFO]: Added file /path/to/subdirectory/file2
    ...

Any keyword arguments given to this method will be passed on to the logging configuration. Where you provide one which clashes with the default (e.g. if you provide a ``format`` argument), yours will take precedence.

::

    # Use your own format instead of the default
    storelet.setup_logging(format="At %(asctime)s, this happened: %(message)s")

    # Log to a file instead of the standard output
    storelet.setup_logging(filename="mybackups.log")

Of course, using this method is entirely optional. You may wish to set up logging a different way using any of the standard `Python logging`_ tools.

::

    import storelet
    import logging

    logging.basicConfig(level=logging.INFO, 
                        format="At %(asctime)s, this happened: %(message)s")

    # Backup stuff here

Most of the normal status messages which are logged are done so at ``INFO`` level. You may wish to get verbose log output by specifying ``DEBUG`` level.

::

    import storelet
    import logging

    storelet.setup_logging(level=logging.DEBUG)

You can also get access to the defaults used in storelet's ``setup_logging`` method:

::

    storelet.LOGGING_DEFAULTS
    # returns a dict: {'format': '%(asctime)s [%(levelname)s]: %(message)s', 'level': logging.INFO}

Warning
-------

This is a very early release and the API is likely to change. Do not consider it stable until it hits 1.0. Don't complain if it eats your face.


.. _Python Logging: http://docs.python.org/2/howto/logging.html

