from distutils.core import setup
setup(
        name = 'pytc',
        version = '0.3.1',
        py_modules = ['pytc'],
        description = 'Command line Twitter client',
        author = 'Bryan Kam',
        author_email = 'pytc@vo.racio.us',
        url = 'http://twitter.com/pythontc',
        keywords = ['twitter'],
        scripts = ['pytc'],
        classifiers = [
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.6'
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Natural Language :: English',
            'Operating System :: POSIX :: Linux',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content'
            ]
)
